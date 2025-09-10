import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import PyPDF2
import docx
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class RAGSystem:
    def __init__(self, db_path='instance/legal_db.db'):
        self.db_path = db_path
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self._init_vector_db()
    
    def _init_vector_db(self):
        """Inicializa la base de datos vectorial"""
        try:
            # Dimensiones del embedding (384 para all-MiniLM-L6-v2)
            self.index = faiss.IndexFlatL2(384)
            self._load_documents()
        except Exception as e:
            logging.error(f"Error inicializando vector DB: {e}")
            self.index = None
    
    def _load_documents(self):
        """Carga documentos desde la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                SELECT id, title, content, embedding, user_id, doc_type, source 
                FROM rag_documents 
                WHERE is_active = 1
            ''')
            
            documents = []
            embeddings = []
            
            for row in c.fetchall():
                doc_id, title, content, embedding_blob, user_id, doc_type, source = row
                
                # Convertir blob a numpy array
                if embedding_blob:
                    embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    embeddings.append(embedding)
                
                documents.append({
                    'id': doc_id,
                    'title': title,
                    'content': content,
                    'user_id': user_id,
                    'type': doc_type,
                    'source': source
                })
            
            if embeddings:
                embeddings_matrix = np.vstack(embeddings)
                self.index.reset()
                self.index.add(embeddings_matrix)
            
            self.documents = documents
            conn.close()
            
        except Exception as e:
            logging.error(f"Error cargando documentos: {e}")
    
    def add_document(self, file, user_id: int, doc_type: str = 'general') -> Dict:
        """Añade un documento al sistema RAG"""
        try:
            # Extraer texto según el tipo de archivo
            text = self._extract_text(file)
            if not text:
                return {'success': False, 'error': 'No se pudo extraer texto'}
            
            # Generar embedding
            embedding = self.model.encode(text)
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO rag_documents 
                (title, content, embedding, user_id, doc_type, source, uploaded_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                file.filename,
                text[:100000],  # Limitar tamaño
                embedding.tobytes(),
                user_id,
                doc_type,
                'upload',
                datetime.now().isoformat()
            ))
            
            doc_id = c.lastrowid
            conn.commit()
            conn.close()
            
            # Actualizar índice en memoria
            if self.index is not None:
                self.index.add(embedding.reshape(1, -1))
                self.documents.append({
                    'id': doc_id,
                    'title': file.filename,
                    'content': text,
                    'user_id': user_id,
                    'type': doc_type,
                    'source': 'upload'
                })
            
            return {'success': True, 'id': doc_id, 'title': file.filename}
            
        except Exception as e:
            logging.error(f"Error añadiendo documento: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_text(self, file) -> str:
        """Extrae texto de diferentes tipos de archivos"""
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.pdf'):
                return self._extract_pdf_text(file)
            elif filename.endswith('.docx'):
                return self._extract_docx_text(file)
            elif filename.endswith('.txt'):
                return file.read().decode('utf-8')
            else:
                # Intentar como texto plano
                try:
                    return file.read().decode('utf-8')
                except:
                    return ""
        except Exception as e:
            logging.error(f"Error extrayendo texto: {e}")
            return ""
    
    def _extract_pdf_text(self, file) -> str:
        """Extrae texto de PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extrayendo PDF: {e}")
            return ""
    
    def _extract_docx_text(self, file) -> str:
        """Extrae texto de DOCX"""
        try:
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extrayendo DOCX: {e}")
            return ""
    
    def query(self, query_text: str, user_id: int, limit: int = 3) -> List[Dict]:
        """Busca documentos relevantes para la consulta"""
        if self.index is None or not self.documents:
            return []
        
        try:
            # Generar embedding para la consulta
            query_embedding = self.model.encode(query_text).reshape(1, -1)
            
            # Buscar documentos similares
            distances, indices = self.index.search(query_embedding, limit * 2)
            
            # Filtrar por usuario y preparar resultados
            results = []
            seen_ids = set()
            
            for idx in indices[0]:
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    
                    # Filtrar por usuario y evitar duplicados
                    if (doc['user_id'] == user_id and 
                        doc['id'] not in seen_ids and 
                        len(results) < limit):
                        
                        results.append({
                            'id': doc['id'],
                            'title': doc['title'],
                            'content': doc['content'][:1000] + '...' if len(doc['content']) > 1000 else doc['content'],
                            'type': doc['type'],
                            'source': doc['source'],
                            'relevance': float(1 - distances[0][idx])  # Convertir distancia a similitud
                        })
                        seen_ids.add(doc['id'])
            
            return results
            
        except Exception as e:
            logging.error(f"Error en query RAG: {e}")
            return []
    
    def delete_document(self, doc_id: int, user_id: int) -> bool:
        """Elimina un documento del sistema RAG"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute(
                'UPDATE rag_documents SET is_active = 0 WHERE id = ? AND user_id = ?',
                (doc_id, user_id)
            )
            
            conn.commit()
            conn.close()
            
            # Actualizar en memoria
            self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
            
            # Reconstruir índice (simplificado - en producción sería más eficiente)
            self._load_documents()
            
            return True
            
        except Exception as e:
            logging.error(f"Error eliminando documento: {e}")
            return False
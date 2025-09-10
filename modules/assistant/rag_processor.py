import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import re
import unicodedata

# ---- CONFIGURACIÓN ----
STORE_PATH = 'instance/vector_store'
EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
VECTOR_DIMENSION = 768

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[\n\t]+', ' ', text)
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s.,;:]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class RAGProcessor:
    def __init__(self):
        os.makedirs(STORE_PATH, exist_ok=True)
        print("-> [RAG __init__] Cargando modelo de embeddings... (Esto puede tardar la primera vez)")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print("-> [RAG __init__] Modelo cargado exitosamente.")
        
        self.index_path = os.path.join(STORE_PATH, 'documents.index')
        self.metadata_path = os.path.join(STORE_PATH, 'documents_meta.txt')
        
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = f.read().splitlines()
                print(f"-> [RAG __init__] Índice vectorial existente con {self.index.ntotal} artículos cargado.")
            except Exception as e:
                print(f"-> [RAG __init__] ERROR: No se pudo cargar el índice existente. Se creará uno nuevo. Error: {e}")
                self._initialize_empty_index()
        else:
            print("-> [RAG __init__] No se encontró un índice existente.")
            self._initialize_empty_index()

    def _initialize_empty_index(self):
        self.index = faiss.IndexFlatL2(VECTOR_DIMENSION) 
        self.metadata = []
        print("-> [RAG _initialize] Se ha inicializado un nuevo índice vectorial vacío.")

    def _extract_articles_from_pdf(self, pdf_path):
        print(f"-> [RAG extract] Extrayendo artículos del PDF: {os.path.basename(pdf_path)}")
        doc = fitz.open(pdf_path)
        articles = {}
        current_article_text = ""
        current_article_num = None
        article_pattern = re.compile(r'^ARTICULO (\d+)\.?>?(.*)')

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            for line in text.split('\n'):
                line = line.strip()
                match = article_pattern.match(line)
                if match:
                    if current_article_num is not None:
                        articles[current_article_num] = f"Artículo {current_article_num}: {current_article_text.strip()}"
                    current_article_num = match.group(1)
                    current_article_text = match.group(2).strip()
                elif current_article_num is not None:
                    if not line.startswith("CODIGO CIVIL COLOMBIANO") and not line.startswith("Página"):
                        current_article_text += " " + line
        if current_article_num is not None and current_article_num not in articles:
            articles[current_article_num] = f"Artículo {current_article_num}: {current_article_text.strip()}"

        print(f"-> [RAG extract] Se extrajeron {len(articles)} artículos del documento.")
        return list(articles.values())

    def process_document(self, file_path, original_filename):
        print(f"-> [RAG process] Procesando el documento: {original_filename}")
        
        chunks = self._extract_articles_from_pdf(file_path)
        if not chunks:
            print("-> [RAG process] ADVERTENCIA: No se encontraron artículos en el documento. Proceso abortado.")
            return

        normalized_chunks = [normalize_text(chunk) for chunk in chunks]
        
        print(f"-> [RAG process] Creando embeddings para {len(normalized_chunks)} artículos...")
        embeddings = self.model.encode(
            normalized_chunks, 
            batch_size=32,
            show_progress_bar=True,
            convert_to_tensor=False
        )
        
        self.index.add(np.array(embeddings).astype('float32'))
        for chunk in chunks:
            clean_chunk = re.sub(r'\s+', ' ', chunk).strip()
            self.metadata.append(f"Fuente: {original_filename}::{clean_chunk}")
        
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.metadata))
        print(f"-> [RAG process] Documento '{original_filename}' procesado. Total de artículos en memoria: {self.index.ntotal}")

    def get_relevant_context(self, query, top_k=3):
        print(f"\n-> [RAG get_context] Buscando contexto para la pregunta: '{query}'")
        if self.index.ntotal == 0:
            print("-> [RAG get_context] ERROR CRÍTICO: El índice de vectores está vacío. Imposible buscar.")
            return ""
        
        print(f"-> [RAG get_context] Tamaño del índice: {self.index.ntotal} vectores.")
        normalized_query = normalize_text(query)
        query_embedding = self.model.encode([normalized_query])
        
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        print(f"-> [RAG get_context] Resultados de la búsqueda (índices): {indices}")
        print(f"-> [RAG get_context] Resultados de la búsqueda (distancias): {distances}")

        context = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                context.append(self.metadata[idx])

        if not context:
            print("-> [RAG get_context] ADVERTENCIA: La búsqueda no arrojó ningún resultado relevante.")
        
        return "\n\n---\n\n".join(context)
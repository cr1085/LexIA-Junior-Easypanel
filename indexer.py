import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- Configuración de Rutas ---
PDFS_PATH = "biblioteca_pdfs/"
INDEX_PATH = "faiss_index_maestra"

def create_master_index():
    """
    Procesa todos los PDFs en la carpeta 'biblioteca_pdfs' y crea un 
    índice vectorial FAISS persistente.
    """
    print("Iniciando la indexación de la Biblioteca Jurídica Maestra...")
    
    # Lista para almacenar el texto extraído y los metadatos de origen
    docs_with_metadata = []
    
    pdf_files = [f for f in os.listdir(PDFS_PATH) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"Error: No se encontraron archivos PDF en la carpeta '{PDFS_PATH}'.")
        return

    print(f"Se encontraron {len(pdf_files)} archivos PDF para procesar.")

    # 1. Extracción de texto de cada PDF
    for pdf_file in pdf_files:
        file_path = os.path.join(PDFS_PATH, pdf_file)
        print(f"-> Procesando: {pdf_file}")
        try:
            with fitz.open(file_path) as doc:
                full_text = ""
                for page_num, page in enumerate(doc, start=1):
                    full_text += page.get_text()
                
                # Guardamos el texto completo con el nombre del archivo como metadato
                docs_with_metadata.append(
                    {"text": full_text, "source": pdf_file}
                )
        except Exception as e:
            print(f"  Error al leer el archivo {pdf_file}: {e}")
            continue
    
    if not docs_with_metadata:
        print("Error: No se pudo extraer texto de ningún PDF.")
        return

    # 2. División del texto en fragmentos (chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )
    
    all_chunks = []
    for doc in docs_with_metadata:
        chunks = text_splitter.split_text(doc["text"])
        # Añadimos el metadato de origen a cada chunk
        for chunk in chunks:
            all_chunks.append({"page_content": chunk, "metadata": {"source": doc["source"]}})

    # Convertimos al formato que LangChain espera (Document objects)
    from langchain.schema.document import Document
    documents_for_langchain = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in all_chunks]

    print(f"Se crearon {len(documents_for_langchain)} chunks de texto en total.")
    print("Generando embeddings... (Esto puede tardar varios minutos)")

    # 3. Creación de embeddings y almacenamiento en FAISS
    start_time = time.time()
    # Usamos un modelo de embedding eficiente y open-source
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vector_store = FAISS.from_documents(documents_for_langchain, embedding=embeddings)
    
    if not os.path.exists(INDEX_PATH):
        os.makedirs(INDEX_PATH)
        
    vector_store.save_local(INDEX_PATH)
    
    end_time = time.time()
    print(f"\n¡Indexación completada!")
    print(f"El índice se guardó correctamente en la carpeta '{INDEX_PATH}'.")
    print(f"Tiempo total del proceso: {end_time - start_time:.2f} segundos.")

if __name__ == "__main__":
    create_master_index()
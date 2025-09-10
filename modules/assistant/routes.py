# from flask import Blueprint, request, jsonify, current_app # <-- 1. IMPORTAR current_app
# from flask_login import login_required
# from .core import AIAssistant
# # Quitamos la importación directa de RAGProcessor

# assistant_bp = Blueprint('assistant', __name__)
# ai_assistant = AIAssistant()
# # rag_processor = RAGProcessor() # <-- 2. BORRAR ESTA LÍNEA

# def get_db_connection():
#     db_path = Config.DATABASE_PATH
#     conn = sqlite3.connect(db_path)
#     conn.row_factory = sqlite3.Row
#     return conn

# @assistant_bp.route('/ask', methods=['POST'])
# @login_required
# def ask():
#     data = request.get_json()
#     question = data.get('question')

#     if not question:
#         return jsonify({'error': 'No se proporcionó ninguna pregunta.'}), 400

#     # 3. USAR EL PROCESADOR COMPARTIDO DESDE 'current_app'
#     context = current_app.rag_processor.get_relevant_context(question)
    
#     print(f"DEBUG: Contexto encontrado para la pregunta:\n---\n{context}\n---")
    
#     if context:
#         prompt = f"Basándote únicamente en el contexto: {context}, responde: {question}"        
#     else:
#         prompt = question

#     response_text = ai_assistant.get_response(prompt)
    
#     return jsonify({'response': response_text})

# ==================================================================

# from flask import Blueprint, request, jsonify, current_app
# from flask_login import login_required, current_user
# import sqlite3
# from config import Config
# from datetime import datetime

# assistant_bp = Blueprint('assistant', __name__)

# # Necesitamos acceso a la clase del asistente para crear una instancia
# from .core import AIAssistant
# ai_assistant = AIAssistant()

# def get_db_connection():
#     conn = sqlite3.connect(Config.DATABASE_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# @assistant_bp.route('/ask', methods=['POST'])
# @login_required
# def ask():
#     data = request.get_json()
#     question = data.get('question')

#     if not question:
#         return jsonify({'error': 'No se proporcionó ninguna pregunta.'}), 400

#     # --- INICIO DE LA LÓGICA INTELIGENTE ---
#     # 1. Buscamos contexto en los documentos, como siempre.
#     context = current_app.rag_processor.get_relevant_context(question)
    
#     print(f"DEBUG: Contexto encontrado para la pregunta:\n---\n{context}\n---")
    
#     if context:
#         # 2. Si encontramos contexto, creamos el prompt estricto de RAG.
#         prompt = f"""
#         Basándote únicamente en el siguiente contexto extraído de documentos legales, responde la pregunta del usuario.
#         Si la respuesta no está en el contexto, di "La información no se encuentra en los documentos que he procesado."

#         ---
#         Contexto:
#         {context}
#         ---

#         Pregunta del usuario: {question}
#         """
#     else:
#         # 3. Si NO hay contexto, es una pregunta general. Creamos un prompt conversacional.
#         prompt = f"Eres un asistente amigable y profesional. Responde la siguiente pregunta de forma concisa: {question}"
    
#     # 4. Le pasamos el prompt adecuado al motor de IA.
#     response_text = ai_assistant.get_response(prompt)
#     # --- FIN DE LA LÓGICA INTELIGENTE ---
    
#     # Guardamos la consulta en el log
#     try:
#         conn = get_db_connection()
#         conn.execute('INSERT INTO query_log (user_id, question) VALUES (?, ?)', (current_user.id, question))
#         conn.commit()
#         conn.close()
#     except Exception as e:
#         print(f"Error al registrar la consulta: {e}")

#     return jsonify({'response': response_text})

# ==================================================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import os
import sqlite3
from config import Config

# --- INICIO: NUEVAS IMPORTACIONES PARA EL RAG PERSISTENTE ---
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
# --- FIN: NUEVAS IMPORTACIONES ---

assistant_bp = Blueprint('assistant', __name__)

# --- INICIO: CARGA DEL ÍNDICE Y MODELOS (SE EJECUTA UNA SOLA VEZ) ---
INDEX_PATH = "faiss_index_maestra"
vector_store = None

try:
    # Cargamos el modelo de embeddings que usó el indexador
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    if os.path.exists(INDEX_PATH):
        # Cargamos la base de conocimiento persistente desde el disco
        vector_store = FAISS.load_local(
            INDEX_PATH, 
            embedding_model, 
            allow_dangerous_deserialization=True
        )
        print(f"-> Base de Conocimiento Maestra ('{INDEX_PATH}') cargada exitosamente.")
    else:
        print(f"-> ADVERTENCIA: No se encontró la Base de Conocimiento en '{INDEX_PATH}'. El asistente solo responderá de forma general.")
except Exception as e:
    print(f"-> ERROR CRÍTICO al cargar la Base de Conocimiento: {e}")

# Plantilla del prompt para instruir a la IA a ser un abogado experto
prompt_template = """
Eres LexIA, un Asistente Jurídico Junior. Tu tono es profesional pero también amable y didáctico. Tu objetivo es ayudar al usuario a entender el contenido de la Información Jurídica.

Analiza la pregunta del usuario. Luego, revisa el siguiente contexto que se te ha proporcionado.

**Usa la información del contexto para construir una respuesta conversacional y clara.** No te limites a copiar y pegar. Explica el concepto legal en tus propias palabras, pero asegúrate de que cada afirmación que hagas esté directamente respaldada por el texto del contexto.

Si el contexto no contiene la información necesaria para responder, indica amablemente: "He revisado mis Validaciones Jurídicas, pero no he encontrado información específica sobre tu pregunta."

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA AMABLE Y PROFESIONAL:
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
# --- FIN: CARGA DEL ÍNDICE Y MODELOS ---

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@assistant_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No se proporcionó ninguna pregunta.'}), 400

    # Si el índice no se cargó, devolvemos un error claro
    if not vector_store:
        return jsonify({'answer': 'Error: La Base de Conocimiento Maestra no está disponible. Por favor, ejecute el indexador y reinicie el servidor.', 'sources': []}), 500

    # 1. Seleccionar el modelo de IA (Ollama o Google) desde config.py
    try:
        if Config.AI_PROVIDER == 'google':
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=Config.GOOGLE_API_KEY, temperature=0.1)
        else:
            llm = Ollama(model="phi3:mini", temperature=0.1)
    except Exception as e:
        return jsonify({'answer': f"Error al inicializar el modelo de IA: {e}", 'sources': []}), 500

    # 2. Configurar y ejecutar la cadena de RAG con la biblioteca persistente
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}), # Busca 4 fragmentos relevantes
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    try:
        result = qa_chain.invoke({"query": question})
    except Exception as e:
        print(f"ERROR al ejecutar la cadena RAG: {e}")
        return jsonify({'answer': "Ocurrió un error al procesar la respuesta de la IA.", 'sources': []}), 500

    # 3. Formatear las fuentes para enviarlas al frontend
    sources = []
    if result.get('source_documents'):
        seen_sources = set()
        for doc in result['source_documents']:
            source_name = doc.metadata.get('source', 'Fuente desconocida')
            if source_name not in seen_sources:
                sources.append(source_name)
                seen_sources.add(source_name)
    
    # Guardamos la consulta en el log
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO query_log (user_id, question) VALUES (?, ?)', (current_user.id, question))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al registrar la consulta en el log: {e}")

    # 4. Devolvemos una respuesta JSON estructurada
    return jsonify({
        'answer': result.get('result', 'No se pudo generar una respuesta.'),
        'sources': sources
    })
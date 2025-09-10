# import os
# from dotenv import load_dotenv

# # Forzamos la carga del archivo .env que está en la misma carpeta que este config.py
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Ajustamos la ruta para que encuentre el .env en la raíz
# if os.path.exists(dotenv_path):
#     print(f"-> Cargando configuración desde: {dotenv_path}")
#     load_dotenv(dotenv_path=dotenv_path)
# else:
#     # Si no lo encuentra, busca en la carpeta actual (útil para la estructura de módulos)
#     dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
#     if os.path.exists(dotenv_path):
#         print(f"-> Cargando configuración desde: {dotenv_path}")
#         load_dotenv(dotenv_path=dotenv_path)
#     else:
#          print("-> ADVERTENCIA: No se encontró el archivo .env. Usando variables de entorno del sistema.")


# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY')
#     DATABASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'legal_db.db') # Ruta corregida
    
#     GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
#     OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
#     HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
#     GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
#     AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama')

# # Verificación final que se imprime en la terminal al iniciar
# print("-" * 30)
# print(f"-> MODO DE IA CONFIGURADO: '{Config.AI_PROVIDER}'")
# print("-" * 30)


import os
from dotenv import load_dotenv

# La raíz del proyecto es el directorio donde se encuentra este archivo.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # La base de datos estará en la carpeta 'instance' DENTRO de la raíz del proyecto.
    # Esta es la ruta correcta y robusta.
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'legal_db.db')
    
    # Claves API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # El interruptor principal para la IA
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama')

# Verificación que se imprime en la terminal al iniciar
print("-" * 30)
print(f"-> RUTA DE LA BASE DE DATOS: '{Config.DATABASE_PATH}'")
print(f"-> MODO DE IA CONFIGURADO: '{Config.AI_PROVIDER}'")
print("-" * 30)
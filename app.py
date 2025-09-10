# Importante: Cargar la configuración de .env PRIMERO que todo.
import os
from dotenv import load_dotenv

# Nos aseguramos de que encuentre el archivo .env en la raíz del proyecto
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Importamos la función que crea nuestra aplicación desde el __init__.py de modules
from modules import create_app

# Creamos la instancia de la aplicación. La función create_app() se encarga
# de registrar todos los blueprints como 'assistant_bp', 'auth_bp', etc.
app = create_app()

# Este bloque solo se ejecuta si corres el script directamente con 'python app.py'
if __name__ == '__main__':
    app.run(debug=True)
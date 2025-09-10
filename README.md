# LexIA Junior: Asistente Jurídico Inteligente con RAG

**LexIA Junior** es una aplicación web avanzada que funciona como un asistente legal especializado. Utilizando una arquitectura de Generación Aumentada por Recuperación (RAG) sobre una base de conocimiento personalizable, LexIA puede analizar múltiples documentos legales y responder preguntas complejas con respuestas naturales, conversacionales y basadas en fuentes verificables.

Este proyecto demuestra la implementación de un sistema de IA robusto, con una personalidad definida y una interfaz de usuario amigable, ideal para asistir a profesionales del derecho en sus tareas de investigación y consulta.

---

### ⭐ Características Avanzadas

* **Base de Conocimiento Multi-Documento:** Capacidad para indexar y consultar simultáneamente varios archivos PDF (leyes, códigos, manuales, contratos), creando un "cerebro" legal unificado.
* **IA Conversacional con Personalidad:** Gracias a un sistema de prompts refinado, LexIA no solo extrae datos, sino que responde de manera amable y didáctica, simulando la interacción con un verdadero asistente junior.
* **Búsqueda Semántica de Alta Precisión:** Utiliza un `retriever` de compresión contextual para filtrar y entregar solo los fragmentos más relevantes al modelo de IA, mejorando drásticamente la precisión de las respuestas.
* **Citación de Fuentes para Verificabilidad:** Cada respuesta generada está respaldada por una lista de los documentos fuente consultados, garantizando la transparencia y la confianza en la información.
* **Motor de IA Configurable:** Permite cambiar fácilmente entre un modelo local (privacidad total con **Ollama**) y un modelo en la nube (**Google Gemini API**) a través de una simple variable de entorno.
* **Interfaz Temática y Profesional:** Incluye un sistema de autenticación, panel de bienvenida personalizado y un diseño de chat con avatares para una experiencia de usuario agradable.

---

### 🚀 Demostración de Capacidades

LexIA Junior puede responder a una amplia gama de preguntas, desde su propio rol hasta detalles específicos del Código Civil o la Constitución. Algunos ejemplos:

* `Desde tu perspectiva como asistente, ¿cuáles son las habilidades blandas más importantes que debe tener un abogado junior?`
* `¿Qué es el derecho de petición según la Constitución y quiénes pueden ejercerlo?`
* `Si una persona encuentra un tesoro en un terreno que no es suyo, ¿a quién le pertenece según el Código Civil?`

---

### ⚙️ Stack Tecnológico y Puesta en Marcha

* **Backend:** Python, Flask
* **Motor de IA:** Ollama (local) / Google Gemini (nube)
* **Sistema RAG:** LangChain, FAISS, Sentence-Transformers
* **Base de Datos (Usuarios):** SQLite
* **Frontend:** HTML, CSS, JavaScript

### Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en un entorno local.

#### 1. Prerrequisitos
* Python 3.10+
* (Opcional, para modo local) [Ollama](https://ollama.com/) instalado y ejecutándose.

#### 2. Clonar el Repositorio
```bash
git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
cd tu-repositorio
```

#### 3. Entorno Virtual y Dependencias
```bash
# Crear y activar entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto y añade las siguientes variables:

```
# Clave secreta para la seguridad de Flask
SECRET_KEY="una-clave-muy-secreta-y-dificil-de-adivinar"

# Elige el motor de IA. Opciones: "ollama" o "google"
AI_PROVIDER="google"

# Pega tu clave de API si vas a usar el modo 'google'
GOOGLE_API_KEY="AIzaSy...tu_clave_de_google_aqui"
```

#### 5. Crear la Base de Conocimiento
1.  Coloca todos los documentos PDF que el asistente debe estudiar en la carpeta `/biblioteca_pdfs`.
2.  Ejecuta el script indexador **una sola vez**. Este proceso puede tardar varios minutos.
    ```bash
    python indexer.py
    ```

#### 6. Inicializar la Base de Datos de Usuarios
```bash
flask init-db
```

#### 7. Ejecutar la Aplicación
```bash
flask run
```
La aplicación estará disponible en `http://127.0.0.1:5000`.
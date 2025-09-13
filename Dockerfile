# Usa Python 3.11 con herramientas de compilación
FROM python:3.11-slim

# --- DECLARA TODOS LOS ARGUMENTOS QUE PASA EASY PANEL ---
ARG AI_PROVIDER
ARG GOOGLE_API_KEY
ARG SECRET_KEY
ARG DISCORD_TOKEN
ARG GROQ_API_KEY
ARG OPENROUTER_API_KEY
ARG HUGGINGFACE_API_KEY
ARG DATABASE_URL
ARG GIT_SHA

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    libffi-dev \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero para optimizar caché
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto (usará $PORT definido por EasyPanel)
EXPOSE $PORT

# Crear archivo .env dinámicamente con las variables de build (opcional, pero útil)
RUN echo "AI_PROVIDER=${AI_PROVIDER:-google}" > .env && \
    echo "GOOGLE_API_KEY=${GOOGLE_API_KEY:-}" >> .env && \
    echo "SECRET_KEY=${SECRET_KEY:-secret-key-default}" >> .env && \
    echo "DISCORD_TOKEN=${DISCORD_TOKEN:-}" >> .env && \
    echo "GROQ_API_KEY=${GROQ_API_KEY:-}" >> .env && \
    echo "OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}" >> .env && \
    echo "HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY:-}" >> .env && \
    echo "DATABASE_URL=${DATABASE_URL:-postgresql://localhost}" >> .env && \
    echo "GIT_SHA=${GIT_SHA:-unknown}" >> .env

# Ejecutar la app con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--timeout", "120", "app:app"]
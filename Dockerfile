FROM python:3.11-slim

# --- Declara todas las variables de build que EasyPanel envía ---
ARG AI_PROVIDER
ARG GOOGLE_API_KEY
ARG SECRET_KEY
ARG DISCORD_TOKEN
ARG GROQ_API_KEY
ARG OPENROUTER_API_KEY
ARG HUGGINGFACE_API_KEY
ARG DATABASE_URL
ARG GIT_SHA

# Instalar dependencias del sistema para compilar paquetes pesados
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    libffi-dev \
    libpoppler-cpp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero para cachear mejor
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos del proyecto
COPY . .

# Hacer ejecutable el entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puerto
EXPOSE $PORT

# Usar el entrypoint como comando principal (¡NO necesitas Start Command en EasyPanel!)
ENTRYPOINT ["/entrypoint.sh"]
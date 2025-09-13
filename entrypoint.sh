#!/bin/sh
set -e

echo "🚀 Iniciando despliegue de Lexia Junior..."

# --- 1. Generar .env desde variables de build ---
if [ ! -f .env ]; then
    echo "⚠️  Generando .env desde variables del build..."
    echo "AI_PROVIDER=${AI_PROVIDER:-google}" > .env
    echo "GOOGLE_API_KEY=${GOOGLE_API_KEY:-}" >> .env
    echo "SECRET_KEY=${SECRET_KEY:-secret-key-default}" >> .env
    echo "DISCORD_TOKEN=${DISCORD_TOKEN:-}" >> .env
    echo "GROQ_API_KEY=${GROQ_API_KEY:-}" >> .env
    echo "OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}" >> .env
    echo "HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY:-}" >> .env
    echo "DATABASE_URL=${DATABASE_URL:-sqlite:///${PWD}/instance/legal_db.db}" >> .env
    echo "GIT_SHA=${GIT_SHA:-unknown}" >> .env
fi

# Exportar variables para que Python y Flask las vean
export $(grep -v '^#' .env | xargs)

# --- 2. Crear carpeta 'instance' si no existe ---
mkdir -p instance

# --- 3. Ejecutar indexación (indexer.py) ---
echo "🔍 Ejecutando indexación de PDFs con indexer.py..."
cd /app  # Aseguramos que estamos en el directorio correcto
python indexer.py
echo "✅ Indexación completada."

# --- 4. Inicializar base de datos ---
echo "🗄️  Ejecutando 'flask init-db'..."
cd /app
flask init-db
echo "✅ Base de datos inicializada."

# --- 5. Iniciar Gunicorn ---
echo "🚀 Iniciando servidor Gunicorn en http://0.0.0.0:$PORT..."
cd /app
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
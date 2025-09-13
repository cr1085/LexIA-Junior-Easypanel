#!/bin/sh
set -e

echo "🚀 Iniciando despliegue de Lexia Junior..."

# --- 1. Generar .env desde variables de build (si no existe) ---
if [ ! -f .env ]; then
    echo "⚠️  Generando .env desde variables de entorno del build..."
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

# --- 2. Crear carpeta 'instance' si no existe (necesaria para SQLite) ---
mkdir -p instance

# --- 3. Ejecutar indexación (indexer.py) ---
echo "🔍 Ejecutando indexación de PDFs con indexer.py..."
python indexer.py
echo "✅ Indexación completada."

# --- 4. Inicializar base de datos con flask init-db ---
echo "🗄️  Ejecutando 'flask init-db'..."
flask init-db
echo "✅ Base de datos inicializada."

# --- 5. Iniciar Gunicorn (solo aquí, en producción) ---
echo "🚀 Iniciando servidor Gunicorn en http://0.0.0.0:$PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
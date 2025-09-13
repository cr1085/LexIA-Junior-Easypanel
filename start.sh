#!/bin/bash
echo "🚀 Iniciando Lexia Junior..."

# Si no existe el índice, generarlo
if [ ! -d "faiss_index_maestra" ]; then
    echo "🔍 Generando índice vectorial..."
    python indexer.py
else
    echo "✅ Índice vectorial ya existe."
fi

# Iniciar la app con Gunicorn usando $PORT (¡CRUCIAL!)
echo "🚀 Iniciando servidor Gunicorn en http://0.0.0.0:\$PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
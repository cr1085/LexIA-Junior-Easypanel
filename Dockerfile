FROM python:3.11-slim

# Crear carpeta de la app
WORKDIR /app

# Instalar dependencias del sistema (ej. psycopg2 necesita gcc y libpq)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias primero para aprovechar caché
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 8000

# Ejecutar con gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]

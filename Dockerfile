# Imagen base liviana con Python 3.11
FROM python:3.11-slim

# Crear directorio de la app
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y otras librerías
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias primero (mejora caché en rebuilds)
COPY requirements.txt .

# Instalar dependencias de Python (incluye gunicorn ✅)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto que usará gunicorn
EXPOSE 8000

# Comando por defecto para producción
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]

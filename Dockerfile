# Usa una imagen base oficial de Python 3.11 (evita alpine por problemas de compilación)
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt .
COPY . .

# Instala dependencias con pip (usando --no-cache-dir para reducir tamaño)
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE $PORT

# Ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--timeout", "120", "app:app"]
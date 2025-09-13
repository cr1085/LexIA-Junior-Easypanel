# Usa Python 3.11 con herramientas necesarias
FROM python:3.11-slim

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

# Copiar solo lo necesario para instalar dependencias (optimización de caché)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODOS los archivos restantes del proyecto
COPY . .

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Ejecutar el script de inicio como entrada principal
ENTRYPOINT ["./start.sh"]
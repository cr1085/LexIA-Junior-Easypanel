FROM python:3.11-slim

ARG AI_PROVIDER
ARG GOOGLE_API_KEY
ARG SECRET_KEY
ARG DISCORD_TOKEN
ARG GROQ_API_KEY
ARG OPENROUTER_API_KEY
ARG HUGGINGFACE_API_KEY
ARG DATABASE_URL
ARG GIT_SHA

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    libffi-dev \
    libpoppler-cpp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE $PORT

ENTRYPOINT ["/entrypoint.sh"]
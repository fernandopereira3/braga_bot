FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

VOLUME /app/users

    # Instalar dependências do sistema e Chromium (multi-arch: amd64 e arm64)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium

# Instalar dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos do projeto
COPY . .

# Executar a aplicação
CMD ["python", "braga.py"]
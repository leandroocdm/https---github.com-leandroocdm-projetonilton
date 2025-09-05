FROM python:3.9-slim

# Instale as dependências do WeasyPrint
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libgirepository1.0-dev \
    build-essential \
    libpng-dev

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos de dependência e instale
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copie todos os arquivos do seu projeto para o container
COPY . .

# Comando para iniciar o servidor
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app"]
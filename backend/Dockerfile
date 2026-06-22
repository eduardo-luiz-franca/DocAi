FROM python:3.11-slim

# Dependências de sistema para OCR (Tesseract) e leitura de PDF (Poppler),
# exigidas pelo `unstructured[pdf]` em documentos digitalizados.
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-por \
        poppler-utils \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala as dependências Python primeiro para aproveitar o cache de camadas.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do backend (o pacote é importado como `backend.*`).
COPY backend ./backend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

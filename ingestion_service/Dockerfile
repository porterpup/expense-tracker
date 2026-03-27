FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the ingestion service code
COPY . /app

EXPOSE 8000

# Database path and data volume
ENV INGEST_DB_PATH=/data/expenses.db
VOLUME ["/data"]

CMD ["uvicorn", "ingestion_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

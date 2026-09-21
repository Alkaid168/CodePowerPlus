FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data/knowledge_taxonomy.json data/knowledge_taxonomy.schema.json ./data/
COPY data/taxonomy_versions ./data/taxonomy_versions
COPY scripts ./scripts
COPY data/evaluation ./data/evaluation
COPY README.md .
ENV CODEPOWERPLUS_DB_PATH=/app/storage/codepowerplus.db
RUN mkdir -p storage
VOLUME ["/app/storage"]
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

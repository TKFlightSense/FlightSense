FROM python:3.11-slim
WORKDIR /app
COPY services/classifier /app/services/classifier
COPY packages/tkfs_common /app/packages/tkfs_common
COPY models/artifacts /app/models/artifacts
RUN pip install --no-cache-dir fastapi uvicorn pydantic numpy && \
    pip install --no-cache-dir /app/packages/tkfs_common
ENV PYTHONPATH=/app
CMD ["uvicorn", "services.classifier.tkfs_classifier.server:app", "--host", "0.0.0.0", "--port", "8001"]

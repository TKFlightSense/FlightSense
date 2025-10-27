FROM python:3.11-slim
WORKDIR /app
COPY services/reporting /app/services/reporting
COPY packages/tkfs_common /app/packages/tkfs_common
RUN pip install --no-cache-dir jinja2 pydantic && \
    pip install --no-cache-dir /app/packages/tkfs_common
ENV PYTHONPATH=/app
CMD ["python","-m","services.reporting.tkfs_reporting.worker"]

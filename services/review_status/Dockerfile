# FlightSense Review Status Tracker
# Streamlit-based status tracking UI

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    streamlit \
    mysql-connector-python

# Copy application files
COPY app.py .

# Copy shared assets (logo) - create images folder first
# COPY images/ ./images/

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]

FROM python:3.9-slim

WORKDIR /app

RUN pip install streamlit mysql-connector-python

COPY app.py .
COPY images/ ./images/

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]

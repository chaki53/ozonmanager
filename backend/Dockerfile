FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt &&     apt-get update && apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libffi-dev &&     rm -rf /var/lib/apt/lists/*

COPY app ./app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

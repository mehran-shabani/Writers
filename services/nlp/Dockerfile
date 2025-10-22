FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    build-essential curl wget git \
    libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app /app/app
COPY ../../scripts /app/scripts
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8001"]

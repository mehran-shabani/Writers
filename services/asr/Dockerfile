FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg sox && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY asr_service.py .
EXPOSE 7000
CMD ["uvicorn","asr_service:app","--host","0.0.0.0","--port","7000"]

FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    sox \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY asr_service.py .

# Create non-root user (note: GPU access may require additional group membership)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7000/health || exit 1

CMD ["uvicorn", "asr_service:app", "--host", "0.0.0.0", "--port", "7000"]

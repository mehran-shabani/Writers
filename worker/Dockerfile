FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy worker code and shared backend package
COPY . ./worker
COPY ../backend ./backend

ENV PYTHONPATH="/app/backend"

CMD ["bash", "-c", "cd worker && ./entrypoint.sh"]

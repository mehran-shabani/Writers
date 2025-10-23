FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash=5.2.* \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY worker/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy worker code and shared backend package
COPY --chown=app:app worker ./worker
COPY --chown=app:app backend ./backend

ENV PYTHONPATH="/app/backend"

USER app

CMD ["bash", "-c", "cd worker && ./entrypoint.sh"]

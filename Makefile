.PHONY: up down build logs migrate test init-bucket

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec nlp python -m app -migrate

init-bucket:
	docker compose exec nlp python /app/scripts/init_minio.py

test:
	docker compose exec nlp pytest -q

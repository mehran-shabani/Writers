.PHONY: all up down build logs migrate test init-bucket clean help

all: build up migrate init-bucket

help:
	@echo "Available targets:"
	@echo "  all         - Build, start, migrate, and initialize"
	@echo "  build       - Build Docker images"
	@echo "  up          - Start services"
	@echo "  down        - Stop services"
	@echo "  logs        - Follow service logs"
	@echo "  migrate     - Run database migrations"
	@echo "  init-bucket - Initialize MinIO bucket"
	@echo "  test        - Run tests"
	@echo "  clean       - Stop and remove containers, volumes"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec nlp python /app/scripts/db_migrate.py

init-bucket:
	docker compose exec nlp python /app/scripts/init_minio.py

test:
	docker compose exec nlp pytest -q

clean:
	docker compose down -v
	rm -rf models/ data/

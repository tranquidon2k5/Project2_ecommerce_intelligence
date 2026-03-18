.PHONY: dev build down logs db-migrate db-seed crawl test clean

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

build:
	docker-compose build

down:
	docker-compose down

logs:
	docker-compose logs -f

db-migrate:
	docker-compose exec backend alembic upgrade head

db-seed:
	docker-compose exec backend python /app/scripts/seed_data.py

crawl:
	docker-compose exec crawler scrapy crawl tiki -a category=dien-thoai

test:
	docker-compose exec backend python -m pytest tests/ -v

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

shell-backend:
	docker-compose exec backend bash

shell-db:
	docker-compose exec db psql -U shopsmart shopsmart_db

generate-data:
	docker-compose exec backend python /app/scripts/generate_fake_data.py

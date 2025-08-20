dev:
	docker compose -f docker-compose.yml up --build --remove-orphans

dev-d:
	docker compose -f docker-compose.yml up --build --remove-orphans -d

scrape:
	@docker compose exec app python scripts/scrape_czech.py

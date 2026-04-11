up:
	@docker compose -f docker-compose.local.yaml up -d

down:
	@docker compose -f docker-compose.local.yaml down

shell:
	@docker compose -f docker-compose.local.yaml run --rm django bash

makemigrations:
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py makemigrations

migrate:
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py migrate

createsuperuser:
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py createsuperuser
up:
	@docker compose -f docker-compose.local.yaml up -d --build

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

test:
	@docker compose -f docker-compose.local.yaml run --rm django pytest

generate-client:
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py spectacular --file schema.yaml --validate --fail-on-warn
	@docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -i /local/schema.yaml -g typescript-axios -o /local/typescript-axios-client/
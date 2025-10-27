.PHONY: setup up down logs lint test fmt migrate seed openapi

setup: ## Install pre-commit hooks
\tpre-commit install

up: ## Run local stack
\tdocker compose up -d --build

down: ## Stop stack
\tdocker compose down

logs:
\tdocker compose logs -f --tail=200 api classifier reporting

lint:
\truff . && black --check . && mypy services packages

fmt:
\tblack . && ruff --fix .

test:
\tpytest -q

migrate:
\tdocker compose exec api alembic upgrade head

openapi:
\tcurl -s http://localhost:8000/openapi.json > docs/api/openapi.json

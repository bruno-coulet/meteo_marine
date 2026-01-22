.PHONY: help install run collect consolidate docker-build docker-run docker-clean

help:
	@echo "=== Commandes disponibles ==="
	@echo "Local (avec uv):"
	@echo "  make install          Installe les dépendances"
	@echo "  make run              Exécute requete_ok.py"
	@echo "  make collect          Récupère les données"
	@echo "  make consolidate      Consolide les données"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build l'image Docker"
	@echo "  make docker-run       Lance le conteneur"
	@echo "  make docker-clean     Supprime les conteneurs/images"

# Installation
install:
	uv sync

# Exécution locale
run:
	uv run python main.py

collect:
	uv run python main.py

consolidate:
	uv run python consolidate_data.py

# Docker
docker-build:
	docker build -t meteo-marine:latest .

docker-run:
	docker run --rm -v $(PWD)/data:/app/data meteo-marine:latest

docker-collect:
	docker compose run --rm collect-data

docker-consolidate:
	docker compose run --rm consolidate-data

docker-clean:
	docker compose down
	docker rmi meteo-marine:latest 2>/dev/null || true

# Développement
lint:
	uv run black --check .
	uv run ruff check .

format:
	uv run black .
	uv run ruff check --fix .

test:
	uv run pytest -v

# Nettoyage
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage

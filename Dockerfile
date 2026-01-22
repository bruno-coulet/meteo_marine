# Build stage
FROM python:3.11-slim as builder

# Installer uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copier les fichiers de configuration
COPY pyproject.toml .

# Créer un environnement virtuel et installer les dépendances
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install --upgrade pip && \
    uv pip install -e .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copier l'environnement virtuel du builder
COPY --from=builder /app/.venv /app/.venv

# Copier le code source
COPY . .

# Créer le dossier data pour les résultats
RUN mkdir -p data/raw data/processed

# Activer l'environnement virtuel
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Exécuter le script par défaut
ENTRYPOINT ["python"]
CMD ["main.py"]

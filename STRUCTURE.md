# Structure du projet

## Organisation des fichiers

```
.
├── main.py                 # Point d'entrée principal
├── utils.py               # Classe MeteoMarineMarseille et fonctions utilitaires
├── consolidate_data.py    # Consolidation et splits ML
├── pyproject.toml         # Dépendances (uv)
├── Dockerfile             # Image Docker
├── docker-compose.yml     # Orchestration
├── Makefile              # Commandes utiles
├── .gitignore            # Fichiers à ignorer
└── data/
    ├── raw/              # Données brutes (organisées par année)
    │   ├── 2024/         # Fichiers CSV de 2024
    │   ├── 2025/         # Fichiers CSV de 2025
    │   └── 2026/         # Fichiers CSV de 2026
    └── processed/        # Données consolidées pour ML
```

## Fichiers principaux

### `main.py`
- **Point d'entrée** pour la collecte de données
- Constantes: `START_DATE`, `END_DATE`
- Exécution: `python main.py` ou `uv run main.py`

### `utils.py`
- **Classe `MeteoMarineMarseille`** avec méthodes:
  - `get_marine_weather_open_meteo()` - Vagues
  - `get_weather_data_open_meteo()` - Météo générale
  - `collect_historical_data_batch()` - Collecte par lots
  - `process_to_daily_summary()` - Traitement quotidien
  - `save_data()` - Sauvegarde organisée

### `consolidate_data.py`
- Étape 2: Fusion des données mensuelles
- Création des splits train/val/test
- Exécution: `python consolidate_data.py` ou `uv run consolidate_data.py`

## Workflow de développement

### Localement (recommandé pour le développement)

```bash
# Installation
uv sync

# Collecte données
uv run python main.py

# Consolidation
uv run python consolidate_data.py
```

### Avec Make

```bash
make install
make collect
make consolidate
```

### Avec Docker

```bash
make docker-build
docker compose run --rm collect-data
docker compose run --rm consolidate-data
```

## Avantages de cette structure

✅ **Séparation des responsabilités**
- `main.py` : orchestration et configuration
- `utils.py` : logique métier
- `consolidate_data.py` : post-traitement

✅ **Facilité de test**
- Les fonctions sont isolées dans `utils.py`
- Facile à mocker et tester

✅ **Réutilisabilité**
- `utils.MeteoMarineMarseille` peut être importée ailleurs
- `consolidate_data.py` indépendant

✅ **Maintenabilité**
- Code lisible et organisé
- Facile d'ajouter de nouvelles fonctionnalités

## Imports

```python
# Dans main.py ou tout autre fichier
from utils import MeteoMarineMarseille

# Utilisation
client = MeteoMarineMarseille(api_key)
data = client.collect_historical_data_batch(start, end)
```

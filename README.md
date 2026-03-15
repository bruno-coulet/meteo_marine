# Météo Marine Marseille - ML Classification

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tool: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Outil de collecte et de classification (Machine Learning) des données de météo marine de Marseille via l'API Open-Meteo.

---

## Objectif
Récupérer et organiser les données quotidiennes de météo marine (vagues, vent, température) pour un outil de prédiction des annulations de navettes maritimes de Marseille.

Le projet croise les données de vagues (Marine API) et les données atmosphériques (ERA5 Archive).

## Installation Rapide (Recommandé)

Le pipeline principal utilise Open-Meteo et ne nécessite pas de clé API.

```bash
# 1. Installation des dépendances avec uv
uv sync

# 2 : Pipeline complet (option A)
uv run python main.py

# 2 : étapes séparées  (option B)
# Collecte des données en fichiers mensuels
uv run python src/collect.py
# Consolidation en un seul fichier
uv run python src/consolidate.py
# Splits du fichier consolidé en jeu de train/val/test pour le Machine Learning
uv run python src/split.py
```

## Pipeline de Données
Le projet suit un flux strict pour garantir la reproductibilité des modèles :

1. **Collecte (`src/collect.py`)** : Récupération des données brutes -> `data/raw/`.
2. **Consolidation (`src/consolidate.py`)** : Fusion et nettoyage -> `data/processed/consolidated_YYYY_MM_DD-au-MM_DD.parquet`.
3. **Split ML (`src/split.py`)** : Création des fichiers `train.parquet`, `val.parquet`, `test.parquet` -> `data/processed/`.
4. **Pipeline (`main.py`)** : Orchestration des 3 étapes (collecte + consolidation + split).

### Features collectées :
* **Marine** : Hauteur/Direction/Période des vagues, Houle.
* **Météo** : Température, Vent (vitesse/rafales/direction).

## Modes Avancés (Docker & Makefile)
Si vous préférez ne pas utiliser `uv` en direct :
* **Make** : `make install`, `make collect`, `make consolidate`, `make split`.
* **Docker** : `docker compose run --rm collect-data`.

Le mode **Make** est idéal pour standardiser les commandes dans l'équipe, avec des alias simples à retenir.
Le mode **Docker** est recommandé si vous voulez un environnement reproductible, isolé de votre machine locale.
En pratique : utilisez `uv` pour itérer vite en local, puis `Docker`/`Make` pour fiabiliser l'exécution sur d'autres postes ou en CI.

## Performance

| Opération | Temps | Taille |
|-----------|-------|--------|
| Collecte 31 jours | ~2-3 min | ~5-10 KB |
| Consolidation annuelle | ~5-10 sec | ~150-200 KB |
| Chargement train.parquet | <50 ms | ~70-120 KB |

## Documentation Additionnelle
* [README_ML.md](documentation/README_ML.md) : Guide spécifique pour l'entraînement des modèles.
* [UTILS_EXPLIQUE.md](documentation/UTILS_EXPLIQUE.md) : Détails de l'architecture du code.
* [DOCKER.md](documentation/DOCKER.md) : Configuration des conteneurs.
* [DOCKER_EXPLIQUE.md](documentation/DOCKER_EXPLIQUE.md) : Explication détaillée de l'architecture Docker.

Note : un ancien script Météo-France a été archivé dans [archive/requete_meteo_france.py](archive/requete_meteo_france.py).

---

**Licence :** Ce projet est sous licence MIT.
**Auteur :** Bruno Coulet - *Projet réalisé en alternance IA*.
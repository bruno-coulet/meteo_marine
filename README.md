# Météo Marine Marseille - ML Classification

Projet de collecte et classification Machine Learning des données de météo marine de Marseille via Open-Meteo.

## 🎯 Objectif

Récupérer et organiser les données quotidiennes de météo marine (vagues, vent, température) pour du Machine Learning.

## 📊 Données collectées

### Données Marines (Open-Meteo Marine API)
- Hauteur max des vagues (m)
- Direction des vagues (°)
- Période des vagues (s)
- Hauteur des vagues de vent (m)
- Hauteur de la houle (m)

### Données Météo (Open-Meteo ERA5 Archive)
- Température max/min (°C)
- Vitesse du vent max (km/h)
- Rafales max (km/h)
- Direction du vent dominant (°)

## 🚀 Quick Start

### Localement (avec uv)

```bash
# 1. Installation des dépendances
uv sync

# 2. Collecte des données (voir configuration ci-dessous)
uv run python main.py

# 3. Consolidation et splits ML
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

## ⚙️ Configuration

### `main.py` - Constantes principales

```python
# Période à récupérer
START_DATE = "2025-11-01"  # None = il y a 730 jours
END_DATE = "2025-11-30"    # None = aujourd'hui

# Format de sauvegarde (CSV recommandé pour ML)
SAVE_JSON = False          # True = sauvegarde aussi .json
```

## 📁 Structure des données

```
data/
├── raw/                    # Données brutes (par année)
│   ├── 2025/
│   │   ├── meteo_2025_01_01-31.csv
│   │   ├── meteo_2025_02_01-28.csv
│   │   └── meteo_2025_11_01-30.csv   (5-10 KB par mois, rapide)
│   └── 2024/
│       └── meteo_2024_12_01-31.csv
└── processed/              # Données ML prêtes
    ├── marseille_marine_consolidated.csv
    ├── train.csv           # 70%
    ├── val.csv             # 15%
    └── test.csv            # 15%
```

## 📊 Fichiers générés

| Fichier | Format | Taille | Utilité |
|---------|--------|--------|---------|
| `meteo_YYYY_MM_DD-DD.csv` | CSV | 5-10 KB | Chargement rapide, pandas |
| `meteo_YYYY_MM_DD-DD.json` | JSON | 15-25 KB | Archivage, APIs (optionnel) |
| `consolidated.csv` | CSV | Cumulé | Toutes les données fusionnées |
| `train.csv` | CSV | 70% | Entraînement ML |
| `val.csv` | CSV | 15% | Validation ML |
| `test.csv` | CSV | 15% | Test/Évaluation ML |

## 🏗️ Architecture du projet

```
main.py              # Point d'entrée + constantes
utils.py             # Classe MeteoMarineMarseille
consolidate_data.py  # Consolidation + splits
pyproject.toml       # Dépendances (uv)
Dockerfile           # Image Docker
docker-compose.yml   # Orchestration
Makefile             # Commandes utiles
```

## 📦 Dépendances

- **requests** - Requêtes HTTP
- **pandas** - Manipulation données
- **numpy** - Calculs numériques
- **scikit-learn** - Machine Learning

Optionnelles:
- **tensorflow/torch** - Deep Learning
- **jupyter** - Notebooks exploration

## 🔄 Workflow complet

1. **Collecte** → `uv run python main.py`
   - Récupère données mensuelles via API
   - Crée `data/raw/YYYY/meteo_*.csv` (par année)

2. **Consolidation** → `uv run python consolidate_data.py`
   - Fusionne tous les CSV mensuels
   - Crée `data/processed/marseille_marine_consolidated.csv`
   - Génère splits train/val/test

3. **ML** → Vos modèles
   ```python
   import pandas as pd
   train = pd.read_csv('data/processed/train.csv')
   # ... votre pipeline ML
   ```

## 🐳 Docker

Voir [DOCKER.md](DOCKER.md) pour le guide complet.

```bash
# Build
docker build -t meteo-marine:latest .

# Run
docker run --rm -v $(pwd)/data:/app/data meteo-marine:latest

# Compose
docker compose run --rm collect-data
```

## 📚 Documentation

- [README_ML.md](README_ML.md) - Utilisation en Machine Learning
- [DOCKER.md](DOCKER.md) - Guide Docker complet
- [DOCKER_EXPLIQUE.md](DOCKER_EXPLIQUE.md) - Docker détaillé (architecture, troubleshooting)
- [STRUCTURE.md](STRUCTURE.md) - Organisation du projet
- [UTILS_EXPLIQUE.md](UTILS_EXPLIQUE.md) - Architecture utils.py (APIs, flux, fonctions)

## 🔍 Performance

| Opération | Temps | Taille |
|-----------|-------|--------|
| Collecte 31 jours | ~2-3 min | ~5-10 KB |
| Consolidation annuelle | ~5-10 sec | ~150-200 KB |
| Chargement train.csv | <50 ms | 70 KB |
| JSON (optionnel) | +5x lent | +150% taille |

## 🎓 Utilisation en ML

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Charger données
train_df = pd.read_csv('data/processed/train.csv')

# Features et target
X = train_df.drop(['date'], axis=1)
y = train_df['wave_height_max']  # ou autre colonne cible

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Votre modèle ML
# ...
```

## 📝 API Open-Meteo

- **Marine**: `https://marine-api.open-meteo.com/v1/marine`
- **Weather**: `https://archive-api.open-meteo.com/v1/era5`
- Gratuit, pas d'authentification requise
- Historique complet disponible

## 📄 Licence

MIT

## 👤 Auteur

Bruno Coulet


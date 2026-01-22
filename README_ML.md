# Workflow ML - Météo Marine Marseille

## Structure des données

```
data/
├── raw/                          # Données brutes organisées par année
│   ├── 2024/
│   │   └── meteo_2024_12_01-31.csv
│   ├── 2025/
│   │   ├── meteo_2025_01_01-31.csv
│   │   ├── meteo_2025_02_01-28.csv
│   │   └── meteo_2025_11_01-30.csv
│   └── 2026/
│       └── meteo_2026_01_01-22.csv
└── processed/                    # Données consolidées pour ML
    ├── marseille_marine_consolidated.csv    # Toutes les données fusionnées
    ├── train.csv                 # 70% des données
    ├── val.csv                   # 15% des données
    └── test.csv                  # 15% des données
```

## Workflow complet

### Étape 1: Récupérer les données brutes

```bash
python requete_ok.py
```

**Options de personnalisation** (en début du script):
```python
START_DATE = None      # None = il y a 730 jours, ou "2025-01-22"
END_DATE = None        # None = aujourd'hui, ou "2026-01-22"
```

**Résultat:**
- Crée des fichiers CSV mensuels: `data/raw/YYYY_MM/meteo_YYYY_MM_DD-DD.csv`
- Chaque fichier contient les données quotidiennes de vagues, vent, température, etc.

### Étape 2: Consolider et créer les splits

```bash
python consolidate_data.py
```

**Résultat:**
- `data/processed/marseille_marine_consolidated.csv` → toutes les données fusionnées
- `data/processed/train.csv` → 70% des données (entraînement)
- `data/processed/val.csv` → 15% des données (validation)
- `data/processed/test.csv` → 15% des données (test)

## Données disponibles

Chaque ligne représente un jour avec les colonnes:

### Données marines
- `wave_height_max` - Hauteur max des vagues (m)
- `wave_direction_dominant` - Direction des vagues (°)
- `wave_period_max` - Période des vagues (s)
- `wind_wave_height_max` - Hauteur vagues de vent (m)
- `swell_wave_height_max` - Hauteur de la houle (m)

### Données météo
- `temperature_max` - Température max (°C)
- `temperature_min` - Température min (°C)
- `wind_speed_max` - Vitesse vent max (km/h)
- `wind_gusts_max` - Rafales max (km/h)
- `wind_direction_dominant` - Direction vent (°)

### Métadonnées
- `date` - Date (YYYY-MM-DD)

## Utilisation en ML

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Charger les données
train_df = pd.read_csv('data/processed/train.csv')
val_df = pd.read_csv('data/processed/val.csv')
test_df = pd.read_csv('data/processed/test.csv')

# Préparation des features et cible
X_train = train_df.drop('date', axis=1)
X_val = val_df.drop('date', axis=1)
X_test = test_df.drop('date', axis=1)

# Normalisation
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# ... votre modèle ML ici
```

## Notes importantes

✅ Les données sont **temporellement ordonnées** → pas de mélange train/test aléatoire naïf  
✅ Format CSV simple → compatible avec tous les frameworks (sklearn, PyTorch, TensorFlow)  
✅ Données historiques fiables → source Open-Meteo (réanalyse ERA5)  
✅ Structure modulaire → facile de rajouter de nouvelles périodes

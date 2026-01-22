"""
Script de consolidation des données mensuelles en un seul fichier exploitable
pour le machine learning
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def consolidate_monthly_data():
    """
    Consolide tous les fichiers CSV mensuels de data/raw/ en un seul fichier
    Sauvegarde dans data/processed/marseille_marine_consolidated.csv
    """
    
    # Parcours tous les fichiers CSV dans data/raw/
    raw_dir = Path("data/raw")
    
    if not raw_dir.exists():
        print(f"Erreur: Le dossier {raw_dir} n'existe pas")
        print("Exécutez d'abord requete_ok.py pour générer les données")
        return False
    
    # Récupération de tous les CSV
    csv_files = sorted(raw_dir.glob("**/meteo_*.csv"))
    
    if not csv_files:
        print(f"Aucun fichier CSV trouvé dans {raw_dir}")
        return False
    
    print(f"=== CONSOLIDATION DES DONNÉES ===")
    print(f"Nombre de fichiers à fusionner: {len(csv_files)}\n")
    
    # Lecture et fusion de tous les fichiers
    dataframes = []
    total_rows = 0
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            print(f"✓ Lecture: {csv_file.relative_to(Path.cwd())} ({len(df)} lignes)")
            dataframes.append(df)
            total_rows += len(df)
        except Exception as e:
            print(f"✗ Erreur lecture {csv_file}: {e}")
            continue
    
    if not dataframes:
        print("Aucun fichier n'a pu être lu")
        return False
    
    # Fusion des DataFrames
    print(f"\nFusion de {len(dataframes)} fichiers...")
    consolidated_df = pd.concat(dataframes, ignore_index=True)
    
    # Suppression des doublons si présents
    initial_rows = len(consolidated_df)
    consolidated_df = consolidated_df.drop_duplicates(subset=['date'], keep='first')
    duplicates_removed = initial_rows - len(consolidated_df)
    
    if duplicates_removed > 0:
        print(f"Doublons supprimés: {duplicates_removed}")
    
    # Tri par date
    if 'date' in consolidated_df.columns:
        consolidated_df['date'] = pd.to_datetime(consolidated_df['date'])
        consolidated_df = consolidated_df.sort_values('date').reset_index(drop=True)
    
    # Création du dossier processed/
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarde du fichier consolidé
    output_file = processed_dir / "marseille_marine_consolidated.csv"
    consolidated_df.to_csv(output_file, index=False)
    
    print(f"\n=== RÉSULTATS ===")
    print(f"✓ Fichier consolidé: {output_file}")
    print(f"Total de lignes: {len(consolidated_df)}")
    print(f"Plage temporelle: {consolidated_df['date'].min()} à {consolidated_df['date'].max()}")
    print(f"\nDimensions: {consolidated_df.shape}")
    print(f"Colonnes: {', '.join(consolidated_df.columns.tolist())}")
    
    # Statistiques
    print(f"\n=== STATISTIQUES ===")
    numeric_cols = consolidated_df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) > 0:
        print(consolidated_df[numeric_cols].describe())
    
    return True


def create_ml_splits(train_ratio=0.7, val_ratio=0.15, random_state=42):
    """
    Crée les splits train/val/test à partir du fichier consolidé
    par défaut: 70% train, 15% val, 15% test
    """
    
    consolidated_file = Path("data/processed/marseille_marine_consolidated.csv")
    
    if not consolidated_file.exists():
        print(f"Erreur: {consolidated_file} n'existe pas")
        print("Exécutez consolidate_data() d'abord")
        return False
    
    # Lecture du fichier consolidé
    df = pd.read_csv(consolidated_file)
    print(f"\n=== CRÉATION DES SPLITS TRAIN/VAL/TEST ===")
    print(f"Données totales: {len(df)} lignes")
    
    # Création des indices mélangés
    indices = df.index.tolist()
    from random import Random
    rng = Random(random_state)
    rng.shuffle(indices)
    
    # Calcul des points de split
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    # Split
    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]
    
    train_df = df.iloc[train_idx].sort_index().reset_index(drop=True)
    val_df = df.iloc[val_idx].sort_index().reset_index(drop=True)
    test_df = df.iloc[test_idx].sort_index().reset_index(drop=True)
    
    # Sauvegarde
    processed_dir = Path("data/processed")
    
    train_file = processed_dir / "train.csv"
    val_file = processed_dir / "val.csv"
    test_file = processed_dir / "test.csv"
    
    train_df.to_csv(train_file, index=False)
    val_df.to_csv(val_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f"✓ Train: {len(train_df)} lignes ({train_ratio*100:.0f}%) → {train_file}")
    print(f"✓ Val: {len(val_df)} lignes ({val_ratio*100:.0f}%) → {val_file}")
    print(f"✓ Test: {len(test_df)} lignes ({(1-train_ratio-val_ratio)*100:.0f}%) → {test_file}")
    
    return True


if __name__ == "__main__":
    # Étape 1: Consolider les données mensuelles
    if consolidate_monthly_data():
        print("\n" + "="*60)
        # Étape 2: Créer les splits ML
        create_ml_splits()
    else:
        print("Consolidation échouée")

"""
Script principal pour récupérer les données météo marine de Marseille
via les APIs Open-Meteo

Utilisation:
    - Modifiez START_DATE et END_DATE ci-dessous
    - Exécutez: `uv run main.py` ou `python main.py` si vous n'aveez installer uv pour gérrer l'environnement virtuel
    - Les données seront sauvegardées dans data/raw/YYYY/ sous forme de fichiers CSV mensuels (et JSON si SAVE_JSON=True)
"""

from datetime import datetime, timedelta
from src.utils import MeteoMarineMarseille

# ============================================================================
# CONFIGURATION - Modifier ces constantes pour personnaliser les requêtes
# ============================================================================
# Format: "YYYY-MM-DD" ou None pour utiliser les valeurs par défaut
START_DATE = "2026-01-01"  # None = il y a 730 jours; exemple: "2024-01-22"
END_DATE = "2026-02-28"    # None = aujourd'hui; exemple: "2026-01-22"

# Format de sauvegarde des données
# CSV (recommandé pour ML):
#   + Léger (~5-10 KB pour 31 jours)
#   + Rapide à charger (~1-2 ms)
#   + Compatible pandas/sklearn
#   - Moins flexible pour structures complexes
#
# JSON (utile pour archivage/APIs):
#   + Flexibilité (structures imbriquées possibles)
#   + Standard universel
#   - Lourd (~15-25 KB, +150% vs CSV)
#   - Lent à charger (~5-10 ms, +5x vs CSV)
SAVE_JSON = False  # True = sauvegarde aussi .json; False = que .csv (recommandé)
# ============================================================================


def main():
    """Point d'entrée principal"""

    # Parsing des dates de configuration
    if END_DATE is None:
        end_date = datetime.now()
    else:
        try:
            end_date = datetime.strptime(END_DATE, "%Y-%m-%d")
        except ValueError:
            print(f"Erreur: END_DATE '{END_DATE}' doit être au format YYYY-MM-DD")
            return

    if START_DATE is None:
        start_date = end_date - timedelta(days=730)
    else:
        try:
            start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
        except ValueError:
            print(f"Erreur: START_DATE '{START_DATE}' doit être au format YYYY-MM-DD")
            return

    # Vérification que start_date < end_date
    if start_date >= end_date:
        print(
            f"Erreur: START_DATE ({start_date.date()}) doit être avant END_DATE ({end_date.date()})"
        )
        return

    print("=== COLLECTE DES DONNÉES MÉTÉO MARINE MARSEILLE ===")
    print(f"Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    print(f"Durée: {(end_date - start_date).days} jours")

    # Initialisation du client
    meteomarine = MeteoMarineMarseille()

    try:
        # Collecte des données par lots (utilise Open-Meteo principalement)
        print("\n1. Collecte des données via Open-Meteo...")
        batch_data = meteomarine.collect_historical_data_batch(start_date, end_date)

        # Traitement en résumé quotidien
        print("\n2. Traitement des données quotidiennes...")
        daily_df = meteomarine.process_to_daily_summary(batch_data)

        if not daily_df.empty:
            # Sauvegarde du résumé quotidien dans structure organisée par mois
            csv_files, json_files = meteomarine.save_data(
                daily_df, start_date, end_date, save_json=SAVE_JSON
            )

            print(f"\n=== RÉSULTATS ===")
            print(f"Nombre de jours collectés: {len(daily_df)}")
            print(f"Période effective: {daily_df['date'].min()} à {daily_df['date'].max()}")
            print(f"\nFichiers sauvegardés:")
            for csv_file in csv_files:
                print(f"- {csv_file}")

            # Affichage d'un échantillon
            print(f"\n=== ÉCHANTILLON DES DONNÉES ===")
            print(daily_df.head(10).to_string())

            # Statistiques
            print(f"\n=== STATISTIQUES ===")
            numeric_cols = daily_df.select_dtypes(include=["float64", "int64"]).columns
            if len(numeric_cols) > 0:
                print(daily_df[numeric_cols].describe())

        else:
            print("Aucune donnée quotidienne n'a pu être extraite.")

    except Exception as e:
        print(f"Erreur lors de la collecte : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

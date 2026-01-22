"""
Script principal pour récupérer les bulletins météo marine de Marseille
via les APIs disponibles de Météo-France et alternatives

Utilisation:
    - Modifiez START_DATE et END_DATE ci-dessous
    - Exécutez: python main.py ou uv run main.py
"""

from datetime import datetime, timedelta
from utils import MeteoMarineMarseille

# ============================================================================
# CONFIGURATION - Modifier ces constantes pour personnaliser les requêtes
# ============================================================================
# Format: "YYYY-MM-DD" ou None pour utiliser les valeurs par défaut
START_DATE = "2025-11-01"  # None = il y a 730 jours; exemple: "2024-01-22"
END_DATE = "2025-11-30"    # None = aujourd'hui; exemple: "2026-01-22"

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

    # Configuration API (optionnel pour Open-Meteo)
    api_key = "eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNFltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJORFEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIwNDZmYjk2OS0zNDg2LTQ2ZDUtYTY2Ni0xYmU0ZDY0NWJkMTQiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6IjNnZnBtUmZVYXF3amFHNjlLT0pHVU01d3hlY2EiLCJuYmYiOjE3NTU0MjEyNzIsImF6cCI6IjNnZnBtUmZVYXF3amFHNjlLT0pHVU01d3hlY2EiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hdXRoMlwvdG9rZW4iLCJleHAiOjE3NTU0MjQ4NzIsImlhdCI6MTc1NTQyMTI3MiwianRpIjoiZTRhODg1MmUtNDA1Ni00YjRiLThmNjYtMWUyODBmMzU5NDM1IiwiY2xpZW50X2lkIjoiM2dmcG1SZlVhcXdqYUc2OUtPSkdVTTV3eGVjYSJ9.a2hY2X9V-l5a5pvaAJVEkO0LQ05Sk2B8KVmrB0dxmYgR08soBQ2Q4naNqJ3XgncZ-Na3KrnSLWjlTH_iVcMOKNzGFsu4PVQhHgeKiUV_JStNtGjT2RRpSKH_g6HfqYXaAJ0tWDVgIrdpT_mg1iwiQMbP5NTSlgD5V32h9v0331Yph47IUJ_vCFpwH9SUwxU8SSUbubu8_aKuvnjUWHs2ySealWu18CFkpHswXe_ttWT1uo02aZ41JjRIshx8UIyAKpTdfcQa6FuYO5UrkDkc7e1cthYcQvkTtZjYhSZgh5dGvFDiyd4jDVjo9ttVcNQluWihRCozDihkqiAPVGEsxg"

    print("=== COLLECTE DES DONNÉES MÉTÉO MARINE MARSEILLE ===")
    print(f"Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    print(f"Durée: {(end_date - start_date).days} jours")

    # Initialisation du client
    meteomarine = MeteoMarineMarseille(api_key)

    try:
        # Collecte des données par lots (utilise Open-Meteo principalement)
        print("\n1. Collecte des données via Open-Meteo...")
        batch_data = meteomarine.collect_historical_data_batch(start_date, end_date)

        # Traitement en résumé quotidien
        print("\n2. Traitement des données quotidiennes...")
        daily_df = meteomarine.process_to_daily_summary(batch_data)

        if not daily_df.empty:
            # Sauvegarde du résumé quotidien dans structure organisée par mois
            csv_file, json_file = meteomarine.save_data(
                daily_df, start_date, end_date, save_json=SAVE_JSON
            )

            print(f"\n=== RÉSULTATS ===")
            print(f"Nombre de jours collectés: {len(daily_df)}")
            print(f"Période effective: {daily_df['date'].min()} à {daily_df['date'].max()}")
            print(f"\nFichier sauvegardé:")
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

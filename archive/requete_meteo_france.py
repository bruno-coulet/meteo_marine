#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script legacy archivé pour expérimenter la collecte via l'API Météo-France.

Ce script ne fait pas partie du pipeline principal, qui repose sur Open-Meteo.
Il est conservé comme référence technique uniquement.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests


class MeteoMarineMarseille:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://portail-api.meteofrance.fr"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        self.marseille_coords = {"lat": 43.2965, "lon": 5.3698}
        self.zone_maritime = "MEDITERRANEAN_WEST"

    def get_daily_marine_bulletin(self, date):
        date_str = date.strftime("%Y-%m-%d")
        endpoint = "/v1/marine/bulletins/coastal"

        params = {
            "date": date_str,
            "zone": self.zone_maritime,
            "lat": self.marseille_coords["lat"],
            "lon": self.marseille_coords["lon"],
            "format": "json",
        }

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                print("Rate limit atteint, attente de 60 secondes...")
                time.sleep(60)
                return self.get_daily_marine_bulletin(date)

            print(f"Erreur {response.status_code} pour {date_str}: {response.text}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête pour {date_str}: {e}")
            return None

    def get_marine_observations(self, date):
        date_str = date.strftime("%Y-%m-%d")
        endpoint = "/v1/marine/observations"

        params = {
            "date": date_str,
            "lat": self.marseille_coords["lat"],
            "lon": self.marseille_coords["lon"],
            "radius": 50,
            "format": "json",
        }

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()

            print(f"Erreur observations {response.status_code} pour {date_str}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Erreur observations pour {date_str}: {e}")
            return None

    def collect_historical_data(self, start_date, end_date):
        all_data = []
        current_date = start_date

        print(f"Récupération des données du {start_date} au {end_date}")

        while current_date <= end_date:
            print(f"Traitement de {current_date.strftime('%Y-%m-%d')}...")

            bulletin = self.get_daily_marine_bulletin(current_date)
            observations = self.get_marine_observations(current_date)

            if bulletin or observations:
                all_data.append(
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "bulletin": bulletin,
                        "observations": observations,
                    }
                )

            time.sleep(1)
            current_date += timedelta(days=1)

        return all_data

    def save_to_json(self, data, filename):
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        print(f"Données sauvegardées dans {filename}")

    def extract_summary_dataframe(self, data):
        summary_data = []

        for daily_record in data:
            date = daily_record["date"]
            bulletin = daily_record.get("bulletin", {})

            summary_data.append(
                {
                    "date": date,
                    "wind_direction": bulletin.get("wind", {}).get("direction"),
                    "wind_speed": bulletin.get("wind", {}).get("speed"),
                    "wind_gusts": bulletin.get("wind", {}).get("gusts"),
                    "wave_height": bulletin.get("waves", {}).get("height"),
                    "wave_period": bulletin.get("waves", {}).get("period"),
                    "visibility": bulletin.get("visibility"),
                    "weather_condition": bulletin.get("weather", {}).get("condition"),
                }
            )

        return pd.DataFrame(summary_data)


def main():
    api_key = os.getenv("METEO_FRANCE_API_KEY")
    if not api_key:
        print("Erreur: définissez METEO_FRANCE_API_KEY pour utiliser ce script archivé.")
        return

    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    meteomarine = MeteoMarineMarseille(api_key)

    try:
        historical_data = meteomarine.collect_historical_data(start_date, end_date)

        meteomarine.save_to_json(
            historical_data,
            f"data/marseille_marine_weather_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json",
        )

        summary_df = meteomarine.extract_summary_dataframe(historical_data)
        summary_df.to_csv(
            f"data/marseille_marine_summary_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            index=False,
        )

        print(f"Collecte terminée ! {len(historical_data)} jours de données récupérés.")
        print(f"Résumé : {len(summary_df)} entrées dans le DataFrame")

    except Exception as e:
        print(f"Erreur lors de la collecte : {e}")


if __name__ == "__main__":
    main()
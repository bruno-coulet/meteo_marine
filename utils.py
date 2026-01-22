"""
Utilitaires pour la collecte et traitement des données météo marine
"""

import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from pathlib import Path


class MeteoMarineMarseille:
    """Client pour récupérer les données de météo marine de Marseille"""

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.meteofrance_base = "https://portail-api.meteofrance.fr"
        self.open_meteo_base = "https://marine-api.open-meteo.com/v1"

        # Headers pour Météo-France API
        self.headers = {}
        if api_key:
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

        # Coordonnées de Marseille
        self.marseille_coords = {"lat": 43.2965, "lon": 5.3698}

    def get_marine_weather_open_meteo(self, start_date, end_date):
        """
        Récupère les données météo marine via Open-Meteo (gratuit, pas de clé requise)
        Inclut les données historiques et les vagues
        """
        url = f"{self.open_meteo_base}/marine"

        params = {
            "latitude": self.marseille_coords["lat"],
            "longitude": self.marseille_coords["lon"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": [
                "wave_height",
                "wave_direction",
                "wave_period",
                "wind_wave_height",
                "wind_wave_direction",
                "wind_wave_period",
                "swell_wave_height",
                "swell_wave_direction",
                "swell_wave_period",
            ],
            "daily": [
                "wave_height_max",
                "wave_direction_dominant",
                "wave_period_max",
                "wind_wave_height_max",
                "swell_wave_height_max",
            ],
            "timezone": "Europe/Paris",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur Open-Meteo marine: {e}")
            return None

    def get_weather_data_open_meteo(self, start_date, end_date):
        """
        Récupère les données météo générales (vent, etc.) via Open-Meteo
        """
        url = "https://archive-api.open-meteo.com/v1/era5"

        params = {
            "latitude": self.marseille_coords["lat"],
            "longitude": self.marseille_coords["lon"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "surface_pressure",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "wind_direction_10m_dominant",
            ],
            "timezone": "Europe/Paris",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur Open-Meteo weather: {e}")
            return None

    def collect_historical_data_batch(self, start_date, end_date, batch_days=30):
        """
        Collecte les données par lots pour éviter les timeouts
        """
        all_data = []
        current_start = start_date

        print(
            f"Récupération des données du {start_date} au {end_date} par lots de {batch_days} jours"
        )

        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=batch_days - 1), end_date)

            print(
                f"Traitement du lot: {current_start.strftime('%Y-%m-%d')} à {current_end.strftime('%Y-%m-%d')}"
            )

            # Données marine via Open-Meteo
            marine_data = self.get_marine_weather_open_meteo(current_start, current_end)

            # Données météo générales via Open-Meteo
            weather_data = self.get_weather_data_open_meteo(current_start, current_end)

            if marine_data or weather_data:
                batch_data = {
                    "period_start": current_start.strftime("%Y-%m-%d"),
                    "period_end": current_end.strftime("%Y-%m-%d"),
                    "marine_data": marine_data,
                    "weather_data": weather_data,
                }
                all_data.append(batch_data)

            # Pause entre les lots
            time.sleep(2)
            current_start = current_end + timedelta(days=1)

        return all_data

    def process_to_daily_summary(self, batch_data_list):
        """
        Convertit les données par lots en résumé quotidien
        """
        daily_records = []

        for batch in batch_data_list:
            marine_data = batch.get("marine_data", {})
            weather_data = batch.get("weather_data", {})

            # Traitement des données quotidiennes marines
            if marine_data and "daily" in marine_data:
                daily_marine = marine_data["daily"]
                dates = daily_marine.get("time", [])

                for i, date_str in enumerate(dates):
                    try:
                        record = {
                            "date": date_str,
                            "wave_height_max": (
                                daily_marine.get("wave_height_max", [None])[i]
                                if i < len(daily_marine.get("wave_height_max", []))
                                else None
                            ),
                            "wave_direction_dominant": (
                                daily_marine.get("wave_direction_dominant", [None])[i]
                                if i < len(daily_marine.get("wave_direction_dominant", []))
                                else None
                            ),
                            "wave_period_max": (
                                daily_marine.get("wave_period_max", [None])[i]
                                if i < len(daily_marine.get("wave_period_max", []))
                                else None
                            ),
                            "wind_wave_height_max": (
                                daily_marine.get("wind_wave_height_max", [None])[i]
                                if i < len(daily_marine.get("wind_wave_height_max", []))
                                else None
                            ),
                            "swell_wave_height_max": (
                                daily_marine.get("swell_wave_height_max", [None])[i]
                                if i < len(daily_marine.get("swell_wave_height_max", []))
                                else None
                            ),
                        }

                        # Ajout des données météo si disponibles
                        if weather_data and "daily" in weather_data:
                            daily_weather = weather_data["daily"]
                            weather_dates = daily_weather.get("time", [])

                            if date_str in weather_dates:
                                weather_idx = weather_dates.index(date_str)
                                record.update(
                                    {
                                        "temperature_max": (
                                            daily_weather.get("temperature_2m_max", [None])[
                                                weather_idx
                                            ]
                                            if weather_idx
                                            < len(daily_weather.get("temperature_2m_max", []))
                                            else None
                                        ),
                                        "temperature_min": (
                                            daily_weather.get("temperature_2m_min", [None])[
                                                weather_idx
                                            ]
                                            if weather_idx
                                            < len(daily_weather.get("temperature_2m_min", []))
                                            else None
                                        ),
                                        "wind_speed_max": (
                                            daily_weather.get("wind_speed_10m_max", [None])[
                                                weather_idx
                                            ]
                                            if weather_idx
                                            < len(daily_weather.get("wind_speed_10m_max", []))
                                            else None
                                        ),
                                        "wind_gusts_max": (
                                            daily_weather.get("wind_gusts_10m_max", [None])[
                                                weather_idx
                                            ]
                                            if weather_idx
                                            < len(daily_weather.get("wind_gusts_10m_max", []))
                                            else None
                                        ),
                                        "wind_direction_dominant": (
                                            daily_weather.get("wind_direction_10m_dominant", [None])[
                                                weather_idx
                                            ]
                                            if weather_idx
                                            < len(
                                                daily_weather.get("wind_direction_10m_dominant", [])
                                            )
                                            else None
                                        ),
                                    }
                                )

                        daily_records.append(record)

                    except (IndexError, ValueError) as e:
                        print(f"Erreur traitement date {date_str}: {e}")
                        continue

        return pd.DataFrame(daily_records)

    def save_data(self, data, start_date, end_date, save_json=False):
        """
        Sauvegarde les données organisées par mois
        Format: data/raw/YYYY_MM/meteo_YYYY_MM_DD-DD.csv
        """
        # Création du dossier de sortie structuré par mois
        start_month = start_date.strftime("%Y_%m")

        output_dir = Path("data/raw") / start_month
        output_dir.mkdir(parents=True, exist_ok=True)

        # Nom du fichier: meteo_2025_01_01-31.csv
        filename = f"meteo_{start_date.strftime('%Y_%m_%d')}-{end_date.strftime('%d')}.csv"
        csv_file = output_dir / filename

        # Sauvegarde CSV
        if isinstance(data, pd.DataFrame):
            data.to_csv(csv_file, index=False)
            print(f"✓ CSV sauvegardé: {csv_file}")

        # Sauvegarde JSON optionnelle (données brutes)
        json_file = None
        if save_json:
            json_filename = filename.replace(".csv", ".json")
            json_file = output_dir / json_filename
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"✓ JSON sauvegardé: {json_file}")

        return csv_file, json_file

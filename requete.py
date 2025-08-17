#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour récupérer les bulletins météo marine de Marseille
via les APIs disponibles de Météo-France et alternatives
"""

import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

class MeteoMarineMarseille:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.meteofrance_base = "https://portail-api.meteofrance.fr"
        self.open_meteo_base = "https://marine-api.open-meteo.com/v1"
        
        # Headers pour Météo-France API
        self.headers = {}
        if api_key:
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        
        # Coordonnées de Marseille
        self.marseille_coords = {
            "lat": 43.2965,
            "lon": 5.3698
        }
    
    def get_marine_weather_open_meteo(self, start_date, end_date):
        """
        Récupère les données météo marine via Open-Meteo (gratuit, pas de clé requise)
        Inclut les données historiques et les vagues
        """
        # Open-Meteo Marine Weather API
        url = f"{self.open_meteo_base}/marine"
        
        params = {
            "latitude": self.marseille_coords["lat"],
            "longitude": self.marseille_coords["lon"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": [
                "wave_height", "wave_direction", "wave_period",
                "wind_wave_height", "wind_wave_direction", "wind_wave_period",
                "swell_wave_height", "swell_wave_direction", "swell_wave_period"
            ],
            "daily": [
                "wave_height_max", "wave_direction_dominant", "wave_period_max",
                "wind_wave_height_max", "swell_wave_height_max"
            ],
            "timezone": "Europe/Paris"
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
                "temperature_2m", "relative_humidity_2m", "precipitation",
                "surface_pressure", "cloud_cover",
                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
            ],
            "daily": [
                "temperature_2m_max", "temperature_2m_min",
                "wind_speed_10m_max", "wind_gusts_10m_max",
                "wind_direction_10m_dominant"
            ],
            "timezone": "Europe/Paris"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur Open-Meteo weather: {e}")
            return None
    
    def get_meteofrance_bulletins_bms(self, date):
        """
        Essaie de récupérer les BMS (Bulletins Météo Marine) depuis Météo-France
        Note: Les endpoints exacts peuvent varier
        """
        if not self.api_key:
            return None
            
        # Essai avec différents endpoints possibles
        possible_endpoints = [
            "/public/DPBulletin/v1/bms",
            "/public/bulletins/v1/marine",
            "/v1/marine/bms"
        ]
        
        for endpoint in possible_endpoints:
            try:
                url = f"{self.meteofrance_base}{endpoint}"
                params = {
                    "zone": "MEDITWEST",  # Zone Méditerranée Ouest
                    "date": date.strftime("%Y-%m-%d")
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    continue  # Essaie l'endpoint suivant
                else:
                    print(f"Erreur {response.status_code} sur {endpoint}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Erreur réseau sur {endpoint}: {e}")
                continue
        
        return None
    
    def scrape_meteofrance_bms_web(self, date):
        """
        Alternative: scraping des BMS depuis le site web public
        """
        try:
            # URL du site public Météo-France marine
            url = "https://meteofrance.com/meteo-marine"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Ici il faudrait parser le HTML pour extraire les BMS
                # Cette partie nécessiterait BeautifulSoup
                print("Accès au site web réussi, parsing HTML requis")
                return {"source": "web", "status": "accessible"}
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur scraping web: {e}")
            return None
    
    def collect_historical_data_batch(self, start_date, end_date, batch_days=30):
        """
        Collecte les données par lots pour éviter les timeouts
        """
        all_data = []
        current_start = start_date
        
        print(f"Récupération des données du {start_date} au {end_date} par lots de {batch_days} jours")
        
        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=batch_days-1), end_date)
            
            print(f"Traitement du lot: {current_start.strftime('%Y-%m-%d')} à {current_end.strftime('%Y-%m-%d')}")
            
            # Données marine via Open-Meteo
            marine_data = self.get_marine_weather_open_meteo(current_start, current_end)
            
            # Données météo générales via Open-Meteo  
            weather_data = self.get_weather_data_open_meteo(current_start, current_end)
            
            if marine_data or weather_data:
                batch_data = {
                    "period_start": current_start.strftime("%Y-%m-%d"),
                    "period_end": current_end.strftime("%Y-%m-%d"),
                    "marine_data": marine_data,
                    "weather_data": weather_data
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
                            "wave_height_max": daily_marine.get("wave_height_max", [None])[i] if i < len(daily_marine.get("wave_height_max", [])) else None,
                            "wave_direction_dominant": daily_marine.get("wave_direction_dominant", [None])[i] if i < len(daily_marine.get("wave_direction_dominant", [])) else None,
                            "wave_period_max": daily_marine.get("wave_period_max", [None])[i] if i < len(daily_marine.get("wave_period_max", [])) else None,
                            "wind_wave_height_max": daily_marine.get("wind_wave_height_max", [None])[i] if i < len(daily_marine.get("wind_wave_height_max", [])) else None,
                            "swell_wave_height_max": daily_marine.get("swell_wave_height_max", [None])[i] if i < len(daily_marine.get("swell_wave_height_max", [])) else None
                        }
                        
                        # Ajout des données météo si disponibles
                        if weather_data and "daily" in weather_data:
                            daily_weather = weather_data["daily"]
                            weather_dates = daily_weather.get("time", [])
                            
                            if date_str in weather_dates:
                                weather_idx = weather_dates.index(date_str)
                                record.update({
                                    "temperature_max": daily_weather.get("temperature_2m_max", [None])[weather_idx] if weather_idx < len(daily_weather.get("temperature_2m_max", [])) else None,
                                    "temperature_min": daily_weather.get("temperature_2m_min", [None])[weather_idx] if weather_idx < len(daily_weather.get("temperature_2m_min", [])) else None,
                                    "wind_speed_max": daily_weather.get("wind_speed_10m_max", [None])[weather_idx] if weather_idx < len(daily_weather.get("wind_speed_10m_max", [])) else None,
                                    "wind_gusts_max": daily_weather.get("wind_gusts_10m_max", [None])[weather_idx] if weather_idx < len(daily_weather.get("wind_gusts_10m_max", [])) else None,
                                    "wind_direction_dominant": daily_weather.get("wind_direction_10m_dominant", [None])[weather_idx] if weather_idx < len(daily_weather.get("wind_direction_10m_dominant", [])) else None
                                })
                        
                        daily_records.append(record)
                        
                    except (IndexError, ValueError) as e:
                        print(f"Erreur traitement date {date_str}: {e}")
                        continue
        
        return pd.DataFrame(daily_records)
    
    def save_data(self, data, base_filename):
        """
        Sauvegarde les données en JSON et CSV
        """
        # Création du dossier de sortie
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        
        # Sauvegarde JSON complète
        json_file = output_dir / f"{base_filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Données complètes sauvegardées: {json_file}")
        
        # Si c'est un DataFrame, sauvegarde CSV
        if isinstance(data, pd.DataFrame):
            csv_file = output_dir / f"{base_filename}.csv"
            data.to_csv(csv_file, index=False)
            print(f"Résumé CSV sauvegardé: {csv_file}")
            
            return json_file, csv_file
        
        return json_file, None

def main():
    # Configuration
    api_key = "eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNFltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJORFEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIwNDZmYjk2OS0zNDg2LTQ2ZDUtYTY2Ni0xYmU0ZDY0NWJkMTQiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6IjNnZnBtUmZVYXF3amFHNjlLT0pHVU01d3hlY2EiLCJuYmYiOjE3NTU0MjEyNzIsImF6cCI6IjNnZnBtUmZVYXF3amFHNjlLT0pHVU01d3hlY2EiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hdXRoMlwvdG9rZW4iLCJleHAiOjE3NTU0MjQ4NzIsImlhdCI6MTc1NTQyMTI3MiwianRpIjoiZTRhODg1MmUtNDA1Ni00YjRiLThmNjYtMWUyODBmMzU5NDM1IiwiY2xpZW50X2lkIjoiM2dmcG1SZlVhcXdqYUc2OUtPSkdVTTV3eGVjYSJ9.a2hY2X9V-l5a5pvaAJVEkO0LQ05Sk2B8KVmrB0dxmYgR08soBQ2Q4naNqJ3XgncZ-Na3KrnSLWjlTH_iVcMOKNzGFsu4PVQhHgeKiUV_JStNtGjT2RRpSKH_g6HfqYXaAJ0tWDVgIrdpT_mg1iwiQMbP5NTSlgD5V32h9v0331Yph47IUJ_vCFpwH9SUwxU8SSUbubu8_aKuvnjUWHs2ySealWu18CFkpHswXe_ttWT1uo02aZ41JjRIshx8UIyAKpTdfcQa6FuYO5UrkDkc7e1cthYcQvkTtZjYhSZgh5dGvFDiyd4jDVjo9ttVcNQluWihRCozDihkqiAPVGEsxg"
    
    # Période des 2 dernières années
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    print("=== COLLECTE DES DONNÉES MÉTÉO MARINE MARSEILLE ===")
    print(f"Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    
    # Initialisation du client
    meteomarine = MeteoMarineMarseille(api_key)
    
    try:
        # Collecte des données par lots (utilise Open-Meteo principalement)
        print("\n1. Collecte des données via Open-Meteo...")
        batch_data = meteomarine.collect_historical_data_batch(start_date, end_date)
        
        # Sauvegarde des données brutes
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_file, _ = meteomarine.save_data(
            batch_data,
            f"marseille_marine_raw_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}"
        )
        
        # Traitement en résumé quotidien
        print("\n2. Traitement des données quotidiennes...")
        daily_df = meteomarine.process_to_daily_summary(batch_data)
        
        if not daily_df.empty:
            # Sauvegarde du résumé quotidien
            summary_json, summary_csv = meteomarine.save_data(
                daily_df,
                f"marseille_marine_daily_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}"
            )
            
            print(f"\n=== RÉSULTATS ===")
            print(f"Nombre de jours collectés: {len(daily_df)}")
            print(f"Période effective: {daily_df['date'].min()} à {daily_df['date'].max()}")
            print(f"\nFichiers générés:")
            print(f"- Données brutes: {raw_file}")
            print(f"- Résumé quotidien: {summary_csv}")
            
            # Affichage d'un échantillon
            print(f"\n=== ÉCHANTILLON DES DONNÉES ===")
            print(daily_df.head(10).to_string())
            
            # Statistiques
            print(f"\n=== STATISTIQUES ===")
            numeric_cols = daily_df.select_dtypes(include=['float64', 'int64']).columns
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
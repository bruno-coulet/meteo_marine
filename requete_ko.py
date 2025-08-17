#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour récupérer les bulletins météo marine de Marseille
via l'API de Météo-France pour les 2 dernières années
"""

import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from pathlib import Path


class MeteoMarineMarseille:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://portail-api.meteofrance.fr"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Coordonnées de Marseille
        self.marseille_coords = {
            "lat": 43.2965,
            "lon": 5.3698
        }
        
        # Zone maritime de Marseille (à adapter selon l'API)
        self.zone_maritime = "MEDITERRANEAN_WEST"
        
    def get_daily_marine_bulletin(self, date):
        """
        Récupère le bulletin météo marine pour une date donnée
        """
        date_str = date.strftime("%Y-%m-%d")
        
        # Endpoint pour les bulletins côtiers (à adapter selon l'API réelle)
        endpoint = f"/v1/marine/bulletins/coastal"
        
        params = {
            "date": date_str,
            "zone": self.zone_maritime,
            "lat": self.marseille_coords["lat"],
            "lon": self.marseille_coords["lon"],
            "format": "json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"Rate limit atteint, attente de 60 secondes...")
                time.sleep(60)
                return self.get_daily_marine_bulletin(date)
            else:
                print(f"Erreur {response.status_code} pour {date_str}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête pour {date_str}: {e}")
            return None
    
    def get_marine_observations(self, date):
        """
        Récupère les observations marines (SHIP, BUOY) pour une date donnée
        """
        date_str = date.strftime("%Y-%m-%d")
        
        # Endpoint pour les observations marines
        endpoint = f"/v1/marine/observations"
        
        params = {
            "date": date_str,
            "lat": self.marseille_coords["lat"],
            "lon": self.marseille_coords["lon"],
            "radius": 50,  # Rayon en km autour de Marseille
            "format": "json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erreur observations {response.status_code} pour {date_str}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erreur observations pour {date_str}: {e}")
            return None
    
    def collect_historical_data(self, start_date, end_date):
        """
        Collecte les données historiques sur une période donnée
        """
        all_data = []
        current_date = start_date
        
        print(f"Récupération des données du {start_date} au {end_date}")
        
        while current_date <= end_date:
            print(f"Traitement de {current_date.strftime('%Y-%m-%d')}...")
            
            # Récupération du bulletin quotidien
            bulletin = self.get_daily_marine_bulletin(current_date)
            
            # Récupération des observations
            observations = self.get_marine_observations(current_date)
            
            if bulletin or observations:
                daily_data = {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "bulletin": bulletin,
                    "observations": observations
                }
                all_data.append(daily_data)
            
            # Pause pour éviter la limitation de débit
            time.sleep(1)
            
            current_date += timedelta(days=1)
        
        return all_data
    
    def save_to_json(self, data, filename):
        """
        Sauvegarde les données au format JSON
        """
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Données sauvegardées dans {filename}")
    
    def extract_summary_dataframe(self, data):
        """
        Extrait un résumé des données sous forme de DataFrame pandas
        """
        summary_data = []
        
        for daily_record in data:
            date = daily_record["date"]
            bulletin = daily_record.get("bulletin", {})
            
            # Extraction des informations principales (à adapter selon la structure réelle)
            summary = {
                "date": date,
                "wind_direction": bulletin.get("wind", {}).get("direction"),
                "wind_speed": bulletin.get("wind", {}).get("speed"),
                "wind_gusts": bulletin.get("wind", {}).get("gusts"),
                "wave_height": bulletin.get("waves", {}).get("height"),
                "wave_period": bulletin.get("waves", {}).get("period"),
                "visibility": bulletin.get("visibility"),
                "weather_condition": bulletin.get("weather", {}).get("condition")
            }
            
            summary_data.append(summary)
        
        return pd.DataFrame(summary_data)

def main():
    # Configuration
    api_key = "eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNFltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJORFEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIwNDZmYjk2OS0zNDg2LTQ2ZDUtYTY2Ni0xYmU0ZDY0NWJkMTQiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6IjNnZnBtUmZVYXF3amFHNjlLT0pHVU01d3hlY2EiLCJuYmYiOjE3NTU0MjEyNzIsImF6cCI6IjNnZnBtUmZVYXF3amFHNjlLT0pHVU01d3hlY2EiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hdXRoMlwvdG9rZW4iLCJleHAiOjE3NTU0MjQ4NzIsImlhdCI6MTc1NTQyMTI3MiwianRpIjoiZTRhODg1MmUtNDA1Ni00YjRiLThmNjYtMWUyODBmMzU5NDM1IiwiY2xpZW50X2lkIjoiM2dmcG1SZlVhcXdqYUc2OUtPSkdVTTV3eGVjYSJ9.a2hY2X9V-l5a5pvaAJVEkO0LQ05Sk2B8KVmrB0dxmYgR08soBQ2Q4naNqJ3XgncZ-Na3KrnSLWjlTH_iVcMOKNzGFsu4PVQhHgeKiUV_JStNtGjT2RRpSKH_g6HfqYXaAJ0tWDVgIrdpT_mg1iwiQMbP5NTSlgD5V32h9v0331Yph47IUJ_vCFpwH9SUwxU8SSUbubu8_aKuvnjUWHs2ySealWu18CFkpHswXe_ttWT1uo02aZ41JjRIshx8UIyAKpTdfcQa6FuYO5UrkDkc7e1cthYcQvkTtZjYhSZgh5dGvFDiyd4jDVjo9ttVcNQluWihRCozDihkqiAPVGEsxg"  # À remplacer par votre clé API
    
    # Période des 2 dernières années
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    # Initialisation du client
    meteomarine = MeteoMarineMarseille(api_key)
    
    # Collecte des données
    try:
        historical_data = meteomarine.collect_historical_data(start_date, end_date)
        
        # Sauvegarde des données complètes
        meteomarine.save_to_json(
            historical_data, 
            f"data/marseille_marine_weather_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        )
        
        # Création d'un résumé DataFrame
        summary_df = meteomarine.extract_summary_dataframe(historical_data)
        summary_df.to_csv(
            f"data/marseille_marine_summary_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            index=False
        )
        
        print(f"Collecte terminée ! {len(historical_data)} jours de données récupérés.")
        print(f"Résumé : {len(summary_df)} entrées dans le DataFrame")
        
    except Exception as e:
        print(f"Erreur lors de la collecte : {e}")

if __name__ == "__main__":
    main()
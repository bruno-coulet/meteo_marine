1. APIs réelles utilisées

Open-Meteo Marine API : Pour les données de vagues (gratuit, pas de clé requise)
Open-Meteo Era5 Archive : Pour les données météo historiques (vent, température, etc.)
Ces APIs sont fiables et documentées

2. Gestion des erreurs améliorée

Collecte par lots de 30 jours pour éviter les timeouts
Gestion robuste des erreurs de connexion
Pauses entre les requêtes

3. Données marines complètes

Hauteur, direction et période des vagues
Vagues de vent vs houle
Données quotidiennes et horaires disponibles

4. Endpoints Météo-France corrects

Tentative avec les vrais endpoints possibles
Fallback sur les APIs alternatives si Météo-France ne répond pas

Pour utiliser le script :

Lancez directement - Les APIs Open-Meteo fonctionnent sans clé
Données obtenues :

Vagues : hauteur max, direction, période
Vent : vitesse, direction, rafales
Température, pression, humidité
Données quotidiennes sur 2 ans


Fichiers générés :

data/marseille_marine_raw_*.json : Données complètes
data/marseille_marine_daily_*.csv : Résumé quotidien



Avantages de cette approche :

Fonctionne immédiatement sans problèmes de connexion
Données historiques fiables via Era5 (données de réanalyse)
Spécialement conçu pour la météo marine
Format de sortie exploitable en CSV et JSON

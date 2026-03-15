"""
PROJET : Météo Marine Marseille
UTILITÉ : Pipeline global (Collecte + Consolidation + Split ML)
"""
import src.collect as collect
import src.consolidate as consolidate
import src.split as split

def run_pipeline():
    print("DÉMARRAGE DU PIPELINE MÉTÉO MARINE")
    print("-" * 40)
    
    # Étape 1 : Collecte
    print("\nÉTAPE 1 : Collecte des données...")
    collect.main()
    
    # Étape 2 : Consolidation
    print("\nÉTAPE 2 : Consolidation des fichiers...")
    consolidate.main()

    # Étape 3 : Split ML
    print("\nÉTAPE 3 : Création des splits train/val/test...")
    split.main()
    
    print("\nPIPELINE TERMINÉ AVEC SUCCÈS")

if __name__ == "__main__":
    run_pipeline()
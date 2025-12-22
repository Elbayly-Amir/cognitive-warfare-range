import sys
from src.generator import ThreatGenerator
from src.config import settings
from src.connector import OpenCTIConnector

def main():
    """Point d'entrée principal du script"""
    print("--- DÉMARRAGE DU CONNECTEUR SOCIAL ENGINEERING ---")
    
    masked_token = settings.opencti_token[:4] + "****"
    print(f"Cible : {settings.opencti_url}")
    
    try:
        connector = OpenCTIConnector()
        generator = ThreatGenerator()
    except Exception as e:
        print(f"Erreur lors de l'initialisation du générateur : {e}")
        sys.exit(1)

    print("\n1. Génération des menaces fictives...")
    posts = generator.generate_posts(3)
    
    # 3. Injection dans OpenCTI
    print("\n2. Injection dans OpenCTI...")
    for post in posts:
        connector.send_post(post)
    
    print("\n--- TERMINE ---")
    print("Va voir dans OpenCTI : Menu 'Analyses' -> 'Notes'")

if __name__ == "__main__":
    main()
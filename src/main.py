import sys
import time
import random
import signal
from src.generator import ThreatGenerator
from src.config import settings
from src.connector import OpenCTIConnector

"""Gestion du signal d'arrêt"""
def signal_handler(sig, frame):
    print("\n[!] Arrêt du Cyber Range demandé. Fermeture propre...")
    sys.exit(0)

def main():

    signal.signal(signal.SIGINT, signal_handler)
    print("--- DÉMARRAGE DU CYBER RANGE ---")
    masked_token = settings.opencti_token[:4] + "****"
    print(f"Cible : {settings.opencti_url} (Token: {masked_token})")
    
    try:
        connector = OpenCTIConnector()
        generator = ThreatGenerator()
    except Exception as e:
        print(f"[X] Erreur critique au démarrage : {e}")
        sys.exit(1)

    print("Initialisation terminée. Entrée dans la boucle de simulation.\n")

    batch_count = 1
    while True:
        try:
            nb_posts = random.randint(1, 3)
            print(f"--- Salve #{batch_count} : Génération de {nb_posts} menace(s) ---")            
            posts = generator.generate_posts(nb_posts)
            
            for post in posts:
                connector.send_post(post)
            
            batch_count += 1
            sleep_time = random.randint(15, 30)
            print(f"[zzz] Pause tactique de {sleep_time} secondes...\n")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"[!] Erreur dans la boucle (le service continue) : {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
from pycti import OpenCTIApiClient
from src.config import settings
from src.models import SocialMediaPost
from datetime import datetime
import time

class OpenCTIConnector:
    
    
    def __init__(self):
        """Initialise le connecteur OpenCTI et vérifie la connexion"""
        self.api_url = settings.opencti_url
        self.api_token = settings.opencti_token

        print(f"[Wait] Tentative de connexion à {self.api_url}...")
        
        for i in range(30): # 30 tentatives
            try:
                # On tente d'initialiser le client
                self.api = OpenCTIApiClient(
                    url=self.api_url,
                    token=self.api_token,
                    log_level="error",
                    ssl_verify=False
                )
                self.api.health_check()
                
                print(f"[V] Connexion établie avec succès au bout de {i} tentatives !")
                return
                
            except Exception as e:
                print(f"[...] OpenCTI n'est pas encore prêt. Attente 10s... ({e})")
                time.sleep(10) 

        raise TimeoutError("Impossible de joindre OpenCTI après 5 minutes.")


    def _create_identity(self, author_name: str, description: str) -> dict:
        """Crée ou récupère l'auteur du post (Identity) dans OpenCTI"""
        return self.api.identity.create(
            type="Individual",
            name=author_name,
            description=description,
            create_indicator=False
        )

    def send_post(self, post: SocialMediaPost):
        """Transforme notre Post en objet STIX et l'envoie"""
        print(f"[>>] Envoi du post de {post.author.pseudo} vers OpenCTI...")

        try:
            author_stix = self._create_identity(
                author_name=post.author.pseudo,
                description=f"Bot suspect détecté. Score réputation: {post.author.reputation_score}/100"
            )

            note = self.api.note.create(
                abstract=f"Post Social Media sur {post.platform}",
                content=post.content,
                created=post.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                createdBy=author_stix["id"],
                confidence=80
            )
            
            print(f"   [V] Succès ! Note créée avec ID: {note['id']}")
            return note

        except Exception as e:
            print(f"   [X] Erreur lors de l'envoi : {e}")
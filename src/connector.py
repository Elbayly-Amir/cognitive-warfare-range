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
        
        for i in range(30):
            try:
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

        
    def _analyze_content(self, content: str) -> list[str]:
        """Détecte des mots clés et retourne des labels"""
        labels = ["SIMULATION"]
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["fake", "complot", "secret", "truth" ]):
            labels.append("DISINFORMATION")
        if any(word in content_lower for word in ["urgent", "click here", "act now", "limited time"]):
            labels.append("SCAM")
        if any(word in content_lower for word in ["attack", "hacked", "leak", "password"]):
            labels.append("SECURITY_INCIDENT")

        return labels

    def send_post(self, post: SocialMediaPost):
        print(f"[>>] Envoi du post de {post.author.pseudo} vers OpenCTI...")

        try:
            detected_labels = self._analyze_content(post.content)
            
            for label_name in detected_labels:
                color = "#ff0000" if label_name in ["DISINFORMATION", "SECURITY_INCIDENT"] else "#00bfff"
                try:
                    self.api.label.create(value=label_name, color=color)
                except Exception:
                    pass 

            author_stix = self._create_identity(
                author_name=post.author.pseudo,
                description=f"Bot suspect. Reputation: {post.author.reputation_score}"
            )

            note = self.api.note.create(
                abstract=f"Post sur {post.platform}",
                content=post.content,
                created=post.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                createdBy=author_stix["id"],
                confidence=80
            )
            
            for label in detected_labels:
                self.api.stix_domain_object.add_label(
                    id=note["id"], 
                    label_name=label
                )

            print(f"   [V] Succès ! Note {note['id']} taguée avec : {detected_labels}")
            return note

        except Exception as e:
            print(f"   [X] Erreur : {e}")
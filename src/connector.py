from pycti import OpenCTIApiClient
from src.config import settings
from src.models import SocialMediaPost
from datetime import datetime
import time
from src.label_manager import LabelManager
from src.indicator_manager import IndicatorManager

class OpenCTIConnector:
    
    
    def __init__(self):
        """Initialise le connecteur OpenCTI et vérifie la connexion"""
        self.api_url = settings.opencti_url
        self.api_token = settings.opencti_token
        self.label_manager = LabelManager("labels_config.json")
        self.indicator_manager = IndicatorManager()
        
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


    def send_post(self, post: SocialMediaPost):
            print(f"[>>] Envoi du post de {post.author.pseudo} vers OpenCTI...")

            try:
                detected_labels = self.label_manager.analyze_content(post.content)
                for label_name in detected_labels:
                    rule = self.label_manager.get_rule_by_name(label_name)
                    try:
                        self.api.label.create(
                            value=rule["name"],
                            color=rule["color"]
                        )
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

                indicators = self.indicator_manager.extract_indicators(post.content)
                for indicator in indicators:
                    print(f"   [!] Indicateur technique détecté : {indicator['value']}")
                    
                    stix_indicator = self.api.indicator.create(
                        name=indicator["value"],
                        description=f"Extracted from social media post by {post.author.pseudo}",
                        pattern_type="stix",
                        pattern=f"[{indicator['type']}:value = '{indicator['value']}']",
                        x_opencti_main_observable_type="Domain-Name",
                        valid_from=post.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        score=80,
                        createdBy=author_stix["id"]
                    )
                    
                    self.api.stix_core_relationship.create(
                        fromId=note["id"],
                        toId=stix_indicator["id"],
                        relationship_type="based-on",
                        description="Ce message mentionne cet indicateur technique"
                    )

                print(f"   [V] Succès ! Note {note['id']} traitée ({len(indicators)} indicateurs).")
                return note

            except Exception as e:
                print(f"   [X] Erreur critique lors de l'envoi : {e}")
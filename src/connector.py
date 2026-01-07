from pycti import OpenCTIApiClient
from src.config import settings
from src.models import SocialMediaPost
from datetime import datetime
import time
from src.label_manager import LabelManager
from src.indicator_manager import IndicatorManager

class OpenCTIConnector:
    
    def __init__(self):
        self.api_url = settings.opencti_url
        self.api_token = settings.opencti_token
        self.label_manager = LabelManager("labels_config.json")
        self.indicator_manager = IndicatorManager()
        
        print(f"[Wait] Tentative de connexion à {self.api_url}...")
        self._connect_to_api()

    def _connect_to_api(self):
        """Gère la connexion avec retry"""
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
        return self.api.identity.create(
            type="Individual",
            name=author_name,
            description=description,
            create_indicator=False
        )

    def _process_campaign(self, campaign_name: str, author_id: str):
        """Crée ou récupère une campagne et lie l'auteur"""
        try:
            campaign = self.api.campaign.create(
                name=campaign_name,
                description="Campagne de désinformation détectée par le simulateur.",
                confidence=80,
                createdBy=author_id 
            )
            
            self.api.stix_core_relationship.create(
                fromId=campaign["id"],
                toId=author_id,
                relationship_type="related-to",
                description="Acteur participant à cette campagne"
            )
            return campaign
        except Exception as e:
            print(f"   [WARN] Erreur gestion Campagne '{campaign_name}': {e}")
            return None

    def _process_labels(self, content: str, note_id: str) -> list:
        """Applique les labels"""
        detected_labels = self.label_manager.analyze_content(content)
        for label_name in detected_labels:
            rule = self.label_manager.get_rule_by_name(label_name)
            try:
                self.api.label.create(value=rule["name"], color=rule["color"])
                self.api.stix_domain_object.add_label(id=note_id, label_name=label_name)
            except Exception:
                pass
        return detected_labels

    def _process_location(self, country_code: str):
        """Crée l'objet Pays"""
        if country_code and country_code != "Unknown":
            try:
                return self.api.location.create(
                    name=country_code,
                    type="Country",
                    description=f"Pays d'origine simulé: {country_code}"
                )
            except Exception as e:
                print(f"   [WARN] Erreur création Pays ({country_code}): {e}")
        return None

    def _process_indicators(self, post: SocialMediaPost, note_id: str, author_id: str, location_id: str = None):
        """Gère les indicateurs et corrige l'erreur STIX"""
        indicators = self.indicator_manager.extract_indicators(post.content)
        
        if post.technical_ip:
            indicators.append({"type": "IPv4-Addr", "value": post.technical_ip})

        for data in indicators:
            try:
                pattern, main_type = self._get_pattern_config(data)
                
                stix_indicator = self.api.indicator.create(
                    name=data["value"],
                    description=f"Extracted from post by {post.author.pseudo}",
                    pattern_type="stix",
                    pattern=pattern,
                    x_opencti_main_observable_type=main_type,
                    valid_from=post.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    score=80,
                    createdBy=author_id
                )
                
                self.api.stix_core_relationship.create(
                    fromId=note_id,
                    toId=stix_indicator["id"],
                    relationship_type="related-to",
                    description="Mentionne cet indicateur"
                )
                
                if location_id:
                    self.api.stix_core_relationship.create(
                        fromId=stix_indicator["id"],
                        toId=location_id,
                        relationship_type="related-to",
                        description="Attribution géographique simulée"
                    )
                    
            except Exception as e:
                print(f"   [X] Erreur indicateur {data['value']}: {e}")

    def _get_pattern_config(self, indicator_data):
        value = indicator_data["value"]
        itype = indicator_data["type"]
        if itype == "Domain-Name":
            return f"[domain-name:value = '{value}']", "Domain-Name"
        elif itype == "IPv4-Addr":
            return f"[ipv4-addr:value = '{value}']", "IPv4-Addr"
        elif "Hash" in itype:
            algo = "MD5" if len(value) == 32 else "SHA-256"
            return f"[file:hashes.'{algo}' = '{value}']", "File"
        return None, "Unknown"
    
    def _process_malware(self, malware_info: dict, author_id: str, note_id: str, campaign_id: str = None):
        """Crée le malware, le hash, et lie tout le monde"""
        if not malware_info:
            return

        try:
            malware = self.api.malware.create(
                name=malware_info["name"],
                type=malware_info["type"].lower(),
                description="Malware identifié lors de la simulation.",
                is_family=False,
                createdBy=author_id
            )

            hash_val = malware_info["hash"]
            pattern = f"[file:hashes.'SHA-256' = '{hash_val}']"
            
            indicator = self.api.indicator.create(
                name=hash_val,
                description=f"Hash associé à {malware_info['name']}",
                pattern_type="stix",
                pattern=pattern,
                x_opencti_main_observable_type="File",
                score=90,
                createdBy=author_id
            )

            self.api.stix_core_relationship.create(
                fromId=indicator["id"],
                toId=malware["id"],
                relationship_type="indicates",
                description="Ce hash est une signature de ce malware"
            )

            self.api.stix_core_relationship.create(
                fromId=author_id,
                toId=malware["id"],
                relationship_type="related-to",
                description="L'acteur diffuse ce malware"
            )

            self.api.stix_core_relationship.create(
                fromId=note_id,
                toId=malware["id"],
                relationship_type="related-to"
            )

            if campaign_id:
                 self.api.stix_core_relationship.create(
                    fromId=campaign_id,
                    toId=malware["id"],
                    relationship_type="uses",
                    description="Arsenal déployé durant l'opération"
                )

            print(f"Malware traité : {malware_info['name']}")

        except Exception as e:
            print(f"   [!] Erreur traitement Malware: {e}")

    def send_post(self, post: SocialMediaPost):
        print(f"[>>] Envoi du post de {post.author.pseudo}...")
        try:
            author = self._create_identity(
                post.author.pseudo, 
                f"Bot suspect. Reputation: {post.author.reputation_score}"
            )

            location = self._process_location(post.origin_country)
            location_id = location["id"] if location else None

            if location_id:
                try:
                    self.api.stix_core_relationship.create(
                        fromId=author["id"],
                        toId=location_id,
                        relationship_type="located-at",
                        description="Localisation présumée du bot"
                    )
                except Exception:
                    pass

            campaign_obj = None
            campaign_id = None 

            if post.campaign_name:
                campaign_obj = self._process_campaign(post.campaign_name, author["id"])
                if campaign_obj: campaign_id = campaign_obj["id"]
                
            note = self.api.note.create(
                abstract=f"Post sur {post.platform}",
                content=post.content,
                created=post.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                createdBy=author["id"],
                confidence=80
            )

            if campaign_obj:
                self.api.stix_core_relationship.create(
                    fromId=note["id"],
                    toId=campaign_obj["id"],
                    relationship_type="related-to",
                    description="Fait partie de la campagne"
                )
            
            if post.malware_info:
                self._process_malware(post.malware_info, author["id"], note["id"], campaign_id)

            self._process_labels(post.content, note["id"])
            self._process_indicators(post, note["id"], author["id"], location_id)

            print(f"   [V] Succès ! Note {note['id']} traitée (Campagne: {post.campaign_name}).")
            return note

        except Exception as e:
            print(f"   [X] Erreur critique lors de l'envoi : {e}")
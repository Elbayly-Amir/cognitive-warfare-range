import re

class IndicatorManager:
    def __init__(self):
        """Initialise l'IndicatorManager avec les regex nécessaires."""
        self.domain_regex = r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

    def extract_indicators(self, content: str) -> list[dict]:
        """
        Scan le texte et retourne une liste d'indicateurs STIX potentiels.
        Format retour: [{"type": "domain-name", "value": "example.com"}, ...]
        """
        indicators = []
        domains = re.findall(self.domain_regex, content)
        
        for domain in set(domains):
            clean_domain = domain.rstrip("/")
            
            indicators.append({
                "type": "domain-name",
                "value": clean_domain
            })
            
        return indicators
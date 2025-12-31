import json
import os

class LabelManager:
    def __init__(self, config_path: str = "labels_config.json"):
        """Initialise le gestionnaire de labels"""
        self.rules = self._load_config(config_path)

    def _load_config(self, path: str) -> list:
        """Charge les règles de label depuis le fichier JSON"""
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lecture JSON: {e}")
            return []

    def analyze_content(self, content: str) -> list[str]:
        """Retourne la liste des labels détectés"""
        detected_labels = []
        content_lower = content.lower()

        for rule in self.rules:
            keywords = rule.get("keywords", [])
            if any(k.lower() in content_lower for k in keywords):
                detected_labels.append(rule["name"])

        if "SIMULATION" not in detected_labels:
            detected_labels.append("SIMULATION")
            
        return detected_labels

    def get_rule_by_name(self, name: str) -> dict:
        """Retourne la règle de label correspondant au nom donné"""
        for rule in self.rules:
            if rule["name"] == name:
                return rule
        return {"name": name, "color": "#00bfff", "description": "Auto"}
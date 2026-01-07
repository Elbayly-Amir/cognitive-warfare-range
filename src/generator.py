import json
import random
import os
from faker import Faker
from src.models import SocialMediaPost, SocialMediaUser 
from src.llm_client import LLMClient

class ThreatGenerator:
    def __init__(self, scenario_file: str = "scenarios.json"):
        self.fake = Faker(['fr_FR', 'en_US', 'ru_RU', 'zh_CN'])
        self.config = self._load_scenarios(scenario_file)
        self.llm = LLMClient() 

    def _load_scenarios(self, path: str) -> dict:
        """Charge le JSON complet"""
        if not os.path.exists(path):
            return {"scenarios": [], "personas": []}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Erreur lecture JSON: {e}")
            return {"scenarios": [], "personas": []}

    def _generate_user(self, persona=None) -> SocialMediaUser:
        """Génère un utilisateur, adapté au pays si possible"""
        if persona and persona.get("origin_country") == "RU":
            profile = self.fake["ru_RU"].profile()
        elif persona and persona.get("origin_country") == "CN":
            profile = self.fake["zh_CN"].profile()
        else:
            profile = self.fake.profile()

        return SocialMediaUser(
            pseudo=f"@{profile['username']}",
            average_daily_posts=random.uniform(0.1, 10.0),
            reputation_score=random.randint(0, 100),
            nationality=persona.get("origin_country", "Unknown") if persona else None
        )

    def _pick_scenario(self):
        """Choisit un scénario selon les poids (Probabilités)"""
        scenarios = self.config.get("scenarios", [])
        if not scenarios:
            return None
        
        try:
            weights = [s.get("weight", 1.0) for s in scenarios]
            return random.choices(scenarios, weights=weights, k=1)[0]
        except Exception:
            return random.choice(scenarios)

    def _pick_persona(self):
        """Choisit un persona selon les poids (Probabilités)"""
        personas = self.config.get("personas", [])
        if not personas:
            return None
        
        try:
            weights = [p.get("weight", 1.0) for p in personas]
            return random.choices(personas, weights=weights, k=1)[0]
        except Exception:
            return random.choice(personas)

    def generate_posts(self, count: int = 10) -> list[SocialMediaPost]:
        posts = []
        print(f"   [*] Génération de {count} posts (Mode Persona + IA)...")

        for _ in range(count):
            scenario = self._pick_scenario()
            persona = self._pick_persona()
            
            persona_desc = persona["description"] if persona else None
            country_code = persona.get("origin_country", "Unknown") if persona else "Unknown"
            
            base_content = "Contenu par défaut"
            if scenario and "ai_topic" in scenario:
                try:
                    if hasattr(self.llm, 'generate_content'):
                        base_content = self.llm.generate_content(
                            topic=scenario["ai_topic"], 
                            category=scenario["category"],
                            persona_description=persona_desc
                        )
                    elif hasattr(self.llm, 'generate_text'):
                         prompt = f"Persona: {persona_desc}. Sujet: {scenario['ai_topic']}. Tweet court."
                         base_content = self.llm.generate_text(prompt)
                    else:
                         base_content = f"{scenario['ai_topic']} (Simulation)"
                except Exception as e:
                    print(f"[!] Erreur IA: {e}")
                    base_content = self.fake.text()
            else:
                base_content = self.fake.text()

            malicious_link = f" http://{self.fake.domain_name()}/{self.fake.uri_path()}"
            generated_ip = self.fake.ipv4()
            full_content = f"{base_content} {malicious_link}"

            post = SocialMediaPost(
                platform=self.fake.random_element(elements=("Twitter", "BlueSky", "Mastodon")),
                author=self._generate_user(persona),
                content=full_content,
                created_at=self.fake.date_time_between(start_date="-1h", end_date="now"),
                technical_ip=generated_ip,
                origin_country=country_code
            )
            
            posts.append(post)
            
        return posts
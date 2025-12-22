from faker import Faker
import random
from src.models import SocialMediaUser, SocialMediaPost

class ThreatGenerator:
    def __init__(self):
        self.fake = Faker()
        self.fake = Faker(['fr_FR', 'en_US'])
        
    def _create_random_user(self) -> SocialMediaUser:
        """Méthode privée (interne) pour créer un faux auteur"""
        fake_profile = self.fake.profile()

        clean_username = f"@{fake_profile['username']}".replace(" ", "_")
        
        return SocialMediaUser(
            pseudo=clean_username,
            nationality=random.choice(['FR', 'US', 'RU', 'CN', None]),
            average_daily_posts=round(random.uniform(0.1, 50), 1),
            reputation_score=random.randint(0, 100)
        )
        
    def generate_posts(self, count: int = 10) -> list[SocialMediaPost]:
     """Génère une liste de posts avec des auteurs aléatoires"""
     generated_data = []
     
     for _ in range(count):
        author = self._create_random_user()
        
        post = SocialMediaPost(
            platform=random.choice(['Twitter', 'Mastodon', 'Bluesky']),
            content=self.fake.text(max_nb_chars=280),
            author=author,
            geolocation_lat=float(self.fake.latitude()),
            geolocation_lon=float(self.fake.longitude())
        )
        generated_data.append(post)
        
     return generated_data
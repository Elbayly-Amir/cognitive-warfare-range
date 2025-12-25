import pytest
from src.generator import ThreatGenerator
from src.models import SocialMediaPost

def test_generator_output_types():
    """Test pour vérifier que le générateur produit les bons types de données"""
    generator = ThreatGenerator()
    posts = generator.generate_posts(count=5)
    assert isinstance(posts, list)
    assert len(posts) == 5
    
    first_post = posts[0]
    assert isinstance(first_post, SocialMediaPost)    
    assert len(first_post.content) > 0
    assert first_post.author.pseudo.startswith("@")
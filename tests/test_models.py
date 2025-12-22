import pytest
from pydantic import ValidationError
from src.models import SocialMediaUser, SocialMediaPost

def test_create_valid_user_and_post():
    """Test de création d'un utilisateur et d'un post valides"""
    user = SocialMediaUser(
        pseudo="@white_hat",
        average_daily_posts=5.5,
        reputation_score=80
    )

    assert user.internal_id is not None 
    assert user.pseudo == "@white_hat"

    post = SocialMediaPost(
        platform="Twitter",
        content="Ceci est un test inoffensif.",
        author=user
    )
    
    assert post.content == "Ceci est un test inoffensif."
    assert post.author.pseudo == "@white_hat"

def test_detect_xss_attack():
    """Test pour vérifier que le validateur détecte les tentatives XSS"""
    user = SocialMediaUser(pseudo="@hacker", average_daily_posts=10)
    
    with pytest.raises(ValidationError) as exc_info:
        SocialMediaPost(
            platform="Twitter",
            content="Hello <script>alert('pwned')</script>", # Contenu malveillant
            author=user
        )

    assert "Contenu malveillant détecté" in str(exc_info.value)

def test_invalid_metrics():
    """Test pour vérifier que les métriques invalides sont rejetées"""
    with pytest.raises(ValidationError):
        SocialMediaUser(
            pseudo="@bad_maths",
            average_daily_posts=-5 # Impossible !
        )
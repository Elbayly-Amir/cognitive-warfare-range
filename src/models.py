from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime
from typing import Optional
import uuid


class SocialMediaUser(BaseModel):
    """Modèle représentant un utilisateur de réseau social"""
    internal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pseudo: str = Field(..., min_length=1, description="Le handle visible ex: @dark_vador")
    nationality: Optional[str] = Field(None, description="Nationalité supposée ou déclarée")
    average_daily_posts: float = Field(..., ge=0, description="Vitesse de publication moyenne")
    reputation_score: int = Field(50, ge=0, le=100)


class SocialMediaPost(BaseModel):
    """Modèle représentant un post sur un réseau social"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = Field(..., description="Source: Twitter, Bluesky, Mastodon...")
    content: str = Field(..., min_length=1, description="Le texte du message")
    technical_ip: Optional[str] = Field(None, description="Adresse IP source (métadonnée cachée)")
    origin_country: Optional[str] = Field(None, description="Code pays ISO (ex: RU, CN, FR)")
    geolocation_lat: Optional[float] = None
    geolocation_lon: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: SocialMediaUser

    @field_validator('content')
    def prevent_xss_attempts(cls, v):
        if "<script>" in v:
            raise ValueError("Contenu malveillant détecté (XSS potential)")
        return v
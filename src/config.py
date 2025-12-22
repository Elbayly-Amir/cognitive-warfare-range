from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Configuration de l'application"""
    opencti_url: str = Field(..., description="L'URL de ton instance OpenCTI")
    opencti_token: str = Field(..., description="Le token d'authentification (UUID)")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
"""Configuration centralisée, lue depuis les variables d'environnement.

Aucun secret ne doit avoir de valeur par défaut ici — s'il manque, l'app
doit échouer au démarrage plutôt que de tourner avec une config incomplète.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str
    database_url: str = "sqlite:///./reveal_you.db"
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()

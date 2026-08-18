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
    # Liste d'origines séparées par des virgules (ex: "https://app.example.com,
    # https://autre.example.com"), ou "*" pour tout autoriser. "*" est
    # acceptable tant qu'aucune route n'utilise de cookies/sessions
    # cross-origin (ce n'est pas le cas ici — auth par user_id explicite) ;
    # à restreindre dès qu'un vrai frontend web existe.
    cors_allow_origins: str = "*"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()

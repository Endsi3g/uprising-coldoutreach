"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://prospecting:prospecting@localhost:5432/prospecting"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Apify
    APIFY_TOKEN: str = ""
    APIFY_ACTOR_NAME: str = "uprising-coldoutreach-crawler"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Tracking
    TRACKING_BASE_URL: str = "http://localhost:8000"

    # SMS — TextBelt (free open-source Twilio alternative)
    TEXTBELT_URL: str = "https://textbelt.com/text"
    TEXTBELT_API_KEY: str = "textbelt"  # "textbelt" = free tier (1 SMS/day)

    # Gmail OAuth (Gmail API sending)
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/integrations/gmail/callback"

    # Instagram (Graph API DMs)
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_REDIRECT_URI: str = "http://localhost:8000/integrations/instagram/callback"

    # Webhooks
    WEBHOOK_SECRET: str = ""

    # Jasmin SMS Gateway
    JASMIN_API_URL: str = "http://localhost:8080"
    JASMIN_USER: str = "jookers"
    JASMIN_PASSWORD: str = "jookers"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()

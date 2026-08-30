
from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from a .env file in the working directory.

    Environment variables take precedence over the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""  # OPENAI_API_KEY variable
    model_name: str = "gpt-5.5"  # MODEL_NAME variable

    smtp_host: str = ""  # SMTP_HOST variable
    smtp_port: int = 587  # SMTP_PORT variable
    smtp_username: str = ""  # SMTP_USERNAME variable
    smtp_password: SecretStr = SecretStr("")  # SMTP_PASSWORD variable
    smtp_from: str = ""  # SMTP_FROM variable
    smtp_to: str = ""  # SMTP_TO variable — human consultant's address
    smtp_use_tls: bool = True  # SMTP_USE_TLS variable
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PrinterConfig(BaseSettings):
    """Printer connection settings, loaded from environment variables."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

    host: str = "192.168.0.42"
    port: int = 80
    api_key: str


    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/api/v1"

    def header(self) -> dict[str, str]:
        return {"X-Api-Key": self.api_key}

    def json_headers(self) -> dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

@lru_cache
def get_settings() -> PrinterConfig:
    return PrinterConfig()

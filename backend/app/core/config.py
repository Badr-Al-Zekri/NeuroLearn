from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NeuroLearn AI"
    app_version: str = "0.1.0"
    environment: str = "development"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    embedding_provider: str = "mock"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768
    embedding_batch_size: int = 24
    vector_store_provider: str = "memory"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "neurolearn_chunks"
    chunk_target_tokens: int = 650
    chunk_overlap_tokens: int = 90
    retrieval_top_k: int = 6
    retrieval_min_score: float = 0.18
    cors_origins: list[str] = ["*"]
    max_upload_mb: int = 12

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def ai_mode(self) -> str:
        return "gemini" if self.gemini_api_key else "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()

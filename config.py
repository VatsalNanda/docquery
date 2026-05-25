"""
config.py
---------
Central configuration for docquery.
All settings are loaded from the .env file.
Importing this module anywhere in the project gives access to all settings.
"""

from pydantic_settings import BaseSettings 
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    pydantic-settings automatically reads from .env file.
    """

    # LLM 
    groq_api_key: str 
    llm_model: str = "llama3-70b-8192"

    # Embeddings and Re-ranker (local models)
    embedding_model: str = "all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Qdrant 
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "docquery"

    # App 
    app_env: str = "develop"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings: 
    """
    Returns a cached instance of Settings.
    lru_cache ensures we only read the .env file once,
    not on every function call.
    """
    return Settings()
    
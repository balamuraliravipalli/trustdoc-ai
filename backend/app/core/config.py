from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-5.5", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="trustdoc_chunks", alias="QDRANT_COLLECTION")

    database_url: str = Field(default="sqlite:///./trustdoc.db", alias="DATABASE_URL")
    upload_dir: str = Field(default="./data/uploads", alias="UPLOAD_DIR")

    max_chunk_words: int = Field(default=350, alias="MAX_CHUNK_WORDS")
    chunk_overlap_words: int = Field(default=60, alias="CHUNK_OVERLAP_WORDS")
    top_k: int = Field(default=3, alias="TOP_K")
    min_keyword_score: float = Field(default=0.0, alias="MIN_KEYWORD_SCORE")

    app_api_key: str = Field(default="", alias="APP_API_KEY")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")

    auth_enabled: bool = Field(default=False, alias="AUTH_ENABLED")
    jwt_secret: str = Field(default="change-this-before-deploying", alias="JWT_SECRET")
    demo_admin_email: str = Field(default="admin@trustdoc.local", alias="DEMO_ADMIN_EMAIL")
    demo_admin_password: str = Field(default="admin123", alias="DEMO_ADMIN_PASSWORD")
    demo_user_email: str = Field(default="user@trustdoc.local", alias="DEMO_USER_EMAIL")
    demo_user_password: str = Field(default="user123", alias="DEMO_USER_PASSWORD")
    token_expire_minutes: int = Field(default=240, alias="TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

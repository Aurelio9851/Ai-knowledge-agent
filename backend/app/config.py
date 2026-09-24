from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str
    pinecone_api_key: str

    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.7

    max_file_size: int = 10 * 1024 * 1024
    max_pdf_pages: int = 200

    ollama_model: str = "qwen3.5:9b"
    ollama_host: str = "http://localhost:11434"

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()
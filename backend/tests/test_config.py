from app.config import Settings


def test_settings_defaults():
    settings = Settings(
        database_url="postgresql://test",
        test_database_url="postgresql://test",
        pinecone_api_key="test-key",
    )

    assert settings.retrieval_top_k == 5
    assert settings.retrieval_score_threshold == 0.3

    assert settings.max_file_size == 10 * 1024 * 1024
    assert settings.max_pdf_pages == 200

    assert settings.ollama_model == "qwen3.5:9b"
    assert settings.ollama_host == (
        "http://localhost:11434"
    )

def test_settings_custom_values():
    settings = Settings(
        database_url="postgresql://test",
        test_database_url="postgresql://test",
        pinecone_api_key="test-key",
        retrieval_top_k=10,
        retrieval_score_threshold=0.85,
        max_file_size=5000,
        max_pdf_pages=50,
        ollama_model="custom-model",
        ollama_host="http://custom-host:11434",
    )

    assert settings.retrieval_top_k == 10
    assert settings.retrieval_score_threshold == 0.85
    assert settings.max_file_size == 5000
    assert settings.max_pdf_pages == 50
    assert settings.ollama_model == "custom-model"
    assert settings.ollama_host == (
        "http://custom-host:11434"
    )
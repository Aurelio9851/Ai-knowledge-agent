from ollama import Client
from .config import settings

client = Client(
    host=settings.ollama_host
)


def generate_response(prompt: str) -> str:
    response = client.chat(
        model=settings.ollama_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        think=False,
    )

    return response.message.content



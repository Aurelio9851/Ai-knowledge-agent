from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def create_embedding(text: str) -> list[float]:
    embedding = model.encode(text)

    return embedding.tolist()



def create_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(texts)

    return embeddings.tolist()


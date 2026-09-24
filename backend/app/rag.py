
from .ollama_client import generate_response
def generate_rag_response(
        question: str,
        chunks: list[dict],
) -> str:

    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"""
            [Source {i + 1}]
            Document: {chunk["filename"]}
            Chunk: {chunk["chunk_index"]}

            {chunk["content"]}
            """
        )

    if not context_parts:
        return "I don't know based on the provided documents."
        

    context = "\n\n".join(context_parts)

    prompt = f"""
            Answer the user's question using only the provided context.

            CITATION RULES:
            - Use [Source N] references when making claims based on the context.
            - Every factual claim based on the context should have a citation.
            - Only cite sources that actually support the claim.
            - Do not invent source numbers.
            - If the answer cannot be found in the context, say that you don't know based on the provided documents.

            Context:
            {context}

            Question:
            {question}
            """

    return generate_response(prompt)

   

def build_sources(chunks: list[dict]) -> list[dict]:
    return [
        {
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "chunk_id": chunk["chunk_id"],
            "chunk_index": chunk["chunk_index"],
            "score": chunk["score"],
        }
        for chunk in chunks
    ]
from .ollama_client import generate_response


def route_question(question: str) -> str:
    prompt = f"""
You are a query router for an AI knowledge assistant.

Decide whether the user's question requires information from
the user's uploaded documents.

Return exactly one of these two labels:

DOCUMENT
GENERAL

Use DOCUMENT when:
- The user explicitly refers to a document, paper, file, report, or uploaded content.
- The answer is expected to come from the uploaded documents.
- The user asks about specific information that may be contained in the documents.

Use GENERAL when:
- The user is having a normal conversation.
- The question can be answered using general knowledge.
- The user is greeting the assistant or asking about its capabilities.
- The question does not require the uploaded documents.

Examples:

User: "Hello"
GENERAL

User: "How are you?"
GENERAL

User: "What is machine learning?"
GENERAL

User: "What documents can you access?"
GENERAL

User: "Summarize the main findings of the paper"
DOCUMENT

User: "What does the document say about federated learning?"
DOCUMENT

User: "What are the key results in this report?"
DOCUMENT

Return only the label.

User question:
{question}
"""

    response = generate_response(prompt).strip().upper()

    if response == "DOCUMENT":
        return "DOCUMENT"

    return "GENERAL"
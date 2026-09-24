Sì. Visto che ora abbiamo aggiunto il **query router**, aggiornerei README in tre punti principali:

1. Architettura: Router prima del RAG.
2. Question answering: distinguere `GENERAL` e `DOCUMENT`.
3. Features / struttura: aggiungere il router.

Ti lascio direttamente il **README completo aggiornato**, mantenendo il resto sostanzialmente invariato.

````markdown
# AI Knowledge Agent

A full-stack AI knowledge assistant built around a Retrieval-Augmented Generation (RAG) pipeline with an intelligent query routing layer.

The application allows users to upload documents, process them into searchable chunks, retrieve relevant information using vector similarity search, and ask questions about the stored knowledge base.

A query router first determines whether a question requires information from the uploaded documents or can be answered directly by the language model. This avoids unnecessary retrieval for general conversation and questions that do not depend on the knowledge base.

The backend is built with FastAPI and PostgreSQL, while Pinecone is used as the vector database and Ollama provides the local LLM inference layer.

## Architecture

```text
                    React + TypeScript

                           │

                           │ HTTP / REST

                           ▼

                       FastAPI

                           │

                           ▼

                    Query Router
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
              GENERAL             DOCUMENT
                 │                   │
                 ▼                   ▼
              Ollama            RAG Pipeline
                                     │
                         ┌───────────┼───────────┐
                         │           │           │
                         ▼           ▼           ▼
                    PostgreSQL   Pinecone    Ollama
                    metadata     vector      local LLM
                    & chunks     search

````

### Query routing

```text
User question

      │

      ▼

 Query Router

      │

 ┌────┴─────┐
 │          │
 ▼          ▼
GENERAL   DOCUMENT
 │          │
 ▼          ▼
Ollama    Embedding
             │
             ▼
         Pinecone
             │
             ▼
      Relevant chunks
             │
             ▼
        RAG pipeline
             │
             ▼
           Ollama
```

The router classifies each question into one of two categories:

* `GENERAL` — the question can be answered without using the uploaded documents.
* `DOCUMENT` — the question requires information from the uploaded documents.

General questions are sent directly to the LLM without generating embeddings or querying Pinecone.

Document-related questions follow the complete RAG pipeline.

### Document ingestion

```text
PDF

 │

 ▼

Text extraction

 │

 ▼

Chunking

 │

 ▼

Embeddings

 │

 ├──────────────► PostgreSQL
 │                document + chunks
 │
 └──────────────► Pinecone
                  vector embeddings
```

### Question answering

```text
User question

      │

      ▼

 Query Router

      │
      │
 ┌────┴─────┐
 │          │
 ▼          ▼
GENERAL   DOCUMENT
 │          │
 │          ▼
 │       Embedding
 │          │
 │          ▼
 │       Pinecone
 │          │
 │          ▼
 │    Relevant chunks
 │          │
 │          ▼
 │     PostgreSQL
 │          │
 │          ▼
 │      RAG prompt
 │          │
 └────┬─────┘
      │
      ▼
    Ollama
      │
      ▼
    Answer
      │
      ▼
   + Sources
```

## Features

* PDF document upload
* PDF text extraction
* Configurable document chunking with overlap
* Local embedding generation
* Vector similarity search with Pinecone
* PostgreSQL document and chunk storage
* Retrieval score threshold
* Intelligent query routing
* Direct LLM responses for general questions
* RAG-based question answering for document-related questions
* Multi-document selection for targeted retrieval
* Source attribution in generated answers
* Document CRUD operations
* Document update and deletion
* API error handling
* Database migrations with Alembic
* Automated backend testing with pytest

## Tech Stack

### Backend

* Python 3.11
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL
* Alembic

### AI / Retrieval

* Sentence Transformers
* BAAI/bge-small-en-v1.5
* Pinecone
* Ollama
* Qwen 3.5 9B

### Testing

* pytest
* FastAPI TestClient
* PostgreSQL test database
* Mocking for external services

### Frontend

* React
* TypeScript
* Vite

## Project Structure

```text
ai-knowledge-agent/

│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── embeddings.py
│   │   ├── pinecone_client.py
│   │   ├── ollama_client.py
│   │   ├── chunking.py
│   │   ├── router.py
│   │   └── rag.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_documents.py
│   │   ├── test_retrieval.py
│   │   ├── test_chunking.py
│   │   ├── test_rag.py
│   │   ├── test_pinecone.py
│   │   ├── test_errors.py
│   │   ├── test_config.py
│   │   └── test_chat.py
│   │
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│
├── docker-compose.yml
├── FUTURE_IMPROVEMENTS.txt
└── README.md
```

## Requirements

Before running the backend, install:

* Python 3.11+
* Docker
* A Pinecone account and API key
* Ollama

PostgreSQL is provided through Docker.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>

cd ai-knowledge-agent
```

### 2. Start PostgreSQL

```bash
docker compose up -d
```

The development database is exposed on:

```text
localhost:5432
```

### 3. Create the Python environment

```bash
cd backend

python3.11 -m venv .venv

source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file inside `backend/`:

```env
DATABASE_URL=postgresql://aiagent:aiagent@localhost:5432/aiagent
TEST_DATABASE_URL=postgresql://aiagent:aiagent@localhost:5432/aiagent_test

PINECONE_API_KEY=your-pinecone-api-key

RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=0.5

MAX_FILE_SIZE=10485760
MAX_PDF_PAGES=200

OLLAMA_MODEL=qwen3.5:9b
OLLAMA_HOST=http://localhost:11434
```

Do not commit `.env` or API keys to the repository.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start Ollama

Make sure Ollama is running and the configured model is available.

```bash
ollama pull qwen3.5:9b
```

### 8. Start the API

From `backend/`:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI's interactive documentation is available at:

```text
http://localhost:8000/docs
```

## Database

The application uses PostgreSQL for persistent relational data.

### Documents

Each document stores:

* filename
* extracted/content text
* creation timestamp

### Document chunks

Each document can contain multiple chunks.

Each chunk stores:

* document ID
* chunk index
* chunk content

The relationship between documents and chunks is managed through SQLAlchemy.

Database schema changes are managed with Alembic.

## Vector Search

Document chunks are converted into embeddings using:

```text
BAAI/bge-small-en-v1.5
```

The model produces 384-dimensional embeddings.

Pinecone stores the embeddings together with metadata identifying:

* document ID
* chunk ID
* chunk index

When a user performs a document-related search, the query is embedded using the same model and sent to Pinecone.

Document filters are applied directly during vector search when specific documents are selected.

Only results above the configured similarity threshold are returned.

## Query Routing

Before retrieval, the application classifies each user question using the local language model.

The router returns one of two intents:

```text
GENERAL
DOCUMENT
```

### General questions

Questions that do not require the uploaded knowledge base are sent directly to Ollama.

For example:

```text
User: Hello

Router: GENERAL

→ Ollama
→ Direct answer
```

This avoids unnecessary embedding generation and vector database queries.

### Document questions

Questions that require information from uploaded documents are routed through the RAG pipeline:

```text
User question
      ↓
DOCUMENT
      ↓
Embedding
      ↓
Pinecone
      ↓
Relevant chunks
      ↓
PostgreSQL
      ↓
RAG prompt
      ↓
Ollama
      ↓
Answer + sources
```

## RAG Pipeline

The RAG pipeline consists of four main stages:

### 1. Query embedding

The user's document-related question is converted into a vector representation.

### 2. Retrieval

Pinecone retrieves the most similar document chunks.

### 3. Context construction

The retrieved chunks are loaded from PostgreSQL and assembled into a prompt containing document and source information.

### 4. Generation

The prompt is sent to the configured Ollama model.

The model is instructed to answer using only the retrieved context and to reference the corresponding sources.

If no relevant context is available for a document-related question, the system returns:

```text
I don't know based on the provided documents.
```

## API

### Health

```http
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

### Create document

```http
POST /documents
```

Creates a document directly from text.

### List documents

```http
GET /documents
```

### Get document

```http
GET /documents/{document_id}
```

### Update document

```http
PUT /documents/{document_id}
```

Updates the document and regenerates its chunks and embeddings.

### Delete document

```http
DELETE /documents/{document_id}
```

Deletes the document and its associated vector data.

### Upload PDF

```http
POST /documents/upload
```

Uploads a PDF and automatically:

1. extracts its text;
2. splits it into chunks;
3. generates embeddings;
4. stores the document and chunks;
5. indexes the embeddings in Pinecone.

### Search

```http
GET /search?q=<query>
```

Performs semantic similarity search over the indexed documents.

### Chat

```http
POST /chat
```

Example:

```json
{
  "question": "What does the document say about authentication?"
}
```

The response contains:

* the original question;
* the generated answer;
* the retrieved source chunks.

Questions are first routed as either `GENERAL` or `DOCUMENT`.

General questions are answered directly by Ollama, while document-related questions use the RAG pipeline.

## Testing

The backend currently has a pytest suite covering the main application behavior.

Run:

```bash
pytest -q
```

The test suite covers:

* API endpoints
* document CRUD
* PDF validation
* chunking edge cases
* retrieval behavior
* similarity thresholds
* RAG prompt construction
* Pinecone operations
* configuration
* error handling
* `/search`
* `/chat`

The test suite uses a dedicated PostgreSQL test database and mocks external services where appropriate.


## License

This project is currently intended as a personal portfolio and learning project.


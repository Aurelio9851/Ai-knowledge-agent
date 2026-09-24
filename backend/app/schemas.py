from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    content: str


class DocumentUpdate(BaseModel):
    filename: str
    content: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    content: str

class ChatRequest(BaseModel):
    question: str
    document_ids: list[int] = []

class Source(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
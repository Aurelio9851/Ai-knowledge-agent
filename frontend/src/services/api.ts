import type { ChatResponse, Document } from "../types/api";

const API_URL = "http://localhost:8000";

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to fetch documents");
  }

  return response.json();
}

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Failed to upload document");
  }

  return response.json();
}

export async function deleteDocument(documentId: number): Promise<void> {
  const response = await fetch(`${API_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete document");
  }
}

export async function askQuestion(
  question: string,
  documentIds: number[] = []
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      document_ids: documentIds,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail ?? "Failed to process question"
    );
  }

  return response.json();
}
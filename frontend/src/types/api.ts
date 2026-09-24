export interface Document {
  id: number;
  filename: string;
  content: string;
  created_at?: string;
}

export interface Source {
  document_id: number;
  filename: string;
  chunk_id: number;
  chunk_index: number;
  score: number;
}

export interface ChatResponse {
  question: string;
  answer: string;
  sources: Source[];
}
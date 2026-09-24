import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../services/api";
import type { ChatResponse } from "../types/api";
import Message from "./Message";
import Sources from "./Sources";

interface ChatProps {
  selectedDocumentIds: number[];
  selectedDocumentNames: string[];
}

interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources?: ChatResponse["sources"];
}

function Chat({
  selectedDocumentIds,
  selectedDocumentNames,
}: ChatProps) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function handleSubmit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setQuestion("");
    setError(null);

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setLoading(true);

    try {
      const response = await askQuestion(
        trimmedQuestion,
        selectedDocumentIds
      );

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSuggestion(text: string) {
    setQuestion(text);
  }

  const hasSelectedDocuments =
    selectedDocumentNames.length > 0;

  const scopeDescription =
    selectedDocumentNames.length === 0
      ? "Searching across all documents"
      : selectedDocumentNames.length === 1
        ? `Searching in ${selectedDocumentNames[0]}`
        : `Searching in ${selectedDocumentNames.length} documents`;

  const emptyStateDescription =
    selectedDocumentNames.length === 0
      ? "Ask a question and I'll search your documents for the relevant information."
      : selectedDocumentNames.length === 1
        ? `Ask a question about ${selectedDocumentNames[0]}.`
        : `Ask a question about the ${selectedDocumentNames.length} selected documents.`;

  const inputPlaceholder =
    selectedDocumentNames.length === 0
      ? "Ask anything about your documents..."
      : selectedDocumentNames.length === 1
        ? `Ask about ${selectedDocumentNames[0]}...`
        : `Ask about ${selectedDocumentNames.length} selected documents...`;

  return (
    <section className="chat">
      <div className="chat-header">
        <div>
          <h2>AI Assistant</h2>

          <p>{scopeDescription}</p>
        </div>

        <div className="chat-scope">
          <span className="scope-dot" />

          {hasSelectedDocuments
            ? selectedDocumentNames.length === 1
              ? "Document"
              : `${selectedDocumentNames.length} Documents`
            : "All documents"}
        </div>
      </div>

      <div className="chat-content">
        {messages.length === 0 && !loading ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              ✦
            </div>

            <h3>How can I help?</h3>

            <p>{emptyStateDescription}</p>

            <div className="suggestions">
              <button
                type="button"
                onClick={() =>
                  handleSuggestion(
                    "Summarize the main points"
                  )
                }
              >
                Summarize the main points
              </button>

              <button
                type="button"
                onClick={() =>
                  handleSuggestion(
                    "What are the key findings?"
                  )
                }
              >
                What are the key findings?
              </button>
            </div>
          </div>
        ) : (
          <div className="conversation">
            {messages.map((message) => (
              <div key={message.id}>
                <Message
                  role={message.role}
                  content={message.content}
                />

                {message.role === "assistant" &&
                  message.sources && (
                    <Sources
                      sources={message.sources}
                    />
                  )}
              </div>
            ))}

            {loading && (
              <div className="loading-message">
                <div className="assistant-avatar">
                  ✦
                </div>

                <div className="typing-indicator">
                  <span />
                  <span />
                  <span />
                </div>

                <span className="loading-text">
                  Searching your knowledge base...
                </span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}

      <div className="chat-input-container">
        <form
          className="chat-form"
          onSubmit={handleSubmit}
        >
          <input
            type="text"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder={inputPlaceholder}
            disabled={loading}
          />

          <button
            type="submit"
            disabled={
              loading || !question.trim()
            }
          >
            {loading ? "..." : "↑"}
          </button>
        </form>

        <p className="chat-disclaimer">
          Answers are generated from your uploaded
          documents.
        </p>
      </div>
    </section>
  );
}

export default Chat;
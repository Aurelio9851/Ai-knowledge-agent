import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";
import {
  deleteDocument,
  getDocuments,
} from "./services/api";
import type { Document } from "./types/api";

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] =
    useState<number[]>([]);

  async function loadDocuments() {
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error(
        "Failed to load documents:",
        error
      );
    }
  }

  async function handleDeleteDocument(
    documentId: number
  ) {
    try {
      await deleteDocument(documentId);

      setDocuments((current) =>
        current.filter(
          (document) => document.id !== documentId
        )
      );

      setSelectedDocumentIds((current) =>
        current.filter(
          (id) => id !== documentId
        )
      );
    } catch (error) {
      console.error(
        "Failed to delete document:",
        error
      );
    }
  }

  function handleSelectDocument(
    documentId: number
  ) {
    setSelectedDocumentIds((current) => {
      if (current.includes(documentId)) {
        return current.filter(
          (id) => id !== documentId
        );
      }

      return [...current, documentId];
    });
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  const selectedDocumentNames = documents
    .filter((document) =>
      selectedDocumentIds.includes(document.id)
    )
    .map((document) => document.filename);

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>AI Knowledge Agent</h1>

          <p>
            Ask questions about your documents
          </p>
        </div>

        <div className="status">
          <span className="status-dot" />
          Online
        </div>
      </header>

      <main className="app-content">
        <Sidebar
          documents={documents}
          selectedDocumentIds={selectedDocumentIds}
          onSelectDocument={handleSelectDocument}
          onDeleteDocument={handleDeleteDocument}
          onUploaded={loadDocuments}
        />

        <Chat
          selectedDocumentIds={selectedDocumentIds}
          selectedDocumentNames={selectedDocumentNames}
        />
      </main>
    </div>
  );
}

export default App;
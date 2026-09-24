import type { Document } from "../types/api";

interface DocumentListProps {
  documents: Document[];
  selectedDocumentIds: number[];
  onSelect: (documentId: number) => void;
  onDelete: (documentId: number) => void;
}

function DocumentList({
  documents,
  selectedDocumentIds,
  onSelect,
  onDelete,
}: DocumentListProps) {
  return (
    <div>
      {documents.length === 0 ? (
        <p className="empty-documents">
          No documents uploaded yet.
        </p>
      ) : (
        documents.map((document) => {
          const isSelected =
            selectedDocumentIds.includes(document.id);

          return (
            <div
              key={document.id}
              className={`document-item ${
                isSelected ? "selected" : ""
              }`}
              onClick={() => onSelect(document.id)}
            >
              <div className="document-info">
                <span className="document-icon">
                  📄
                </span>

                <span className="document-name">
                  {document.filename}
                </span>
              </div>

              <button
                className="delete-button"
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  onDelete(document.id);
                }}
                title="Delete document"
              >
                ×
              </button>
            </div>
          );
        })
      )}
    </div>
  );
}

export default DocumentList;
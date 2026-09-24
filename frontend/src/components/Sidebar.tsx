import type { Document } from "../types/api";
import DocumentList from "./DocumentList";
import UploadDocument from "./UploadDocument";

interface SidebarProps {
  documents: Document[];
  selectedDocumentIds: number[];
  onSelectDocument: (documentId: number) => void;
  onDeleteDocument: (documentId: number) => void;
  onUploaded: () => void;
}

function Sidebar({
  documents,
  selectedDocumentIds,
  onSelectDocument,
  onDeleteDocument,
  onUploaded,
}: SidebarProps) {
  return (
    <aside>
      <h2>Knowledge Base</h2>

      <UploadDocument onUploaded={onUploaded} />

      <div className="document-list">
        <DocumentList
          documents={documents}
          selectedDocumentIds={selectedDocumentIds}
          onSelect={onSelectDocument}
          onDelete={onDeleteDocument}
        />
      </div>
    </aside>
  );
}

export default Sidebar;
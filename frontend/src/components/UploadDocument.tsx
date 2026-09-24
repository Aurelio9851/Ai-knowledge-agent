import { useRef, useState } from "react";
import { uploadDocument } from "../services/api";

interface UploadDocumentProps {
  onUploaded: () => void;
}

function UploadDocument({ onUploaded }: UploadDocumentProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleButtonClick() {
    fileInputRef.current?.click();
  }

  async function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await uploadDocument(file);
      onUploaded();
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Upload failed"
      );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        disabled={uploading}
        hidden
      />

      <button
        type="button"
        onClick={handleButtonClick}
        disabled={uploading}
      >
        {uploading ? "Uploading..." : "+ Upload PDF"}
      </button>

      {error && <p>{error}</p>}
    </div>
  );
}

export default UploadDocument;
import type { Source } from "../types/api";

interface SourcesProps {
  sources: Source[];
}

function Sources({ sources }: SourcesProps) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="sources">
      <div className="sources-header">
        <span>Sources</span>
        <span>{sources.length}</span>
      </div>

      <div className="sources-list">
        {sources.map((source, index) => (
          <div
            className="source-card"
            key={source.chunk_id}
          >
            <div className="source-number">
              {index + 1}
            </div>

            <div className="source-icon">
              📄
            </div>

            <div className="source-info">
              <strong>{source.filename}</strong>

              <span>
                Chunk {source.chunk_index}
              </span>
            </div>

            <div className="source-score">
              {(source.score * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sources;
interface MessageProps {
  role: "user" | "assistant";
  content: string;
}

function Message({ role, content }: MessageProps) {
  const isUser = role === "user";

  function renderContent() {
    if (isUser) {
      return content;
    }

    const parts = content.split(/(\[Source \d+\])/g);

    return parts.map((part, index) => {
      const match = part.match(/^\[Source (\d+)\]$/);

      if (!match) {
        return <span key={index}>{part}</span>;
      }

      return (
        <span
          key={index}
          className="citation"
        >
          {match[1]}
        </span>
      );
    });
  }

  return (
    <div
      className={`message-row ${
        isUser
          ? "user-message"
          : "assistant-message"
      }`}
    >
      {!isUser && (
        <div className="assistant-avatar">
          ✦
        </div>
      )}

      <div className="message-content">
        <span className="message-role">
          {isUser ? "You" : "AI Assistant"}
        </span>

        <div className="message-bubble">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default Message;
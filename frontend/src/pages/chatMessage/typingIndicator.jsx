function TypingIndicator() {
  return (
    <div className="message-row from-bot">
      <div className="message-avatar">
        <span className="message-avatar-letter">L</span>
      </div>
      <div className="typing-bubble">
        <span className="typing-dot" style={{ animationDelay: "0ms" }} />
        <span className="typing-dot" style={{ animationDelay: "150ms" }} />
        <span className="typing-dot" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}

export default TypingIndicator;
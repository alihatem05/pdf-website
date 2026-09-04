function ChatMessage({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`message-row ${isUser ? "from-user" : "from-bot"}`}>
      {!isUser && (
        <div className="message-avatar">
          <span className="message-avatar-letter">L</span>
        </div>
      )}
      <div className={`message-bubble ${isUser ? "bubble-user" : "bubble-bot"}`}>
        {text}
      </div>
    </div>
  );
}

export default ChatMessage;
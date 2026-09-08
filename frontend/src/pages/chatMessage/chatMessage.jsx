import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function ChatMessage({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`message-row ${isUser ? "from-user" : "from-bot"}`}>
      {!isUser && (
        <div className="message-avatar">
          <span className="message-avatar-letter">AI</span>
        </div>
      )}
      <div className={`message-bubble ${isUser ? "bubble-user" : "bubble-bot"}`}>
        {isUser ? text : <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>}
      </div>
    </div>
  );
}

export default ChatMessage;
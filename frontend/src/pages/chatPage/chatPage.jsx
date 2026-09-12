import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useGetChat, useSendMessage } from "../../hooks/useChat.js";
import { Send, Loader2, AlertCircle, FileText } from "lucide-react";
import ChatMessage from "../chatMessage/chatMessage.jsx";
import TypingIndicator from "../chatMessage/typingIndicator.jsx";
import "./chatPage.css";

function ChatPage() {
  const { chatId } = useParams();
  const [input, setInput] = useState("");
  const [pendingMessage, setPendingMessage] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const { data: chat, isLoading } = useGetChat(chatId);
  const { mutate: sendMessage, isPending } = useSendMessage();

  const messages = chat?.messages ?? [];
  const documents = chat?.documents ?? [];
  const isDocumentReady = documents.length > 0 && documents.every((document) => document.status === "ready");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending, pendingMessage]);

  function handleSend() {
    const text = input.trim();
    if (!text || isPending || !isDocumentReady) return;

    setPendingMessage(text);
    sendMessage(
      { chatId, content: text },
      { onSettled: () => setPendingMessage(null) }
    );
    setInput("");

    if (inputRef.current) {
      inputRef.current.style.height = "auto";
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleInput(e) {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  }

  if (isLoading) {
    return <div className="chat-page" />;
  }

  return (
    <div className="chat-page">
      <div className="chat-messages">
        {messages.length === 0 && !pendingMessage ? (
          <div className="chat-empty-state">
            <h1 className="chat-empty-title">Start a conversation</h1>
            <p className="chat-empty-subtitle">
              {isDocumentReady
                ? "Ask a question about your document to get started."
                : "DocAI will answer questions about it once it's ready."}
            </p>
          </div>
        ) : (
          <div className="chat-messages-inner">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} role={msg.role} text={msg.content} />
            ))}

            {pendingMessage && <ChatMessage role="user" text={pendingMessage} />}

            {isPending && <TypingIndicator />}

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="chat-input-bar">
        {documents.length > 0 && (
          <div className="chat-input-file-row">
            {documents.map((document) => (
              <div className="chat-file-chip" key={document.id}>
                {document.status === "processing" && <Loader2 size={14} strokeWidth={2} className="chat-status-spinner" />}
                {document.status === "failed" && <AlertCircle size={14} strokeWidth={2} className="chat-status-error" />}
                {document.status === "ready" && <FileText size={14} strokeWidth={1.8} />}
                <span className="chat-file-chip-name">
                  {document.status === "processing"
                    ? `Processing ${document.filename}...`
                    : document.status === "failed"
                      ? document.error_message || "Failed to process PDF"
                      : document.filename}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="chat-input-inner">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKey}
            placeholder={isDocumentReady ? "Message DocAI..." : "Waiting for PDF to finish processing..."}
            className="chat-textarea"
            disabled={!isDocumentReady}
          />

          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || isPending || !isDocumentReady}
            className="icon-btn-round icon-btn-send"
            aria-label="Send message"
          >
            <Send size={15} strokeWidth={1.8} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;
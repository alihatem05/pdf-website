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
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const { data: chat, isLoading } = useGetChat(chatId);
  const { mutate: sendMessage, isPending } = useSendMessage();

  const messages = chat?.messages ?? [];
  const documentStatus = chat?.document?.status;
  const isDocumentReady = documentStatus === "ready";

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending]);

  function handleSend() {
    const text = input.trim();
    if (!text || isPending || !isDocumentReady) return;

    sendMessage({ chatId, content: text });
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
        {messages.length === 0 ? (
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

            {isPending && <TypingIndicator />}

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="chat-input-bar">
        {chat?.document && (
          <div className="chat-input-file-row">
            <div className="chat-file-chip">
              {documentStatus === "processing" && (
                <>
                  <Loader2 size={14} strokeWidth={2} className="chat-status-spinner" />
                  <span className="chat-file-chip-name">Processing {chat.document.filename}...</span>
                </>
              )}
              {documentStatus === "failed" && (
                <>
                  <AlertCircle size={14} strokeWidth={2} className="chat-status-error" />
                  <span className="chat-file-chip-name">
                    {chat.document.error_message || "Failed to process PDF"}
                  </span>
                </>
              )}
              {documentStatus === "ready" && (
                <>
                  <FileText size={14} strokeWidth={1.8} />
                  <span className="chat-file-chip-name">{chat.document.filename}</span>
                </>
              )}
            </div>
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
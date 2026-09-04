import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useGetChat, useSendMessage } from "../../hooks/useChat.js";
import { Send, Plus } from "lucide-react";
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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending]);

  function handleSend() {
    const text = input.trim();
    if (!text || isPending) return;

    sendMessage({ chatId, content: text });
    setInput("");
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
        <div className="chat-messages-inner">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} role={msg.role} text={msg.content} />
          ))}

          {isPending && <TypingIndicator />}

          <div ref={bottomRef} />
        </div>
      </div>

      <div className="chat-input-bar">
        <div className="chat-input-inner">
          <button type="button" className="icon-btn-round" aria-label="Attach file">
            <Plus size={16} strokeWidth={1.8} />
          </button>

          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKey}
            placeholder="Message DocAI..."
            className="chat-textarea"
          />

          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || isPending}
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
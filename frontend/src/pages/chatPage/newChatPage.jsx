import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useSendMessage } from "../../hooks/useChat.js";
import { Send, Plus } from "lucide-react";
import "./chatPage.css";

function NewChatPage() {
  const [input, setInput] = useState("");
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { mutate: sendMessage, isPending } = useSendMessage();

  function handleSend() {
    const text = input.trim();
    if (!text || isPending) return;

    sendMessage(
			{ chatId: null, content: text },
			{
				onSuccess: (messages) => {
					navigate(`/main/chat/${messages[0].chat_id}`);
				},
			}
		);
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

  return (
    <div className="chat-page">
      <div className="chat-empty-state">
        <h1 className="chat-empty-title">Start a conversation</h1>
        <p className="chat-empty-subtitle">Ask DocAI anything to get started.</p>
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

export default NewChatPage;
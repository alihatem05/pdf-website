import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useCreateChatWithDocument } from "../../hooks/useChat.js";
import { Upload, Send, FileText, X } from "lucide-react";
import "./chatPage.css";

function NewChatPage() {
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const { mutate: createChatWithDocument, isPending } = useCreateChatWithDocument();

  const handleFileChange = (e) => {
    setFile(e.target.files[0] ?? null);
    e.target.value = "";
  };

  function handleChooseFile() {
    fileInputRef.current.click();
  }

  function handleRemoveFile() {
    setFile(null);
  }

  function handleSend() {
    if (!file || isPending) return;

    createChatWithDocument(file, {
      onSuccess: (chat) => {
        navigate(`/main/chat/${chat.id}`);
      },
    });
  }

  return (
    <div className="chat-page">
      <div className="chat-empty-state">
        <h1 className="chat-empty-title">Start a conversation</h1>
        <p className="chat-empty-subtitle">Upload a PDF to get started — DocAI will answer questions about it.</p>

        <input
          type="file"
          accept="application/pdf"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: "none" }}
        />

        {!file ? (
          <button type="button" className="upload-btn" onClick={handleChooseFile}>
            <Upload size={16} strokeWidth={1.8} />
            Upload PDF
          </button>
        ) : (
          <div className="upload-selected">
            <div className="chat-file-chip">
              <FileText size={14} strokeWidth={1.8} />
              <span className="chat-file-chip-name">{file.name}</span>
              <button
                type="button"
                className="chat-file-chip-remove"
                aria-label="Remove selected file"
                onClick={handleRemoveFile}
                disabled={isPending}
              >
                <X size={12} strokeWidth={2} />
              </button>
            </div>

            <button
              type="button"
              className="upload-send-btn"
              onClick={handleSend}
              disabled={isPending}
            >
              {isPending ? "Processing..." : (
                <>
                  Send <Send size={15} strokeWidth={1.8} />
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default NewChatPage;
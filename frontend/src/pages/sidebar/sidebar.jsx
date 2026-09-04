import { useAuthStore } from "../../stores/authStore";
import { useNavigate, useParams } from "react-router-dom";
import defaultAvatar from "../../assets/icons/person-circle.svg";
import { useGetChats } from "../../hooks/useChat";

import "./sidebar.css";

function Sidebar() {
  const { user, logout } = useAuthStore();
  const { data: chats } = useGetChats();
  const { chatId: activeId } = useParams();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="brand">Doclify</span>
      </div>

      <button
        type="button"
        className="btn btn-new-chat"
        onClick={() => navigate("/main/chat/new")}
      >
        New Chat
      </button>

      <hr />

      <div className="sidebar-scroll">
        <div className="chat-list">
          {chats?.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${
                chat.id === activeId ? "active" : ""
              }`}
              onClick={() => navigate(`/main/chat/${chat.id}`)}
            >
              <span className="chat-item-label">{chat.title}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="sidebar-footer">
        <img src={defaultAvatar} alt="" className="avatar"/>

        <div className="user-info">
          <p className="user-name">{user?.username}</p>
        </div>

        <div className="footer-dropdown">
          <button
            type="button"
            className="dropdown-item"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
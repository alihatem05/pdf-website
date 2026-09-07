import { useEffect, useRef, useState } from "react";
import { useAuthStore } from "../../stores/authStore";
import { useNavigate, useParams } from "react-router-dom";
import defaultAvatar from "../../assets/icons/person-circle.svg";
import dots from "../../assets/icons/three-dots-vertical.svg";
import { useGetChats, useDeleteChat } from "../../hooks/useChat";
import "./sidebar.css";

function Sidebar() {
  const { user, logout } = useAuthStore();
  const { data: chats, isLoading } = useGetChats();
	const deleteChat = useDeleteChat();
  const { chatId: activeId } = useParams();
  const navigate = useNavigate();
  const [openMenuId, setOpenMenuId] = useState(null);
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpenMenuId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleDelete = (e, chatId) => {
    e.stopPropagation();
    deleteChat.mutate(chatId, {
			onSuccess: () => {
				if (chatId === activeId) {
					navigate("/main/chat/new");
				}
			}
		})
  };

  const toggleMenu = (e, chatId) => {
    e.stopPropagation();
    setOpenMenuId((prev) => (prev === chatId ? null : chatId));
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
					{ isLoading && <span className="loading">Retrieving Chats...</span> }
          {chats?.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${
                chat.id === activeId ? "active" : ""
              }`}
              onClick={() => navigate(`/main/chat/${chat.id}`)}
            >
              <span className="chat-item-label">{chat.title}</span>
              <img
                src={dots}
                alt=""
                className="dots"
                onClick={(e) => toggleMenu(e, chat.id)}
              />
              <div
                ref={openMenuId === chat.id ? menuRef : null}
                className={`item-dropdown ${
                  openMenuId === chat.id ? "open" : ""
                }`}
              >
                <button
                  type="button"
                  className="dropdown-item-dots"
                  onClick={(e) => handleDelete(e, chat.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="sidebar-footer">
        <img src={defaultAvatar} alt="" className="avatar" />
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
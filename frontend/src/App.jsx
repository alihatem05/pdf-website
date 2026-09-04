import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./stores/authStore";
import LoginPage from "./pages/login/login";
import RegisterPage from "./pages/register/register";
import ChatPage from "./pages/chatPage/chatPage";
import NewChatPage from "./pages/chatPage/newChatPage";
import MainPage from "./pages/mainPage/mainPage.jsx";

export default function App() {
  const { isAuthenticated, isLoading } = useAuthStore();

  console.log("[DEBUG] isLoading:", isLoading, "isAuthenticated:", isAuthenticated, "path:", window.location.pathname);

  if (isLoading) {
    return null;
  }

  return (
    <Routes>
      <Route
        path="/"
        element={isAuthenticated ? <Navigate to="/main" replace /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/main" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/main" replace /> : <RegisterPage />}
      />
      <Route
        path="/main"
        element={isAuthenticated ? <MainPage /> : <Navigate to="/login" replace />}
      >
        <Route index element={<Navigate to="chat/new" replace />} />
        <Route path="chat/new" element={<NewChatPage />} />
        <Route path="chat/:chatId" element={<ChatPage />} />
      </Route>
    </Routes>
  );
}
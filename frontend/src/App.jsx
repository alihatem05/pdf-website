import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/login/login";
import RegisterPage from "./pages/register/register";
import DashboardPage from "./pages/dashboard/dashboard";

function AppContent() {
  const [page, setPage] = useState("login");
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <DashboardPage onNavigate={setPage} />;
  }

  return page === "login" ? (
    <LoginPage onNavigate={setPage} />
  ) : (
    <RegisterPage onNavigate={setPage} />
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

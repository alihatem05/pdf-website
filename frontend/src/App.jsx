import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/login/login";
import RegisterPage from "./pages/register/register";
import DashboardPage from "./pages/dashboard/dashboard";

export default function App() {
  const [page, setPage] = useState("login");
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return <DashboardPage onNavigate={setPage} />;
  }

  return page === "login" ? (
    <LoginPage onNavigate={setPage} />
  ) : (
    <RegisterPage onNavigate={setPage} />
  );
}
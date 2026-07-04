import { useState } from "react";
import LoginPage from "./pages/login/login";
import RegisterPage from "./pages/register/register";

export default function App() {
  const [page, setPage] = useState("login");

  return page === "login" ? (
    <LoginPage onNavigate={setPage} />
  ) : (
    <RegisterPage onNavigate={setPage} />
  );
}

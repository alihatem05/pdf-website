// context/AuthContext.jsx
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      try {
        const refreshRes = await api.post("/auth/refresh");
        const newToken = refreshRes.data.access_token;

        const meRes = await api.get("/users/me", {
          headers: { Authorization: `Bearer ${newToken}` },
        });

        setToken(newToken);
        setUser(meRes.data);
      } catch {
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    bootstrap();
  }, []);

  function login(newToken, newUser) {
    setToken(newToken);
    setUser(newUser);
  }

  async function logout() {
    try {
      await api.post("/auth/logout");
    } finally {
      setToken(null);
      setUser(null);
    }
  }

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      logout,
      setToken,
    }),
    [token, user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
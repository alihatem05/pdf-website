import React, { useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { setupInterceptors } from "./api/interceptors";

function InterceptorSetup({ children }) {
  const { token, setToken, logout } = useAuth();
  const tokenRef = useRef(token);

  useEffect(() => {
    tokenRef.current = token;
  }, [token]);

  useEffect(() => {
    setupInterceptors(
      () => tokenRef.current,
      (newToken) => {
        tokenRef.current = newToken;
        setToken(newToken);
      },
      logout
    );
  }, [setToken, logout]);

  return children;
}

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <BrowserRouter>
    <AuthProvider>
      <InterceptorSetup>
        <App />
      </InterceptorSetup>
    </AuthProvider>
  </BrowserRouter>
);
import React, { useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { useAuthStore } from "./stores/authStore";
import { setupInterceptors } from "./api/interceptors";
import { queryClient } from "./lib/queryClient";

function InterceptorSetup({ children }) {
  const { token, setToken } = useAuthStore();
  const tokenRef = useRef(token);

  useEffect(() => {
    tokenRef.current = token;
  }, [token]);

  useEffect(() => {
    setupInterceptors(() => tokenRef.current);
  }, []);

  return children;
}

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <InterceptorSetup>
        <App />
      </InterceptorSetup>
    </BrowserRouter>
  </QueryClientProvider>
);
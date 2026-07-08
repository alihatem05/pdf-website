import { useState, useCallback } from "react";
import { useAuth } from "../context/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api/auth";

function validateEmail(email) {
  const trimmed = email.trim();
  if (!trimmed) return "Email is required";
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmed)) return "Enter a valid email address";
  return null;
}

function validatePassword(password) {
  if (!password) return "Password is required";
  if (password.length < 5) return "Password must be at least 5 characters";
  return null;
}

export function useLogin() {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const submitLogin = useCallback(
    async (email, password) => {
      setError("");

      const emailError = validateEmail(email);
      const passwordError = validatePassword(password);
      if (emailError || passwordError) {
        setError(emailError || passwordError);
        return false;
      }

      setIsLoading(true);
      try {
        const res = await fetch(`${API_BASE}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim(), password }),
        });

        const data = await res.json();

        if (!res.ok) {
          setError(data.detail || "Something went wrong. Please try again.");
          return false;
        }

        login(data.access_token, data.user);
        return true;
      } catch (err) {
        setError("Unable to reach the server. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [login]
  );

  return { submitLogin, isLoading, error };
}

export function useRegister() {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const submitRegister = useCallback(
    async (username, email, password) => {
      setError("");

      const emailError = validateEmail(email);
      const passwordError = validatePassword(password);
      if (!username.trim()) {
        setError("Username is required");
        return false;
      }
      if (emailError || passwordError) {
        setError(emailError || passwordError);
        return false;
      }

      setIsLoading(true);
      try {
        const res = await fetch(`${API_BASE}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: username.trim(),
            email: email.trim(),
            password,
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          setError(data.detail || "Something went wrong. Please try again.");
          return false;
        }

        // Register auto-logs-in, same response shape as login
        login(data.access_token, data.user);
        return true;
      } catch (err) {
        setError("Unable to reach the server. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [login]
  );

  return { submitRegister, isLoading, error };
}
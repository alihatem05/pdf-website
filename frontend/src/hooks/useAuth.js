import { useState, useCallback } from "react";
import api from "../api/axios";
import { useAuth as useAuthContext } from "../context/AuthContext";

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
  const { login } = useAuthContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const submitLogin = useCallback(
    async (email, password, rememberMe) => {
      setError("");

      const emailError = validateEmail(email);
      const passwordError = validatePassword(password);
      if (emailError || passwordError) {
        setError(emailError || passwordError);
        return false;
      }

      setIsLoading(true);
      try {
        const res = await api.post("/auth/login", {
          email: email.trim(),
          password,
          remember_me: rememberMe,
        });

        login(res.data.access_token, res.data.user);
        return true;
      } catch (err) {
        setError(err.response?.data?.detail || "Something went wrong. Please try again.");
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
  const { login } = useAuthContext();
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
        const res = await api.post("/auth/register", {
          username: username.trim(),
          email: email.trim(),
          password,
        });

        login(res.data.access_token, res.data.user);
        return true;
      } catch (err) {
        setError(err.response?.data?.detail || "Something went wrong. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [login]
  );

  return { submitRegister, isLoading, error };
}
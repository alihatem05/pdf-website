import { useMutation } from "@tanstack/react-query";
import { useAuthStore } from "../stores/authStore";
import { authAPI } from "../api/auth";

export function useLoginMutation() {
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: authAPI.login,
    onSuccess: (data) => {
      login(data.access_token, data.user);
    },
  });
}

export function useRegisterMutation() {
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: authAPI.register,
    onSuccess: (data) => {
      login(data.access_token, data.user);
    },
  });
}
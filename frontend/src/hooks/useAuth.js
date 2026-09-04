import { useMutation } from "@tanstack/react-query";
import { useAuthStore } from "../stores/authStore";
import { loginAPI, registerAPI } from "../api/auth";

export function useLoginMutation() {
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: loginAPI,
    onSuccess: (data) => {
      login(data.access_token, data.user);
    },
  });
}

export function useRegisterMutation() {
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: registerAPI,
    onSuccess: (data) => {
      login(data.access_token, data.user);
    },
  });
}
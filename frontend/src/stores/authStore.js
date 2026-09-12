import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: true,

      setToken: (token) => set({ token }),
      setUser: (user) => set({ user }),

      login: (newToken, newUser) =>
        set({ token: newToken, user: newUser, isAuthenticated: true }),

      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: "auth-storage",
    }
  )
);

if (useAuthStore.persist.hasHydrated()) {
  useAuthStore.setState({ isLoading: false });
} else {
  useAuthStore.persist.onFinishHydration(() => {
    useAuthStore.setState({ isLoading: false });
  });
}
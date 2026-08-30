import { create } from "zustand";

export const useAuthStore = create((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  setToken: (token) =>
    set((state) => ({
      token,
    })),

  setUser: (user) =>
    set((state) => ({
      user,
    })),

  login: (newToken, newUser) =>
    set({
      token: newToken,
      user: newUser,
      isAuthenticated: true,
    }),

  logout: () =>
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    }),
}));

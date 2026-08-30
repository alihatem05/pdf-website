import api from "./axios";
import { LoginSchema, RegisterSchema, AuthResponseSchema } from "../schemas/auth";
import { getErrorMessage } from "../utils/errorHandler";

export const authAPI = {
  login: async (credentials) => {
    try {
      const validated = LoginSchema.parse(credentials);
      const response = await api.post("/auth/login", validated);
      return AuthResponseSchema.parse(response.data);
    } catch (error) {
      const message = getErrorMessage(error);
      const err = new Error(message);
      err.originalError = error;
      throw err;
    }
  },

  register: async (credentials) => {
    try {
      const validated = RegisterSchema.parse(credentials);
      const response = await api.post("/auth/register", validated);
      return AuthResponseSchema.parse(response.data);
    } catch (error) {
      const message = getErrorMessage(error);
      const err = new Error(message);
      err.originalError = error;
      throw err;
    }
  },
};

import api from "./axios";

export function setupInterceptors(getAccessToken) {
  api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });

  api.interceptors.response.use((response) => response, async (error) => {
    return Promise.reject(error);
  });
}
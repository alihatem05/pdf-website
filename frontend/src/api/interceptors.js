import api from "./axios";

export function setupInterceptors(getAccessToken, setAccessToken, logout) {
  api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const original = error.config;

      const isRefreshCall = original?.url?.includes("/auth/refresh");

      if (error.response?.status === 401 && !original._retry && !isRefreshCall) {
        original._retry = true;
        try {
          const res = await api.post("/auth/refresh");
          setAccessToken(res.data.access_token);
          original.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api(original);
        } catch {
          logout();
        }
      }

      return Promise.reject(error);
    }
  );
}
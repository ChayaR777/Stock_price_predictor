import axios from "axios";

export const API_BASE = "http://127.0.0.1:8000";

const api = axios.create({ baseURL: API_BASE });
api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem("auth_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
catch {
    // localStorage unavailable, continue without a token
  }
  return config;
});
export default api;

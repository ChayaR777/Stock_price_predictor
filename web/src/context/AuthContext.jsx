import { createContext, useContext, useState, useEffect } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);       // { email } or null
  const [checking, setChecking] = useState(true);
useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      setChecking(false);
      return;
    }
api.get("/auth/me")
      .then((res) => setUser({ email: res.data.email }))
      .catch(() => localStorage.removeItem("auth_token"))
      .finally(() => setChecking(false));
  }, []);
const handleAuthSuccess = (data) => {
    localStorage.setItem("auth_token", data.access_token);
    setUser({ email: data.email });
  };
const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    handleAuthSuccess(res.data);
  };
const signup = async (email, password) => {
    const res = await api.post("/auth/signup", { email, password });
    handleAuthSuccess(res.data);
  };
const logout = () => {
    localStorage.removeItem("auth_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, checking, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
export function useAuth() {
  return useContext(AuthContext);
}

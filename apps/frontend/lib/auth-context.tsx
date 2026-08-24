"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { auth } from "@/lib/api";

interface User {
  id: string;
  email: string;
  name: string;
  is_super_admin: boolean;
  company_id: string | null;
  role: string | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    auth
      .me()
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem("token");
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    await auth.login(email, password);
    const me = await auth.me();
    setUser(me);
  };

  const register = async (name: string, email: string, password: string) => {
    await auth.register(name, email, password);
    await login(email, password);
  };

  const logout = () => {
    auth.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

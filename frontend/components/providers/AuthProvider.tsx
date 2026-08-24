"use client";

import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import api from "@/lib/api";

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const { token, setUser, logout } = useAuth();

  useEffect(() => {
    if (!token) return;

    api
      .get("/users/me")
      .then((res) => setUser(res.data))
      .catch(() => {
        logout();
      });
  }, [token]);

  return <>{children}</>;
}
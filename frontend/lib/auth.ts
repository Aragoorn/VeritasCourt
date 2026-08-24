import { create } from "zustand";
import { persist } from "zustand/middleware";
import api from "./api";
import { User } from "@/types";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  loadUser: () => Promise<void>;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const res = await api.post("/auth/login", { email, password });
        const { access_token, user } = res.data;

        localStorage.setItem("veritas_token", access_token);
        set({ token: access_token, user, isAuthenticated: true });
      },

      register: async (email, password, name) => {
        await api.post("/auth/register", { email, password, name });
      },

      logout: () => {
        localStorage.removeItem("veritas_token");
        set({ user: null, token: null, isAuthenticated: false });
      },

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      loadUser: async () => {
        const token = get().token || localStorage.getItem("veritas_token");
        if (!token) return;

        try {
          const res = await api.get("/users/me");
          set({ user: res.data, token, isAuthenticated: true });
        } catch {
          get().logout();
        }
      },
    }),
    {
      name: "veritas-auth",
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
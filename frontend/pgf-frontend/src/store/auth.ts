// frontend/pgf-frontend/src/store/auth.ts
"use client";

import { create } from "zustand";
import { ROLE_ACCESS, Rol } from "@/lib/constants";

export type UserSession = {
  id: string;
  username: string;
  email?: string;
  rol: Rol;
};

type AuthState = {
  user: UserSession | null;
  setUser: (u: UserSession | null) => void;
  allowed: (section: string) => boolean;
  hasRole: (roles: Rol | Rol[]) => boolean;
  isLogged: () => boolean;
  refreshMe: () => Promise<void>;
};

export const useAuth = create<AuthState>((set, get) => ({
  user: null,

  setUser: (u) => set({ user: u }),

  allowed: (section) => {
    const user = get().user;
    if (!user) return false;
    return ROLE_ACCESS[user.rol]?.includes(section) ?? false;
  },

  hasRole: (roles) => {
    const rlist = Array.isArray(roles) ? roles : [roles];
    const u = get().user;
    return !!u && rlist.includes(u.rol);
  },

  isLogged: () => {
    const u = get().user;
    return !!u;          // si hay usuario, está logueado
  },

  refreshMe: async () => {
    try {
      const res = await fetch("/api/auth/me", { credentials: "include" });
      if (!res.ok) throw new Error();
      const data = await res.json();
      set({ user: data });
    } catch {
      set({ user: null });
    }
  },
}));

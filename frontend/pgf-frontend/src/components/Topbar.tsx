"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/store/auth";
import NotificationBell from "@/components/NotificationBell";

export default function Topbar() {
  const [user, setUser] = useState<any>(null);
  const router = useRouter();
  const { setUser: setAuthUser } = useAuth();

  useEffect(() => {
    const loadUser = async () => {
      try {
        const res = await fetch("/api/auth/me", { credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
          setAuthUser(data);
        }
      } catch (err) {
        console.error("Error loading user:", err);
      }
    };
    loadUser();
  }, [setAuthUser]);

  async function logout() {
    try {
      await fetch("/api/auth/logout", { 
        method: "POST",
        credentials: "include"
      });
      setAuthUser(null);
      router.push("/auth/login");
    } catch (error) {
      console.error("Error al cerrar sesión:", error);
      // Forzar redirección incluso si hay error
      setAuthUser(null);
      router.push("/auth/login");
    }
  }

  return (
    <header className="h-16 bg-white dark:bg-gray-800 shadow flex items-center justify-between px-6 border-b border-gray-200 dark:border-gray-700">
      <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
        Panel de Administración
      </h1>

      <div className="flex items-center gap-4">
        {/* Componente de notificaciones */}
        {user && <NotificationBell />}
        
        {user && (
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user.first_name} {user.last_name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user.rol}
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
              {user.first_name?.[0]}{user.last_name?.[0]}
            </div>
          </div>
        )}

        {user && (
          <>
            <a
              href="/profile/preferences"
              className="px-3 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors duration-200 text-sm font-medium"
            >
              Preferencias
            </a>
            <a
              href="/profile/change-password"
              className="px-3 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors duration-200 text-sm font-medium"
            >
              Cambiar Contraseña
            </a>
          </>
        )}

        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200 text-sm font-medium shadow-sm hover:shadow"
        >
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}


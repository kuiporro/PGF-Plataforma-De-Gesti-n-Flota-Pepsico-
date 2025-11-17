"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/store/auth";

export default function LoginPage() {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [loading, setL] = useState(false);
  const [error, setE] = useState<string | null>(null);

  const router = useRouter();
  const sp = useSearchParams();
  const next = sp.get("next") || "/dashboard";
  const { setUser } = useAuth();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setL(true);
    setE(null);

    try {
      // 🔥 Login normal
      const loginRes = await fetch("/api/auth/login", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ username, password }),
        headers: { "Content-Type": "application/json" },
      });

      if (!loginRes.ok) {
        const errorData = await loginRes.json().catch(() => ({ detail: "Credenciales inválidas" }));
        throw new Error(errorData.detail || "Credenciales inválidas");
      }

      // 🔥 Cargar el usuario con el token httpOnly vía API
      const meRes = await fetch("/api/auth/me", {
        credentials: "include",
      });

      if (!meRes.ok) throw new Error("Error cargando perfil");

      const text = await meRes.text();
      if (!text || text.trim() === "") {
        throw new Error("Respuesta vacía del servidor");
      }

      let user;
      try {
        user = JSON.parse(text);
      } catch (e) {
        console.error("Invalid JSON response:", text);
        throw new Error("Error procesando respuesta del servidor");
      }

      setUser(user);

      // Redirigir según el rol del usuario
      if (["ADMIN", "SPONSOR", "EJECUTIVO"].includes(user.rol)) {
        router.replace("/dashboard/ejecutivo");
      } else if (user.rol === "SUPERVISOR" || user.rol === "JEFE_TALLER" || user.rol === "COORDINADOR_ZONA") {
        router.replace("/workorders");
      } else if (user.rol === "MECANICO") {
        router.replace("/workorders");
      } else if (user.rol === "GUARDIA" || user.rol === "RECEPCIONISTA") {
        router.replace("/vehicles");
      } else if (user.rol === "CHOFER") {
        router.replace("/vehicles");
      } else {
        // Rol desconocido, redirigir a vehicles por defecto
        router.replace("/vehicles");
      }

    } catch (err: any) {
      setE(err.message || "Error al iniciar sesión");
    } finally {
      setL(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-800 shadow-2xl rounded-2xl p-8 space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              PGF
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Plataforma de Gestión de Flota
            </p>
          </div>

          {/* Form */}
          <form onSubmit={onSubmit} className="space-y-5">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Usuario
              </label>
              <input
                id="username"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                placeholder="Ingresa tu usuario"
                value={username}
                onChange={(e) => setU(e.target.value)}
                required
                autoComplete="username"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Contraseña
              </label>
              <input
                id="password"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                type="password"
                placeholder="Ingresa tu contraseña"
                value={password}
                onChange={(e) => setP(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Iniciando sesión...
                </span>
              ) : (
                "Iniciar Sesión"
              )}
            </button>
          </form>

          {/* Link a recuperación */}
          <div className="text-center mt-4">
            <a
              href="/auth/reset-password"
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              ¿Olvidaste tu contraseña?
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

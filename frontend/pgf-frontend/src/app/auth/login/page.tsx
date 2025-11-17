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
        const errorText = await loginRes.text().catch(() => 'Credenciales inválidas');
        throw new Error(errorText || "Credenciales inválidas");
      }

      // 🔥 Cargar el usuario con el token httpOnly vía proxy
      const meRes = await fetch("/api/proxy/auth/me/", {
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

      router.replace(next);

    } catch (err: any) {
      setE(err.message);
    } finally {
      setL(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <form onSubmit={onSubmit} className="max-w-sm w-full space-y-4 border p-6 rounded-xl">
        <h1 className="text-2xl font-semibold">Ingresar</h1>

        <input
          className="w-full border rounded p-2"
          placeholder="Usuario"
          value={username}
          onChange={(e) => setU(e.target.value)}
        />

        <input
          className="w-full border rounded p-2"
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setP(e.target.value)}
        />

        <button disabled={loading} className="w-full rounded bg-black text-white py-2 disabled:opacity-50">
          {loading ? "Entrando..." : "Entrar"}
        </button>

        {error && <p className="text-red-600 text-sm">{error}</p>}
      </form>
    </div>
  );
}

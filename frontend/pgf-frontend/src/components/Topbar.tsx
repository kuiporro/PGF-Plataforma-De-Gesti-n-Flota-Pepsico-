"use client";

import { useEffect, useState } from "react";

export default function Topbar() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    fetch("/api/proxy/users/me")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => setUser(data));
  }, []);

  function logout() {
    document.cookie = "pgf_token=; Max-Age=0; path=/";
    location.href = "/";
  }

  return (
    <header className="h-16 bg-white shadow flex items-center justify-between px-6 border-b">
      <h1 className="text-xl font-semibold">Panel de Administración</h1>

      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-gray-600">
            {user.first_name} {user.last_name} ({user.rol})
          </span>
        )}

        <button
          onClick={logout}
          className="btn btn-danger px-3 py-1"
        >
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}

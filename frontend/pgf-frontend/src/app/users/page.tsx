"use client";

import { useEffect, useState } from "react";

export default function UsersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const r = await fetch("/api/proxy/users/");
        const j = await r.json();
        setRows(j.results ?? []);
      } catch (e) {
        console.error("Error al cargar usuarios", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Usuarios</h1>

      {loading && <p className="text-gray-500">Cargando...</p>}
      {!loading && rows.length === 0 && <p className="text-gray-500">No hay usuarios registrados.</p>}

      {!loading && rows.length > 0 && (
        <div className="overflow-x-auto border rounded-lg">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="p-3">ID</th>
                <th className="p-3">Nombre</th>
                <th className="p-3">Usuario</th>
                <th className="p-3">Email</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((u) => (
                <tr key={u.id} className="border-b hover:bg-gray-50 transition">
                  <td className="p-3">{u.id}</td>
                  <td className="p-3">{u.first_name} {u.last_name}</td>
                  <td className="p-3">{u.username}</td>
                  <td className="p-3">{u.email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import RoleGuard from "@/components/RoleGuard";
import Pagination from "@/components/Pagination";

export default function UsersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;

  useEffect(() => {
    async function load(page: number = 1) {
      try {
        const r = await fetch(`/api/proxy/users/?page=${page}&page_size=${itemsPerPage}`, {
          credentials: "include",
        });
        
        if (!r.ok) {
          if (r.status === 401) {
            console.warn("No autorizado para ver usuarios");
            setRows([]);
            return;
          }
          throw new Error(`HTTP ${r.status}`);
        }
        
        const text = await r.text();
        if (!text || text.trim() === "") {
          setRows([]);
          return;
        }
        
        const j = JSON.parse(text);
        setRows(j.results ?? j ?? []);
        setTotalPages(Math.ceil((j.count || j.results?.length || 0) / itemsPerPage));
        setTotalItems(j.count || j.results?.length || 0);
      } catch (e) {
        console.error("Error al cargar usuarios", e);
        setRows([]);
      } finally {
        setLoading(false);
      }
    }

    load(currentPage);
  }, [currentPage]);

  return (
    <RoleGuard allow={["ADMIN", "SUPERVISOR"]}>
      <div className="p-8 max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Usuarios</h1>
          <Link
            href="/users/create"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
          >
            + Nuevo Usuario
          </Link>
        </div>

      {loading && <p className="text-gray-500">Cargando...</p>}
      {!loading && rows.length === 0 && <p className="text-gray-500">No hay usuarios registrados.</p>}

      {!loading && rows.length > 0 && (
        <div className="overflow-x-auto border rounded-lg">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-gray-100 dark:bg-gray-700 border-b">
              <tr>
                <th className="p-3 text-left">ID</th>
                <th className="p-3 text-left">Nombre</th>
                <th className="p-3 text-left">Usuario</th>
                <th className="p-3 text-left">Email</th>
                <th className="p-3 text-left">RUT</th>
                <th className="p-3 text-left">Rol</th>
                <th className="p-3 text-left">Acciones</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((u) => (
                <tr key={u.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-700 transition">
                  <td className="p-3">{u.id}</td>
                  <td className="p-3">{u.first_name} {u.last_name}</td>
                  <td className="p-3">{u.username}</td>
                  <td className="p-3">{u.email}</td>
                  <td className="p-3">{u.rut || "-"}</td>
                  <td className="p-3">
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded text-xs font-medium">
                      {u.rol}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <Link
                        href={`/users/${u.id}/edit`}
                        className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                      >
                        Editar
                      </Link>
                      <Link
                        href={`/users/${u.id}/delete`}
                        className="text-red-600 dark:text-red-400 hover:underline text-sm"
                      >
                        Eliminar
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={totalItems}
            itemsPerPage={itemsPerPage}
          />
        </div>
      )}
      </div>
    </RoleGuard>
  );
}

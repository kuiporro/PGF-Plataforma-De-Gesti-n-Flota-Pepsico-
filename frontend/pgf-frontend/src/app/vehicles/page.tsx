"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import Pagination from "@/components/Pagination";

export default function VehiclesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;
  const toast = useToast();
  const { hasRole } = useAuth();

  async function load(page: number = 1) {
    try {
      const r = await fetch(`/api/proxy/vehicles/?page=${page}&page_size=${itemsPerPage}`, {
        credentials: "include",
      });
      
      if (!r.ok) {
        if (r.status === 401) {
          console.warn("No autorizado para ver vehículos");
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
      console.error("Error cargando vehículos", e);
      toast.error("Error al cargar vehículos");
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(currentPage);
  }, [currentPage]);

  const canEdit = hasRole(["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA"]);
  const isGuardia = hasRole(["GUARDIA"]);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Vehículos</h1>
        <div className="flex gap-3">
          {isGuardia && (
            <Link 
              href="/vehicles/ingreso" 
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium shadow-sm hover:shadow"
            >
              📥 Registrar Ingreso
            </Link>
          )}
          {canEdit && (
            <Link 
              href="/vehicles/create" 
              className="px-4 py-2 text-white rounded-lg transition-colors font-medium shadow-sm hover:shadow"
              style={{ backgroundColor: '#003DA5' }}
            >
              + Nuevo Vehículo
            </Link>
          )}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Patente</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Marca</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Modelo</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Año</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Estado</th>
              <th className="p-3 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">Acciones</th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="p-8 text-center">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando...</span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-gray-500 dark:text-gray-400">
                  No hay vehículos registrados.
                </td>
              </tr>
            ) : (
              rows.map((v) => (
                <tr key={v.id} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="p-3 font-medium text-gray-900 dark:text-white">{v.patente}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{v.marca}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{v.modelo}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{v.anio}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      v.estado === "ACTIVO" 
                        ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300"
                    }`}>
                      {v.estado || "ACTIVO"}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center justify-end gap-2">
                      <Link 
                        href={`/vehicles/${v.id}`} 
                        className="px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        Ver
                      </Link>
                      {canEdit && (
                        <>
                          <Link 
                            href={`/vehicles/${v.id}/edit`} 
                            className="px-3 py-1 text-sm text-green-600 dark:text-green-400 hover:underline"
                          >
                            Editar
                          </Link>
                          <Link 
                            href={`/vehicles/${v.id}/delete`} 
                            className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:underline"
                          >
                            Eliminar
                          </Link>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
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
    </div>
  );
}

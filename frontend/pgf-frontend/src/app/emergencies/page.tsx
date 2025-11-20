"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";

export default function EmergenciesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 20;
  const toast = useToast();
  const { hasRole } = useAuth();

  async function load(page: number = 1) {
    try {
      const r = await fetch(`/api/proxy/emergencies/?page=${page}&page_size=${itemsPerPage}`, {
        credentials: "include",
      });
      
      if (!r.ok) {
        if (r.status === 401) {
          console.warn("No autorizado para ver emergencias");
          setRows([]);
          return;
        }
        
        // Intentar obtener el mensaje de error del backend
        const errorText = await r.text().catch(() => "");
        let errorMessage = `Error HTTP ${r.status}`;
        
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          if (errorText) {
            errorMessage = errorText;
          }
        }
        
        console.error("Error al cargar emergencias:", {
          status: r.status,
          statusText: r.statusText,
          error: errorMessage,
        });
        
        toast.error(errorMessage || `Error al cargar emergencias (HTTP ${r.status})`);
        setRows([]);
        return;
      }
      
      const text = await r.text();
      if (!text || text.trim() === "") {
        setRows([]);
        return;
      }
      
      const j = JSON.parse(text);
      setRows(j.results ?? j ?? []);
      setTotalPages(Math.ceil((j.count || j.results?.length || 0) / itemsPerPage));
    } catch (e: any) {
      console.error("Error cargando emergencias", e);
      toast.error(e.message || "Error al cargar emergencias");
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(currentPage);
  }, [currentPage]);

  const canEdit = hasRole(["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA", "JEFE_TALLER"]);

  const getEstadoColor = (estado: string) => {
    const colors: Record<string, string> = {
      SOLICITADA: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
      APROBADA: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
      ASIGNADA: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      EN_CAMINO: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
      EN_REPARACION: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
      RESUELTA: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
      CERRADA: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
      RECHAZADA: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    };
    return colors[estado] || "bg-gray-100 text-gray-800";
  };

  const getPrioridadColor = (prioridad: string) => {
    const colors: Record<string, string> = {
      CRITICA: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      ALTA: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
      MEDIA: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
      BAJA: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    };
    return colors[prioridad] || "bg-gray-100 text-gray-800";
  };

  return (
    <RoleGuard allow={["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA", "JEFE_TALLER"]}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Emergencias en Ruta</h1>
          {canEdit && (
            <Link 
              href="/emergencies/create" 
              className="px-4 py-2 text-white rounded-lg transition-colors font-medium shadow-sm hover:shadow"
              style={{ backgroundColor: '#003DA5' }}
            >
              + Nueva Emergencia
            </Link>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-100 dark:bg-gray-700">
              <tr>
                <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Vehículo</th>
                <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Descripción</th>
                <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Ubicación</th>
                <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Prioridad</th>
                <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Estado</th>
                <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Fecha</th>
                <th className="p-3 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">Acciones</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-gray-500">
                    Cargando emergencias...
                  </td>
                </tr>
              ) : rows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-gray-500">
                    No hay emergencias registradas
                  </td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.id} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                      {row.vehiculo_patente || "N/A"}
                    </td>
                    <td className="p-3 text-sm text-gray-900 dark:text-gray-100 max-w-xs truncate">
                      {row.descripcion || "N/A"}
                    </td>
                    <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                      {row.ubicacion || "N/A"}
                    </td>
                    <td className="p-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPrioridadColor(row.prioridad)}`}>
                        {row.prioridad || "N/A"}
                      </span>
                    </td>
                    <td className="p-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEstadoColor(row.estado)}`}>
                        {row.estado || "N/A"}
                      </span>
                    </td>
                    <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                      {row.fecha_solicitud ? new Date(row.fecha_solicitud).toLocaleString('es-CL') : "N/A"}
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex justify-end gap-2">
                        <Link
                          href={`/emergencies/${row.id}`}
                          className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded transition-colors"
                        >
                          Ver
                        </Link>
                        {canEdit && (
                          <Link
                            href={`/emergencies/${row.id}`}
                            className="px-3 py-1 text-sm text-white rounded transition-colors"
                            style={{ backgroundColor: '#003DA5' }}
                          >
                            Gestionar
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-700 dark:text-gray-300">
                Página {currentPage} de {totalPages}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </RoleGuard>
  );
}


"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import Pagination from "@/components/Pagination";

export default function WorkOrdersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [estado, setEstado] = useState("ABIERTA");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;
  const toast = useToast();
  const { hasRole } = useAuth();

  const load = async (page: number = 1) => {
    setLoading(true);

    const url = estado
      ? `/api/proxy/work/ordenes/?estado=${estado}&page=${page}&page_size=${itemsPerPage}`
      : `/api/proxy/work/ordenes/?page=${page}&page_size=${itemsPerPage}`;

    try {
      const r = await fetch(url, { credentials: "include" });
      
      if (!r.ok) {
        if (r.status === 401) {
          console.warn("No autorizado para ver órdenes de trabajo");
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
      const data = j.results ?? j ?? [];
      setRows(Array.isArray(data) ? data : []);
      setTotalPages(Math.ceil((j.count || data.length) / itemsPerPage));
      setTotalItems(j.count || data.length);
    } catch (e) {
      console.error("Error cargando OT:", e);
      toast.error("Error al cargar órdenes de trabajo");
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    load(1);
  }, [estado]);

  useEffect(() => {
    load(currentPage);
  }, [currentPage]);

  const canEdit = hasRole(["ADMIN", "SUPERVISOR"]);

  const getEstadoColor = (estado: string) => {
    const colors: Record<string, string> = {
      ABIERTA: "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400",
      EN_EJECUCION: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400",
      EN_QA: "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400",
      CERRADA: "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400",
    };
    return colors[estado] || "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300";
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Órdenes de Trabajo</h1>
        {canEdit && (
          <Link 
            href="/workorders/create" 
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium shadow-sm hover:shadow"
          >
            + Nueva Orden
          </Link>
        )}
      </div>

      <div className="flex gap-3 mb-6 flex-wrap">
        {["ABIERTA", "EN_EJECUCION", "EN_QA", "CERRADA", "TODAS"].map((e) => (
          <button
            key={e}
            onClick={() => setEstado(e === "TODAS" ? "" : e)}
            className={`px-4 py-2 rounded-lg transition-colors font-medium ${
              estado === e || (estado === "" && e === "TODAS")
                ? "bg-blue-600 text-white"
                : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
            }`}
          >
            {e}
          </button>
        ))}
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">ID</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Patente</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Estado</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Tipo</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Responsable</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Apertura</th>
              <th className="p-3 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">Acciones</th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="p-8 text-center">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando...</span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-gray-500 dark:text-gray-400">
                  No hay órdenes de trabajo registradas.
                </td>
              </tr>
            ) : (
              rows.map((ot) => (
                <tr key={ot.id} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="p-3 font-medium text-gray-900 dark:text-white">#{ot.id}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{ot.vehiculo?.patente || "N/A"}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getEstadoColor(ot.estado)}`}>
                      {ot.estado}
                    </span>
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{ot.tipo || "N/A"}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {ot.responsable ? `${ot.responsable.first_name} ${ot.responsable.last_name}` : "Sin responsable"}
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {new Date(ot.apertura).toLocaleDateString()}
                  </td>
                  <td className="p-3">
                    <div className="flex items-center justify-end gap-2">
                      <Link 
                        href={`/workorders/${ot.id}`} 
                        className="px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        Ver
                      </Link>
                      {canEdit && (
                        <>
                          <Link 
                            href={`/workorders/${ot.id}/edit`} 
                            className="px-3 py-1 text-sm text-green-600 dark:text-green-400 hover:underline"
                          >
                            Editar
                          </Link>
                          {ot.estado === "ABIERTA" && (
                            <Link 
                              href={`/workorders/${ot.id}/delete`} 
                              className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:underline"
                            >
                              Eliminar
                            </Link>
                          )}
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

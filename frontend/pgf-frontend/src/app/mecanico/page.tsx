"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";
import Link from "next/link";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";

/**
 * Vista principal para Mecánico/Técnico.
 * 
 * Muestra:
 * - Mis OTs asignadas
 * - Filtros por estado (Asignadas, En ejecución, En pausa, Finalizadas)
 * - Tarjetas de OT con información clave
 * - Acceso rápido a acciones
 * 
 * Permisos:
 * - Solo MECANICO puede acceder
 */
export default function MecanicoPage() {
  const router = useRouter();
  const toast = useToast();
  const { user } = useAuth();

  const [ots, setOts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>("");

  useEffect(() => {
    cargarOTs();
  }, [filtroEstado]);

  const cargarOTs = async () => {
    setLoading(true);
    try {
      let url = `${ENDPOINTS.WORK_ORDERS}?mecanico=${user?.id || ""}`;
      if (filtroEstado) {
        url += `&estado=${filtroEstado}`;
      }

      const response = await fetch(url, {
        method: "GET",
        ...withSession(),
      });

      if (!response.ok) {
        throw new Error("Error al cargar OTs");
      }

      const data = await response.json();
      setOts(data.results || data || []);
    } catch (error) {
      console.error("Error al cargar OTs:", error);
      toast.error("Error al cargar órdenes de trabajo");
    } finally {
      setLoading(false);
    }
  };

  const estados = [
    { value: "", label: "Todas" },
    { value: "ABIERTA", label: "Asignadas" },
    { value: "EN_EJECUCION", label: "En Ejecución" },
    { value: "EN_PAUSA", label: "En Pausa" },
    { value: "CERRADA", label: "Finalizadas" },
  ];

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case "ABIERTA":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300";
      case "EN_EJECUCION":
        return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300";
      case "EN_PAUSA":
        return "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300";
      case "EN_QA":
        return "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300";
      case "CERRADA":
        return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300";
    }
  };

  const getPrioridadColor = (prioridad: string) => {
    switch (prioridad) {
      case "ALTA":
        return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300";
      case "MEDIA":
        return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300";
      case "BAJA":
        return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300";
    }
  };

  return (
    <RoleGuard allow={["MECANICO"]}>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Mis Órdenes de Trabajo
          </h1>
        </div>

        {/* Filtros */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex gap-4 items-center">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Filtrar por estado:
            </label>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {estados.map((estado) => (
                <option key={estado.value} value={estado.value}>
                  {estado.label}
                </option>
              ))}
            </select>
            <button
              onClick={cargarOTs}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Actualizar
            </button>
          </div>
        </div>

        {/* Lista de OTs */}
        {loading ? (
          <div className="p-6 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando OTs...</p>
          </div>
        ) : ots.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
            <p className="text-gray-500 dark:text-gray-400">
              No tienes órdenes de trabajo {filtroEstado ? `en estado ${filtroEstado}` : "asignadas"}.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ots.map((ot) => (
              <div
                key={ot.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      OT #{ot.id.slice(0, 8)}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {ot.vehiculo_patente || ot.vehiculo?.patente}
                    </p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getEstadoColor(ot.estado)}`}>
                    {ot.estado}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Tipo:</span>
                    <span className="text-gray-900 dark:text-white font-medium">{ot.tipo || "N/A"}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Prioridad:</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getPrioridadColor(ot.prioridad)}`}>
                      {ot.prioridad || "MEDIA"}
                    </span>
                  </div>
                  {ot.motivo && (
                    <div className="text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Motivo: </span>
                      <span className="text-gray-900 dark:text-white">
                        {ot.motivo.length > 50 ? `${ot.motivo.substring(0, 50)}...` : ot.motivo}
                      </span>
                    </div>
                  )}
                  {ot.fecha_apertura && (
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Creada: {new Date(ot.fecha_apertura).toLocaleDateString()}
                    </div>
                  )}
                </div>

                <div className="flex gap-2 mt-4">
                  <Link
                    href={`/mecanico/ot/${ot.id}`}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium text-center"
                  >
                    Abrir OT
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </RoleGuard>
  );
}


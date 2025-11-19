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
 * Dashboard del Taller para Jefe de Taller.
 * 
 * Muestra:
 * - KPIs: OTs abiertas, Mecánicos activos, Promedio de ejecución, OTs atrasadas
 * - Gráfico de carga por mecánico
 * - Tabla de OTs del día
 * 
 * Permisos:
 * - Solo JEFE_TALLER puede acceder
 */
export default function JefeTallerDashboardPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [kpis, setKpis] = useState<any>({});
  const [otsHoy, setOtsHoy] = useState<any[]>([]);
  const [mecanicosCarga, setMecanicosCarga] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Cargar dashboard ejecutivo (tiene los KPIs que necesitamos)
      const dashboardResponse = await fetch("/api/proxy/reports/dashboard-ejecutivo/", {
        method: "GET",
        ...withSession(),
      });

      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json();
        setKpis(dashboardData.kpis || {});
        setMecanicosCarga(dashboardData.mecanicos_carga || []);
      }

      // Cargar OTs del día
      const hoy = new Date().toISOString().split("T")[0];
      const otsResponse = await fetch(`${ENDPOINTS.WORK_ORDERS}?apertura__date=${hoy}`, {
        method: "GET",
        ...withSession(),
      });

      if (otsResponse.ok) {
        const otsData = await otsResponse.json();
        setOtsHoy(otsData.results || otsData || []);
      }
    } catch (error) {
      console.error("Error al cargar datos:", error);
      toast.error("Error al cargar información del dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <RoleGuard allow={["JEFE_TALLER", "ADMIN"]}>
        <div className="p-6 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando dashboard...</p>
          </div>
        </div>
      </RoleGuard>
    );
  }

  return (
    <RoleGuard allow={["JEFE_TALLER", "ADMIN"]}>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard del Taller
          </h1>
          <div className="flex gap-2">
            <Link
              href="/workorders/create"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Crear OT
            </Link>
            <Link
              href="/jefe-taller/gestor"
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Gestor de OTs
            </Link>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              OTs Abiertas
            </h3>
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {kpis.ot_abiertas || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              OTs en Ejecución
            </h3>
            <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
              {kpis.ot_en_ejecucion || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              OTs en Pausa
            </h3>
            <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
              {kpis.ot_en_pausa || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              OTs Cerradas Hoy
            </h3>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              {kpis.ot_cerradas_hoy || 0}
            </p>
          </div>
        </div>

        {/* Gráfico de Carga por Mecánico */}
        {mecanicosCarga.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Carga de Trabajo por Mecánico
            </h2>
            <div className="space-y-3">
              {mecanicosCarga.map((mecanico: any) => (
                <div key={mecanico.id || mecanico.mecanico_id}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {mecanico.mecanico_nombre || "N/A"}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {mecanico.total_ots || 0} OTs
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${Math.min((mecanico.total_ots || 0) * 10, 100)}%`,
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tabla de OTs del Día */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              OTs del Día
            </h2>
          </div>
          <div className="overflow-x-auto">
            {otsHoy.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      OT
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Patente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Mecánico
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Prioridad
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {otsHoy.map((ot) => (
                    <tr key={ot.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        #{ot.id.slice(0, 8)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {ot.vehiculo_patente || ot.vehiculo?.patente}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded ${
                            ot.estado === "ABIERTA"
                              ? "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                              : ot.estado === "EN_EJECUCION"
                              ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300"
                              : "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300"
                          }`}
                        >
                          {ot.estado}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {ot.mecanico_nombre || "Sin asignar"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {ot.prioridad || "MEDIA"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link
                          href={`/workorders/${ot.id}`}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                        >
                          Ver
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                No hay OTs creadas hoy.
              </div>
            )}
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


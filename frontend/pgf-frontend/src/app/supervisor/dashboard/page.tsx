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
 * Dashboard de Zona para Supervisor Zonal.
 * 
 * Muestra:
 * - Ranking de productividad
 * - Gráfico de cumplimiento SLA
 * - Indicador de vehículos fuera de servicio
 * - Mapa de talleres (opcional)
 * 
 * Permisos:
 * - Solo SUPERVISOR puede acceder
 */
export default function SupervisorDashboardPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole, user } = useAuth();

  const [kpis, setKpis] = useState<any>({});
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
      <RoleGuard allow={["SUPERVISOR", "ADMIN"]}>
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
    <RoleGuard allow={["SUPERVISOR", "ADMIN"]}>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard de Zona
          </h1>
          <div className="flex gap-2">
            <Link
              href="/supervisor/analizador"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Analizador de OTs
            </Link>
            <Link
              href="/supervisor/reportes"
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Reportes
            </Link>
          </div>
        </div>

        {/* KPIs Principales */}
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
              Cumplimiento SLA
            </h3>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              {kpis.sla_cumplimiento || "N/A"}%
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Productividad (7 días)
            </h3>
            <p className="text-3xl font-bold text-teal-600 dark:text-teal-400">
              {kpis.productividad_7_dias || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Vehículos en Taller
            </h3>
            <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {kpis.vehiculos_en_taller || 0}
            </p>
          </div>
        </div>

        {/* Ranking de Productividad */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Ranking de Productividad por Taller
          </h2>
          <div className="text-gray-500 dark:text-gray-400">
            <p>Funcionalidad en desarrollo. Mostrará comparativa entre talleres de la zona.</p>
          </div>
        </div>

        {/* Cumplimiento SLA */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Cumplimiento SLA
          </h2>
          <div className="text-gray-500 dark:text-gray-400">
            <p>Gráfico de cumplimiento SLA por taller (en desarrollo).</p>
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


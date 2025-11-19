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
 * Dashboard de Auditoría para Auditor Interno.
 * 
 * Muestra:
 * - Últimos cambios críticos
 * - Actividad por usuario
 * - Evidencias marcadas como inválidas
 * 
 * Permisos:
 * - Solo ADMIN puede acceder (Auditor usa rol ADMIN con permisos de solo lectura)
 */
export default function AuditorDashboardPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [actividad, setActividad] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarActividad();
  }, []);

  const cargarActividad = async () => {
    setLoading(true);
    try {
      // Cargar actividad reciente desde auditoría
      // Nota: Esto requiere un endpoint de auditoría
      // Por ahora, mostramos un placeholder
      setActividad([]);
    } catch (error) {
      console.error("Error al cargar actividad:", error);
      toast.error("Error al cargar información de auditoría");
    } finally {
      setLoading(false);
    }
  };

  return (
    <RoleGuard allow={["ADMIN"]}>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard de Auditoría
          </h1>
          <div className="flex gap-2">
            <Link
              href="/auditor/logs"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Ver Logs
            </Link>
          </div>
        </div>

        {/* Últimos Cambios Críticos */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Últimos Cambios Críticos
          </h2>
          <div className="text-gray-500 dark:text-gray-400">
            <p>Lista de cambios críticos en el sistema (en desarrollo).</p>
          </div>
        </div>

        {/* Actividad por Usuario */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Actividad por Usuario
          </h2>
          <div className="text-gray-500 dark:text-gray-400">
            <p>Resumen de actividad por usuario (en desarrollo).</p>
          </div>
        </div>

        {/* Evidencias Invalidadas */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Evidencias Marcadas como Inválidas
          </h2>
          <div className="text-gray-500 dark:text-gray-400">
            <p>Lista de evidencias que han sido invalidadas (en desarrollo).</p>
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


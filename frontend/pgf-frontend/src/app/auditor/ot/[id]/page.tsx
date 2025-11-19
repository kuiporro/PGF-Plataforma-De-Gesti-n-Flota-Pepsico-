"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";
import Link from "next/link";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";

/**
 * Vista de Auditoría por OT para Auditor.
 * 
 * Muestra:
 * - Línea de tiempo completa
 * - Evidencias con estado original
 * - Comparación entre versiones
 * - Historial de cambios
 * 
 * Permisos:
 * - Solo ADMIN puede acceder (Auditor usa rol ADMIN)
 */
export default function AuditorOTPage() {
  const router = useRouter();
  const params = useParams();
  const otId = params.id as string;
  const toast = useToast();
  const { hasRole } = useAuth();

  const [ot, setOt] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [evidencias, setEvidencias] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (otId) {
      cargarDatos();
    }
  }, [otId]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Cargar OT
      const otResponse = await fetch(`${ENDPOINTS.WORK_ORDERS}${otId}/`, {
        method: "GET",
        ...withSession(),
      });

      if (otResponse.ok) {
        const otData = await otResponse.json();
        setOt(otData);
        setEvidencias(otData.evidencias || []);
      }

      // Cargar timeline
      const timelineResponse = await fetch(ENDPOINTS.WORK_ORDERS_TIMELINE(otId), {
        method: "GET",
        ...withSession(),
      });

      if (timelineResponse.ok) {
        const timelineData = await timelineResponse.json();
        setTimeline(timelineData.timeline || []);
      }
    } catch (error) {
      console.error("Error al cargar datos:", error);
      toast.error("Error al cargar información de auditoría");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <RoleGuard allow={["ADMIN"]}>
        <div className="p-6 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando información...</p>
          </div>
        </div>
      </RoleGuard>
    );
  }

  if (!ot) {
    return (
      <RoleGuard allow={["ADMIN"]}>
        <div className="p-6">
          <p className="text-red-600 dark:text-red-400">OT no encontrada</p>
          <Link href="/auditor/dashboard" className="text-blue-600 hover:text-blue-700">
            Volver
          </Link>
        </div>
      </RoleGuard>
    );
  }

  const evidenciasInvalidadas = evidencias.filter((e) => e.invalidado);

  return (
    <RoleGuard allow={["ADMIN"]}>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Auditoría de OT #{ot.id.slice(0, 8)}
          </h1>
          <Link
            href="/auditor/dashboard"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        {/* Información General */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Información de la OT
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Vehículo:</span>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {ot.vehiculo_patente || ot.vehiculo?.patente}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Estado:</span>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {ot.estado}
              </p>
            </div>
          </div>
        </div>

        {/* Evidencias Invalidadas */}
        {evidenciasInvalidadas.length > 0 && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Evidencias Invalidadas ({evidenciasInvalidadas.length})
            </h2>
            <div className="space-y-3">
              {evidenciasInvalidadas.map((evidencia) => (
                <div
                  key={evidencia.id}
                  className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {evidencia.tipo} - {evidencia.descripcion || "Sin descripción"}
                    </span>
                    <span className="text-xs text-red-600 dark:text-red-400">
                      Invalidada por: {evidencia.invalidado_por_nombre || "N/A"}
                    </span>
                  </div>
                  {evidencia.motivo_invalidacion && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <strong>Motivo:</strong> {evidencia.motivo_invalidacion}
                    </p>
                  )}
                  {evidencia.invalidado_en && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Fecha: {new Date(evidencia.invalidado_en).toLocaleString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timeline Completo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Línea de Tiempo Completa
          </h2>
          {timeline.length > 0 ? (
            <div className="space-y-4">
              {timeline.map((item, index) => (
                <div key={index} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full bg-blue-600"></div>
                    {index < timeline.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-300 dark:bg-gray-600 mt-2"></div>
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {item.accion}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(item.fecha).toLocaleString()}
                      </p>
                    </div>
                    {item.usuario && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Por: {item.usuario.nombre} ({item.usuario.rol})
                      </p>
                    )}
                    {item.detalle && (
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {JSON.stringify(item.detalle, null, 2)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">
              No hay eventos registrados en el timeline.
            </p>
          )}
        </div>
      </div>
    </RoleGuard>
  );
}


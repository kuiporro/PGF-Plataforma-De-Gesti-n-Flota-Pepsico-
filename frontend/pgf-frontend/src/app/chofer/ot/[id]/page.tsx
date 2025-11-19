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
 * Vista de estado de OT para Chofer.
 * 
 * Muestra:
 * - Línea de tiempo completa de la OT
 * - Estado actual
 * - Mecánico asignado
 * - Tiempo estimado
 * 
 * Permisos:
 * - Solo CHOFER puede acceder
 */
export default function ChoferOTPage() {
  const router = useRouter();
  const params = useParams();
  const otId = params.id as string;
  const toast = useToast();
  const { hasRole } = useAuth();

  const [ot, setOt] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
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

      if (!otResponse.ok) {
        throw new Error("Error al cargar OT");
      }

      const otData = await otResponse.json();
      setOt(otData);

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
      toast.error("Error al cargar información de la OT");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <RoleGuard allow={["CHOFER"]}>
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
      <RoleGuard allow={["CHOFER"]}>
        <div className="p-6">
          <p className="text-red-600 dark:text-red-400">OT no encontrada</p>
          <Link href="/chofer" className="text-blue-600 hover:text-blue-700">
            Volver
          </Link>
        </div>
      </RoleGuard>
    );
  }

  const estados = [
    { key: "ABIERTA", label: "Ingreso", icon: "📥" },
    { key: "EN_DIAGNOSTICO", label: "Diagnóstico", icon: "🔍" },
    { key: "EN_EJECUCION", label: "Ejecución", icon: "🔧" },
    { key: "EN_PAUSA", label: "Pausa", icon: "⏸️" },
    { key: "EN_QA", label: "QA", icon: "✅" },
    { key: "CERRADA", label: "Cierre", icon: "✔️" },
  ];

  return (
    <RoleGuard allow={["CHOFER"]}>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Estado de la Orden de Trabajo
          </h1>
          <Link
            href="/chofer"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        {/* Información General */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Información General
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            {ot.mecanico_nombre && (
              <div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Mecánico:</span>
                <p className="text-lg text-gray-900 dark:text-white">
                  {ot.mecanico_nombre}
                </p>
              </div>
            )}
            {ot.motivo && (
              <div className="md:col-span-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Motivo:</span>
                <p className="text-sm text-gray-900 dark:text-white mt-1">
                  {ot.motivo}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Línea de Tiempo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Línea de Tiempo
          </h2>
          <div className="space-y-4">
            {timeline.length > 0 ? (
              timeline.map((item, index) => (
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
                        {item.tipo === "comentario" && (
                          <p>{item.detalle.contenido}</p>
                        )}
                        {item.tipo === "pausa" && (
                          <p>Motivo: {item.detalle.motivo}</p>
                        )}
                        {item.tipo === "cambio_estado" && (
                          <p>Estado anterior: {item.detalle.estado_anterior || "N/A"}</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 dark:text-gray-400">
                No hay eventos registrados aún.
              </p>
            )}
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


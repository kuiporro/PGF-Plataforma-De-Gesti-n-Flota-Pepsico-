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
 * Vista de Asignación de Mecánicos para Jefe de Taller.
 * 
 * Muestra:
 * - Lista de mecánicos disponibles
 * - Indicador de carga de trabajo de cada mecánico
 * - OTs pendientes de asignación
 * - Botón para asignar/reasignar mecánicos
 * 
 * Permisos:
 * - Solo JEFE_TALLER puede acceder
 */
export default function JefeTallerAsignacionPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [mecanicos, setMecanicos] = useState<any[]>([]);
  const [otsPendientes, setOtsPendientes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Cargar mecánicos
      const mecanicosResponse = await fetch(`${ENDPOINTS.USERS}?rol=MECANICO`, {
        method: "GET",
        ...withSession(),
      });

      if (mecanicosResponse.ok) {
        const mecanicosData = await mecanicosResponse.json();
        setMecanicos(mecanicosData.results || mecanicosData || []);
      }

      // Cargar OTs pendientes de asignación
      const otsResponse = await fetch(`${ENDPOINTS.WORK_ORDERS}?estado=ABIERTA&mecanico__isnull=true`, {
        method: "GET",
        ...withSession(),
      });

      if (otsResponse.ok) {
        const otsData = await otsResponse.json();
        setOtsPendientes(otsData.results || otsData || []);
      }
    } catch (error) {
      console.error("Error al cargar datos:", error);
      toast.error("Error al cargar información");
    } finally {
      setLoading(false);
    }
  };

  const cargarCargaTrabajo = async (mecanicoId: string) => {
    try {
      const response = await fetch(`${ENDPOINTS.WORK_ORDERS}?mecanico=${mecanicoId}&estado__in=EN_EJECUCION,EN_PAUSA`, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        return (data.results || data || []).length;
      }
      return 0;
    } catch {
      return 0;
    }
  };

  const handleAsignar = async (otId: string, mecanicoId: string) => {
    try {
      const response = await fetch(`/api/proxy/work/ordenes/${otId}/`, {
        method: "PATCH",
        ...withSession(),
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mecanico: mecanicoId,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        toast.error(error.detail || "Error al asignar mecánico");
        return;
      }

      toast.success("Mecánico asignado correctamente");
      await cargarDatos();
    } catch (error) {
      console.error("Error al asignar:", error);
      toast.error("Error al asignar mecánico");
    }
  };

  if (loading) {
    return (
      <RoleGuard allow={["JEFE_TALLER", "ADMIN"]}>
        <div className="p-6 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando información...</p>
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
            Asignación de Mecánicos
          </h1>
          <Link
            href="/jefe-taller/dashboard"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        {/* OTs Pendientes de Asignación */}
        {otsPendientes.length > 0 && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              OTs Pendientes de Asignación ({otsPendientes.length})
            </h2>
            <div className="space-y-2">
              {otsPendientes.map((ot) => (
                <div
                  key={ot.id}
                  className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600"
                >
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">
                      OT #{ot.id.slice(0, 8)} - {ot.vehiculo_patente || ot.vehiculo?.patente}
                    </span>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {ot.motivo?.substring(0, 100)}...
                    </p>
                  </div>
                  <Link
                    href={`/workorders/${ot.id}/edit`}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                  >
                    Asignar Mecánico
                  </Link>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lista de Mecánicos */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Mecánicos Disponibles
            </h2>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {mecanicos.length > 0 ? (
              mecanicos.map((mecanico) => (
                <MecanicoCard
                  key={mecanico.id}
                  mecanico={mecanico}
                  otsPendientes={otsPendientes}
                  onAsignar={handleAsignar}
                />
              ))
            ) : (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                No hay mecánicos registrados.
              </div>
            )}
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}

function MecanicoCard({
  mecanico,
  otsPendientes,
  onAsignar,
}: {
  mecanico: any;
  otsPendientes: any[];
  onAsignar: (otId: string, mecanicoId: string) => void;
}) {
  const [cargaTrabajo, setCargaTrabajo] = useState(0);
  const [loadingCarga, setLoadingCarga] = useState(true);
  const [otSeleccionada, setOtSeleccionada] = useState<string>("");

  useEffect(() => {
    cargarCarga();
  }, []);

  const cargarCarga = async () => {
    setLoadingCarga(true);
    try {
      const response = await fetch(`${ENDPOINTS.WORK_ORDERS}?mecanico=${mecanico.id}&estado__in=EN_EJECUCION,EN_PAUSA`, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        setCargaTrabajo((data.results || data || []).length);
      }
    } catch (error) {
      console.error("Error al cargar carga:", error);
    } finally {
      setLoadingCarga(false);
    }
  };

  const getCargaColor = (carga: number) => {
    if (carga === 0) return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300";
    if (carga <= 2) return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300";
    return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300";
  };

  return (
    <div className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {mecanico.get_full_name || mecanico.username}
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded ${getCargaColor(cargaTrabajo)}`}>
              {loadingCarga ? "Cargando..." : `${cargaTrabajo} OTs activas`}
            </span>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <span>Email: {mecanico.email || "N/A"}</span>
          </div>
        </div>
        <div className="ml-4">
          {otsPendientes.length > 0 && (
            <div className="flex gap-2">
              <select
                value={otSeleccionada}
                onChange={(e) => setOtSeleccionada(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Seleccionar OT...</option>
                {otsPendientes.map((ot) => (
                  <option key={ot.id} value={ot.id}>
                    OT #{ot.id.slice(0, 8)} - {ot.vehiculo_patente || ot.vehiculo?.patente}
                  </option>
                ))}
              </select>
              <button
                onClick={() => {
                  if (otSeleccionada) {
                    onAsignar(otSeleccionada, mecanico.id);
                    setOtSeleccionada("");
                  }
                }}
                disabled={!otSeleccionada}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Asignar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


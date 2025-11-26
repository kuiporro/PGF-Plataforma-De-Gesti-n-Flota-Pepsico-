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
        const mecanicos = mecanicosData.results || mecanicosData || [];
        console.log("Mecánicos cargados:", mecanicos.length, mecanicos);
        setMecanicos(mecanicos);
      } else {
        console.error("Error al cargar mecánicos:", mecanicosResponse.status, mecanicosResponse.statusText);
        const errorText = await mecanicosResponse.text().catch(() => "Error desconocido");
        console.error("Error detallado:", errorText);
        toast.error(`Error al cargar mecánicos: ${mecanicosResponse.status}`);
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
      // Cargar todas las OTs asignadas al mecánico (no solo las activas)
      const response = await fetch(`${ENDPOINTS.WORK_ORDERS}?mecanico=${mecanicoId}`, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        const ots = data.results || data || [];
        // Separar por estado
        const activas = ots.filter((ot: any) => 
          ["EN_EJECUCION", "EN_PAUSA", "EN_DIAGNOSTICO", "ABIERTA"].includes(ot.estado)
        );
        const todas = ots.length;
        return { activas: activas.length, total: todas, ots: activas };
      }
      return { activas: 0, total: 0, ots: [] };
    } catch {
      return { activas: 0, total: 0, ots: [] };
    }
  };

  const handleAsignar = async (otId: string, mecanicoId: string) => {
    try {
      // Primero verificar el estado de la OT
      const otResponse = await fetch(ENDPOINTS.WORK_ORDER(otId), {
        method: "GET",
        ...withSession(),
      });

      if (!otResponse.ok) {
        toast.error("Error al obtener información de la OT");
        return;
      }

      const ot = await otResponse.json();

      // Si la OT está en EN_DIAGNOSTICO o ABIERTA, usar el endpoint de aprobar-asignacion
      if (ot.estado === "EN_DIAGNOSTICO" || ot.estado === "ABIERTA") {
        const baseUrl = ENDPOINTS.WORK_ORDER(otId).replace(/\/$/, '');
        const response = await fetch(`${baseUrl}/aprobar-asignacion/`, {
          method: "POST",
          ...withSession(),
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mecanico_id: mecanicoId,
          }),
        });

        const text = await response.text();
        let data: any = {};
        
        // Intentar parsear JSON solo si hay contenido
        if (text && text.trim() !== "") {
          try {
            data = JSON.parse(text);
          } catch (e) {
            // Si no es JSON válido, usar el texto como mensaje de error
            data = { detail: text || "Error desconocido" };
          }
        } else {
          // Si la respuesta está vacía, crear un mensaje basado en el status
          data = { 
            detail: `Error ${response.status}: ${response.statusText || "Error al asignar mecánico"}` 
          };
        }

        if (!response.ok) {
          const errorMessage = data.detail || data.message || data.error || `Error ${response.status}: ${response.statusText || "Error al asignar mecánico"}`;
          toast.error(errorMessage);
          console.error("Error al asignar:", {
            status: response.status,
            statusText: response.statusText,
            data: data,
            text: text
          });
          return;
        }

        toast.success("Mecánico asignado correctamente");
        await cargarDatos();
      } else {
        // Para otros estados, usar PATCH directo
        const response = await fetch(ENDPOINTS.WORK_ORDER(otId), {
          method: "PATCH",
          ...withSession(),
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mecanico: mecanicoId,
          }),
        });

        const text = await response.text();
        let data: any = {};
        
        // Intentar parsear JSON solo si hay contenido
        if (text && text.trim() !== "") {
          try {
            data = JSON.parse(text);
          } catch (e) {
            // Si no es JSON válido, usar el texto como mensaje de error
            data = { detail: text || "Error desconocido" };
          }
        } else {
          // Si la respuesta está vacía, crear un mensaje basado en el status
          data = { 
            detail: `Error ${response.status}: ${response.statusText || "Error al asignar mecánico"}` 
          };
        }

        if (!response.ok) {
          const errorMessage = data.detail || data.message || data.error || `Error ${response.status}: ${response.statusText || "Error al asignar mecánico"}`;
          toast.error(errorMessage);
          console.error("Error al asignar:", {
            status: response.status,
            statusText: response.statusText,
            data: data,
            text: text
          });
          return;
        }

        toast.success("Mecánico asignado correctamente");
        await cargarDatos();
      }
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
            {loading ? (
              <div className="p-6 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
                <p className="mt-4 text-gray-500 dark:text-gray-400">Cargando mecánicos...</p>
              </div>
            ) : mecanicos.length > 0 ? (
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
                <p className="text-lg font-medium mb-2">No hay mecánicos registrados.</p>
                <p className="text-sm">Asegúrate de que existan usuarios con rol MECANICO en el sistema.</p>
                <p className="text-xs mt-2 text-gray-400 dark:text-gray-500">
                  Total cargados: {mecanicos.length}
                </p>
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
  const [cargaTrabajo, setCargaTrabajo] = useState({ activas: 0, total: 0, ots: [] });
  const [loadingCarga, setLoadingCarga] = useState(true);
  const [otSeleccionada, setOtSeleccionada] = useState<string>("");
  const [mostrarOTs, setMostrarOTs] = useState(false);

  useEffect(() => {
    cargarCarga();
  }, []);

  const cargarCarga = async () => {
    setLoadingCarga(true);
    try {
      // Cargar todas las OTs asignadas al mecánico
      const response = await fetch(`${ENDPOINTS.WORK_ORDERS}?mecanico=${mecanico.id}`, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        const ots = data.results || data || [];
        // Separar por estado
        const activas = ots.filter((ot: any) => 
          ["EN_EJECUCION", "EN_PAUSA", "EN_DIAGNOSTICO", "ABIERTA"].includes(ot.estado)
        );
        setCargaTrabajo({ activas: activas.length, total: ots.length, ots: activas });
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
              {mecanico.get_full_name || `${mecanico.first_name || ""} ${mecanico.last_name || ""}`.trim() || mecanico.username}
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded ${getCargaColor(cargaTrabajo.activas)}`}>
              {loadingCarga ? "Cargando..." : `${cargaTrabajo.activas} OTs activas`}
            </span>
            {cargaTrabajo.total > 0 && (
              <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                {cargaTrabajo.total} OTs totales
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <div>
              <span>Email: {mecanico.email || "N/A"}</span>
            </div>
            {cargaTrabajo.activas > 0 && (
              <div>
                <button
                  onClick={() => setMostrarOTs(!mostrarOTs)}
                  className="text-blue-600 dark:text-blue-400 hover:underline text-xs"
                >
                  {mostrarOTs ? "Ocultar" : "Ver"} OTs asignadas ({cargaTrabajo.activas})
                </button>
              </div>
            )}
          </div>
          {mostrarOTs && cargaTrabajo.ots.length > 0 && (
            <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                OTs Asignadas:
              </h4>
              <div className="space-y-1">
                {cargaTrabajo.ots.map((ot: any) => (
                  <div
                    key={ot.id}
                    className="text-xs text-gray-700 dark:text-gray-300 flex items-center justify-between"
                  >
                    <span>
                      OT #{ot.id.slice(0, 8)} - {ot.vehiculo_patente || ot.vehiculo?.patente} 
                      <span className="ml-2 px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                        {ot.estado}
                      </span>
                    </span>
                    <Link
                      href={`/workorders/${ot.id}`}
                      className="text-blue-600 dark:text-blue-400 hover:underline ml-2"
                    >
                      Ver
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}
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


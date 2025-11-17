"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";

export default function EmergencyDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();
  const [emergency, setEmergency] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [mecanicos, setMecanicos] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch(`/api/proxy/emergencies/${id}/`, {
          credentials: "include",
        });
        
        if (!r.ok) {
          toast.error("Error al cargar emergencia");
          router.push("/emergencies");
          return;
        }
        
        const data = await r.json();
        setEmergency(data);
      } catch (e) {
        console.error("Error:", e);
        toast.error("Error al cargar emergencia");
      } finally {
        setLoading(false);
      }
    };

    const loadMecanicos = async () => {
      try {
        const r = await fetch("/api/proxy/users/?rol=MECANICO", {
          credentials: "include",
        });
        if (r.ok) {
          const data = await r.json();
          setMecanicos(data.results || data || []);
        }
      } catch (error) {
        console.error("Error cargando mecánicos:", error);
      }
    };

    if (id) {
      load();
      loadMecanicos();
    }
  }, [id, router, toast]);

  const handleAction = async (action: string, data?: any) => {
    try {
      const r = await fetch(`/api/proxy/emergencies/${id}/${action}/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: data ? JSON.stringify(data) : undefined,
      });

      if (!r.ok) {
        const error = await r.json().catch(() => ({ detail: "Error" }));
        toast.error(error.detail || `Error al ${action}`);
        return;
      }

      toast.success(`Acción realizada correctamente`);
      // Recargar datos
      const reload = await fetch(`/api/proxy/emergencies/${id}/`, {
        credentials: "include",
      });
      if (reload.ok) {
        const newData = await reload.json();
        setEmergency(newData);
      }
    } catch (e) {
      console.error("Error:", e);
      toast.error(`Error al ${action}`);
    }
  };

  const canAprobar = hasRole(["JEFE_TALLER", "ADMIN", "SPONSOR"]) && emergency?.estado === "SOLICITADA";
  const canAsignar = hasRole(["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA"]) && emergency?.estado === "APROBADA";
  const canResolver = hasRole(["MECANICO", "ADMIN", "SUPERVISOR"]) && 
    (emergency?.estado === "EN_CAMINO" || emergency?.estado === "EN_SITIO");

  const getEstadoColor = (estado: string) => {
    const colors: Record<string, string> = {
      SOLICITADA: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
      APROBADA: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
      ASIGNADA: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      EN_CAMINO: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
      EN_SITIO: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
      RESUELTA: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
      CERRADA: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
      CANCELADA: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
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

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">Cargando...</div>
      </div>
    );
  }

  if (!emergency) {
    return (
      <div className="p-6">
        <div className="text-center text-red-600">Emergencia no encontrada</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Emergencia - {emergency.vehiculo_patente || "N/A"}
        </h1>
        <Link
          href="/emergencies"
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors"
        >
          Volver
        </Link>
      </div>

      {/* Acciones según estado */}
      <div className="mb-6 flex flex-wrap gap-3">
        {canAprobar && (
          <button
            onClick={() => handleAction("aprobar")}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
          >
            Aprobar Emergencia
          </button>
        )}
        
        {canAsignar && (
          <div className="flex gap-2">
            <select
              id="mecanico-select"
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Seleccionar mecánico...</option>
              {mecanicos.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.first_name} {m.last_name}
                </option>
              ))}
            </select>
            <button
              onClick={() => {
                const select = document.getElementById("mecanico-select") as HTMLSelectElement;
                if (select?.value) {
                  handleAction("asignar-mecanico", { mecanico_id: select.value });
                } else {
                  toast.error("Selecciona un mecánico");
                }
              }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Asignar Mecánico
            </button>
          </div>
        )}

        {canResolver && (
          <button
            onClick={() => handleAction("resolver")}
            className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors font-medium"
          >
            Marcar como Resuelta
          </button>
        )}

        {emergency.estado === "RESUELTA" && (
          <button
            onClick={() => handleAction("cerrar")}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium"
          >
            Cerrar Emergencia
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Información General</h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Vehículo</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{emergency.vehiculo_patente || "N/A"}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Estado</dt>
              <dd className="mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEstadoColor(emergency.estado)}`}>
                  {emergency.estado || "N/A"}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Prioridad</dt>
              <dd className="mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPrioridadColor(emergency.prioridad)}`}>
                  {emergency.prioridad || "N/A"}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Ubicación</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{emergency.ubicacion || "N/A"}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Zona</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{emergency.zona || "N/A"}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Fecha de Solicitud</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                {emergency.fecha_solicitud ? new Date(emergency.fecha_solicitud).toLocaleString('es-CL') : "N/A"}
              </dd>
            </div>
          </dl>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Asignaciones</h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Solicitante</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                {emergency.solicitante_nombre || "N/A"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Aprobador</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                {emergency.aprobador_nombre || "Sin aprobar"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Mecánico Asignado</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                {emergency.mecanico_asignado_nombre || "Sin asignar"}
              </dd>
            </div>
            {emergency.fecha_aprobacion && (
              <div>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Fecha de Aprobación</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                  {new Date(emergency.fecha_aprobacion).toLocaleString('es-CL')}
                </dd>
              </div>
            )}
            {emergency.fecha_resolucion && (
              <div>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Fecha de Resolución</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                  {new Date(emergency.fecha_resolucion).toLocaleString('es-CL')}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      <div className="mt-6 bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Descripción</h2>
        <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
          {emergency.descripcion || "N/A"}
        </p>
        {emergency.observaciones_cierre && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Observaciones de Cierre</h3>
            <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
              {emergency.observaciones_cierre}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}


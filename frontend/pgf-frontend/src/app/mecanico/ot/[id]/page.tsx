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
 * Vista de detalle de OT para Mecánico.
 * 
 * Muestra:
 * - Datos del vehículo
 * - Motivo de ingreso
 * - Checklist técnico
 * - Barra de estados
 * - Botones de acción (Iniciar Diagnóstico, Iniciar Ejecución, Pausar, etc.)
 * - Sección de evidencias
 * - Observaciones técnicas
 * 
 * Permisos:
 * - Solo MECANICO puede acceder
 */
export default function MecanicoOTPage() {
  const router = useRouter();
  const params = useParams();
  const otId = params.id as string;
  const toast = useToast();
  const { hasRole } = useAuth();

  const [ot, setOt] = useState<any>(null);
  const [comentarios, setComentarios] = useState<any[]>([]);
  const [nuevoComentario, setNuevoComentario] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

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

      // Cargar comentarios
      const comentariosResponse = await fetch(`${ENDPOINTS.WORK_COMENTARIOS}?ot=${otId}`, {
        method: "GET",
        ...withSession(),
      });

      if (comentariosResponse.ok) {
        const comentariosData = await comentariosResponse.json();
        setComentarios(comentariosData.results || comentariosData || []);
      }
    } catch (error) {
      console.error("Error al cargar datos:", error);
      toast.error("Error al cargar información de la OT");
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = async (action: string) => {
    setActionLoading(true);
    try {
      const response = await fetch(`/api/proxy/work/ordenes/${otId}/${action}/`, {
        method: "POST",
        ...withSession(),
      });

      if (!response.ok) {
        const error = await response.json();
        toast.error(error.detail || "Error al cambiar estado");
        return;
      }

      toast.success("Estado actualizado correctamente");
      await cargarDatos();
    } catch (error) {
      console.error("Error al cambiar estado:", error);
      toast.error("Error al cambiar estado");
    } finally {
      setActionLoading(false);
    }
  };

  const handleAgregarComentario = async () => {
    if (!nuevoComentario.trim()) {
      toast.error("El comentario no puede estar vacío");
      return;
    }

    try {
      const response = await fetch(ENDPOINTS.WORK_COMENTARIOS, {
        method: "POST",
        ...withSession(),
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ot: otId,
          contenido: nuevoComentario,
          menciones: [],
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        toast.error(error.detail || "Error al agregar comentario");
        return;
      }

      toast.success("Comentario agregado correctamente");
      setNuevoComentario("");
      await cargarDatos();
    } catch (error) {
      console.error("Error al agregar comentario:", error);
      toast.error("Error al agregar comentario");
    }
  };

  if (loading) {
    return (
      <RoleGuard allow={["MECANICO"]}>
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
      <RoleGuard allow={["MECANICO"]}>
        <div className="p-6">
          <p className="text-red-600 dark:text-red-400">OT no encontrada</p>
          <Link href="/mecanico" className="text-blue-600 hover:text-blue-700">
            Volver
          </Link>
        </div>
      </RoleGuard>
    );
  }

  return (
    <RoleGuard allow={["MECANICO"]}>
      <div className="p-6 max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            OT #{ot.id.slice(0, 8)}
          </h1>
          <Link
            href="/mecanico"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        {/* Información del Vehículo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Datos del Vehículo
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Patente:</span>
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
            {ot.motivo && (
              <div className="md:col-span-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Motivo de Ingreso:</span>
                <p className="text-sm text-gray-900 dark:text-white mt-1">
                  {ot.motivo}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Barra de Estados y Acciones */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Acciones
          </h2>
          <div className="flex flex-wrap gap-3">
            {ot.estado === "ABIERTA" && (
              <button
                onClick={() => handleStateChange("en-diagnostico")}
                disabled={actionLoading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
              >
                🟦 Iniciar Diagnóstico
              </button>
            )}
            {ot.estado === "EN_DIAGNOSTICO" && (
              <button
                onClick={() => handleStateChange("en-ejecucion")}
                disabled={actionLoading}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
              >
                🟧 Iniciar Ejecución
              </button>
            )}
            {ot.estado === "EN_EJECUCION" && (
              <>
                <button
                  onClick={() => handleStateChange("en-pausa")}
                  disabled={actionLoading}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
                >
                  🟨 Pausar OT
                </button>
                <button
                  onClick={() => handleStateChange("esperando-repuestos")}
                  disabled={actionLoading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
                >
                  🟥 Esperando Repuestos
                </button>
              </>
            )}
            {ot.estado === "EN_PAUSA" && (
              <button
                onClick={() => handleStateChange("reanudar")}
                disabled={actionLoading}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
              >
                ▶️ Reanudar
              </button>
            )}
          </div>
        </div>

        {/* Evidencias */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Evidencias
            </h2>
            <Link
              href={`/workorders/${otId}/evidences/upload`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Subir Evidencia
            </Link>
          </div>
          {ot.evidencias && ot.evidencias.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {ot.evidencias.map((evidencia: any) => (
                <div key={evidencia.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-2">
                  {evidencia.tipo === "FOTO" ? (
                    <img
                      src={evidencia.url}
                      alt={evidencia.descripcion}
                      className="w-full h-32 object-cover rounded"
                    />
                  ) : (
                    <div className="w-full h-32 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
                      <span className="text-gray-500 dark:text-gray-400">{evidencia.tipo}</span>
                    </div>
                  )}
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 truncate">
                    {evidencia.descripcion || "Sin descripción"}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No hay evidencias subidas aún.</p>
          )}
        </div>

        {/* Observaciones Técnicas / Comentarios */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Observaciones Técnicas
          </h2>
          
          {/* Formulario de nuevo comentario */}
          <div className="mb-4">
            <textarea
              value={nuevoComentario}
              onChange={(e) => setNuevoComentario(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              rows={3}
              placeholder="Agregar observación técnica..."
            />
            <button
              onClick={handleAgregarComentario}
              className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Agregar Observación
            </button>
          </div>

          {/* Lista de comentarios */}
          <div className="space-y-3">
            {comentarios.length > 0 ? (
              comentarios.map((comentario) => (
                <div
                  key={comentario.id}
                  className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {comentario.usuario_nombre || comentario.usuario?.username}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(comentario.creado_en).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {comentario.contenido}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 dark:text-gray-400">No hay observaciones aún.</p>
            )}
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


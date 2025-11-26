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
  const otId = params?.id as string | undefined;
  const toast = useToast();
  const { hasRole } = useAuth();

  const [ot, setOt] = useState<any>(null);
  const [comentarios, setComentarios] = useState<any[]>([]);
  const [nuevoComentario, setNuevoComentario] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (otId && typeof otId === 'string' && otId.trim() !== '') {
      cargarDatos();
    } else if (params && !otId) {
      // Si params existe pero otId no, mostrar error
      toast.error("ID de OT no encontrado en la URL");
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [otId]);

  const cargarDatos = async () => {
    if (!otId || typeof otId !== 'string' || otId.trim() === '') {
      console.error("otId no está definido o es inválido:", otId);
      toast.error("ID de OT no válido");
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      // Cargar OT
      const url = ENDPOINTS.WORK_ORDER(otId);
      if (!url || url.includes('undefined') || url.includes('null')) {
        throw new Error(`URL inválida: ${url} (otId: ${otId})`);
      }
      
      // Asegurar que la URL es relativa válida (empezando con /)
      // Las URLs relativas funcionan directamente con fetch en el navegador
      const fullUrl = url.startsWith('/') ? url : `/${url}`;
      
      const otResponse = await fetch(fullUrl, {
        method: "GET",
        ...withSession(),
      });

      if (!otResponse.ok) {
        const errorText = await otResponse.text().catch(() => "Error desconocido");
        let errorMessage = "Error al cargar OT";
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          errorMessage = errorText || errorMessage;
        }
        throw new Error(errorMessage);
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
      // Para "reanudar", necesitamos encontrar la pausa activa y reanudarla
      if (action === "reanudar") {
        // Buscar pausa activa de esta OT
        const pausasResponse = await fetch(`${ENDPOINTS.WORK_PAUSAS}?ot=${otId}&fin__isnull=true`, {
          method: "GET",
          ...withSession(),
        });

        if (pausasResponse.ok) {
          const pausasData = await pausasResponse.json();
          const pausas = pausasData.results || pausasData || [];
          
          if (pausas.length > 0) {
            // Reanudar la primera pausa activa
            const pausa = pausas[0];
            const reanudarResponse = await fetch(`/api/proxy/work/pausas/${pausa.id}/reanudar/`, {
              method: "POST",
              ...withSession(),
            });

            const text = await reanudarResponse.text();
            let data;
            try {
              data = JSON.parse(text);
            } catch {
              data = { detail: text || "Error desconocido" };
            }

            if (!reanudarResponse.ok) {
              toast.error(data.detail || "Error al reanudar");
              return;
            }

            toast.success("OT reanudada correctamente");
            await cargarDatos();
            return;
          } else {
            // Si no hay pausa activa, cambiar estado directamente a EN_EJECUCION
            action = "en-ejecucion";
          }
        }
      }

      // Para otras acciones, usar el endpoint de cambio de estado
      if (!otId || typeof otId !== 'string' || otId.trim() === '') {
        toast.error("ID de OT no válido");
        console.error("otId inválido en handleStateChange:", otId);
        return;
      }

      if (!action || typeof action !== 'string' || action.trim() === '') {
        toast.error("Acción no válida");
        console.error("action inválido:", action);
        return;
      }

      const url = `/api/proxy/work/ordenes/${otId}/${action}/`;
      if (!url || url.includes('undefined') || url.includes('null')) {
        toast.error(`URL inválida para acción: ${action}`);
        console.error("URL inválida:", url, "otId:", otId, "action:", action);
        return;
      }

      const response = await fetch(url, {
        method: "POST",
        ...withSession(),
      });

      // Leer la respuesta como texto primero
      const text = await response.text();
      
      // Si la respuesta está vacía pero el status es exitoso, considerar éxito
      if (response.ok && (!text || text.trim() === "" || text.trim() === "{}")) {
        toast.success("Estado actualizado correctamente");
        await cargarDatos();
        return;
      }

      // Intentar parsear como JSON
      let data: any = {};
      try {
        if (text && text.trim() && text.trim() !== "{}") {
          data = JSON.parse(text);
        } else if (text && text.trim() === "{}") {
          // Si es un objeto vacío, puede ser una respuesta exitosa
          data = {};
        }
      } catch (e) {
        // Si no es JSON válido, puede ser HTML (página de error) o texto plano
        data = { 
          detail: text || "Error desconocido",
          raw: text.substring(0, 200), // Primeros 200 caracteres para debugging
          parseError: String(e)
        };
      }

      // Si la respuesta es exitosa y tiene datos, actualizar
      if (response.ok) {
        if (data && (data.estado || Object.keys(data).length > 0)) {
          toast.success("Estado actualizado correctamente");
          await cargarDatos();
          return;
        } else if (Object.keys(data).length === 0) {
          // Respuesta exitosa pero vacía, considerar éxito
          toast.success("Estado actualizado correctamente");
          await cargarDatos();
          return;
        }
      }

      if (!response.ok) {
        // Construir mensaje de error más informativo
        let errorMessage = "Error al cambiar estado";
        
        // Si data está vacío pero hay texto, intentar parsear de nuevo
        if (Object.keys(data).length === 0 && text && text.trim()) {
          try {
            const parsed = JSON.parse(text);
            if (parsed && typeof parsed === 'object') {
              data = parsed;
            }
          } catch {
            // Si no se puede parsear, usar el texto como mensaje
            data = { detail: text.substring(0, 200) };
          }
        }
        
        // Si aún está vacío, intentar leer la respuesta de nuevo
        if (Object.keys(data).length === 0) {
          try {
            const clonedResponse = response.clone();
            const jsonData = await clonedResponse.json().catch(() => null);
            if (jsonData && typeof jsonData === 'object') {
              data = jsonData;
            }
          } catch {
            // Si falla, usar el status code
          }
        }
        
        if (data.detail) {
          errorMessage = data.detail;
        } else if (data.message) {
          errorMessage = data.message;
        } else if (data.raw) {
          errorMessage = data.raw;
        } else if (text && text.trim()) {
          errorMessage = text.substring(0, 100);
        } else if (response.status === 403) {
          errorMessage = "No tiene permisos para realizar esta acción";
        } else if (response.status === 400) {
          errorMessage = "Solicitud inválida. Verifique los datos.";
        } else if (response.status === 404) {
          errorMessage = "Recurso no encontrado";
        } else if (response.status === 500) {
          errorMessage = "Error interno del servidor";
        } else {
          errorMessage = `Error ${response.status}: ${response.statusText || "Error desconocido"}`;
        }
        
        toast.error(errorMessage);
        console.error("Error al cambiar estado:", {
          status: response.status,
          statusText: response.statusText,
          url: `/api/proxy/work/ordenes/${otId}/${action}/`,
          action: action,
          data: data,
          text: text ? text.substring(0, 500) : "(vacío)", // Primeros 500 caracteres
          responseHeaders: Object.fromEntries(response.headers.entries()),
          isEmpty: Object.keys(data).length === 0,
          responseType: response.headers.get("content-type"),
          isOk: response.ok,
        });
        return;
      }
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
            {hasRole(["MECANICO", "SUPERVISOR", "ADMIN", "GUARDIA", "JEFE_TALLER"]) && (
              <Link
                href={`/workorders/${otId}/evidences/upload`}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
              >
                Subir Evidencia
              </Link>
            )}
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


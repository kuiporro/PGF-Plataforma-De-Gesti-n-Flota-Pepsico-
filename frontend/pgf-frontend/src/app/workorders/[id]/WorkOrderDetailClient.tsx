"use client";

import { useAuth } from "@/store/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";

interface WorkOrderDetailClientProps {
  ot: any;
  id: string;
}

export default function WorkOrderDetailClient({ ot, id }: WorkOrderDetailClientProps) {
  const router = useRouter();
  const toast = useToast();
  const { hasRole, user } = useAuth();

  // Permisos según nueva especificación
  const isJefeTaller = hasRole(["JEFE_TALLER"]);
  const isMecanico = hasRole(["MECANICO"]);
  const isAdmin = hasRole(["ADMIN"]);
  const canEdit = isJefeTaller || isAdmin;
  const canChangeState = isMecanico || isJefeTaller;
  const canClose = isJefeTaller;
  const canAssign = isJefeTaller;
  // Roles autorizados para subir evidencias
  const canUploadEvidence = hasRole(["MECANICO", "SUPERVISOR", "ADMIN", "GUARDIA", "JEFE_TALLER"]);

  // Acciones de cambio de estado
  const handleStateChange = async (action: string) => {
    try {
      const response = await fetch(`/api/proxy/work/ordenes/${id}/${action}/`, {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        toast.success("Estado actualizado correctamente");
        router.refresh();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Error al cambiar estado");
      }
    } catch (error) {
      toast.error("Error al cambiar estado");
    }
  };

  // Seguridad
  const evidencias = ot.evidencias ?? [];
  const items = ot.items ?? [];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Orden de Trabajo #{id}</h1>
        <div className="flex gap-3">
          <Link
            href={`/workorders/${id}/timeline`}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors font-medium"
          >
            Timeline
          </Link>
          <Link
            href={`/workorders/${id}/comentarios`}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
          >
            Comentarios
          </Link>
          {canEdit && (
            <Link
              href={`/workorders/${id}/edit`}
              className="px-4 py-2 text-white rounded-lg transition-colors font-medium"
              style={{ backgroundColor: '#003DA5' }}
            >
              Editar
            </Link>
          )}
          {ot.estado === "ABIERTA" && isAdmin && (
            <Link
              href={`/workorders/${id}/delete`}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium"
            >
              Eliminar
            </Link>
          )}
        </div>
      </div>

      {/* === Estado y botones === */}
      <section className="p-6 bg-white dark:bg-gray-800 shadow rounded-lg space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Estado Actual</h2>
            <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
              ot.estado === "ABIERTA" ? "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400" :
              ot.estado === "EN_DIAGNOSTICO" ? "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-400" :
              ot.estado === "EN_EJECUCION" ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400" :
              ot.estado === "EN_PAUSA" ? "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400" :
              ot.estado === "EN_QA" ? "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400" :
              ot.estado === "RETRABAJO" ? "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400" :
              "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400"
            }`}>
              {ot.estado}
            </span>
          </div>
        </div>

        {/* Acciones según estado y rol */}
        <div className="flex flex-wrap gap-3 mt-4">
          {/* Diagnóstico: Solo JEFE_TALLER */}
          {ot.estado === "ABIERTA" && isJefeTaller && (
            <Link
              href={`/workorders/${id}/diagnostico`}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium"
            >
              Realizar Diagnóstico
            </Link>
          )}
          
          {/* Aprobar Asignación: Solo JEFE_TALLER */}
          {ot.estado === "EN_DIAGNOSTICO" && canAssign && (
            <Link
              href={`/workorders/${id}/aprobar-asignacion`}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
            >
              Aprobar Asignación
            </Link>
          )}

          {/* Cambiar a EN_EJECUCION: MECANICO o JEFE_TALLER */}
          {ot.estado === "ABIERTA" && canChangeState && (
            <button
              onClick={() => handleStateChange("en-ejecucion")}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              Iniciar Ejecución
            </button>
          )}

          {/* Cambiar a EN_PAUSA: MECANICO o JEFE_TALLER */}
          {ot.estado === "EN_EJECUCION" && canChangeState && (
            <button
              onClick={() => handleStateChange("en-pausa")}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors font-medium"
            >
              Pausar
            </button>
          )}

          {/* Cambiar a EN_QA: MECANICO o JEFE_TALLER */}
          {ot.estado === "EN_EJECUCION" && canChangeState && (
            <button
              onClick={() => handleStateChange("en-qa")}
              className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg transition-colors font-medium"
            >
              Enviar a QA
            </button>
          )}

          {/* Marcar Retrabajo: Solo JEFE_TALLER */}
          {ot.estado === "EN_QA" && canClose && (
            <Link
              href={`/workorders/${id}/retrabajo`}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium"
            >
              Marcar como Retrabajo
            </Link>
          )}

          {/* Cerrar OT: Solo JEFE_TALLER */}
          {ot.estado === "EN_QA" && canClose && (
            <Link
              href={`/workorders/${id}/cerrar`}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
            >
              Cerrar OT
            </Link>
          )}
        </div>
      </section>

      {/* Información general */}
      <section className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow space-y-4">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Información General</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Tipo
            </label>
            <p className="text-lg text-gray-900 dark:text-white">{ot.tipo || "N/A"}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Prioridad
            </label>
            <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
              ot.prioridad === "ALTA" ? "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400" :
              ot.prioridad === "MEDIA" ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400" :
              "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400"
            }`}>
              {ot.prioridad || "MEDIA"}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Supervisor
            </label>
            <p className="text-lg text-gray-900 dark:text-white">
              {ot.supervisor_nombre || (ot.supervisor
                ? `${ot.supervisor.first_name} ${ot.supervisor.last_name}`
                : "Sin supervisor")}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Jefe de Taller
            </label>
            <p className="text-lg text-gray-900 dark:text-white">
              {ot.jefe_taller_nombre || (ot.jefe_taller
                ? `${ot.jefe_taller.first_name} ${ot.jefe_taller.last_name}`
                : "Sin asignar")}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Mecánico
            </label>
            <p className="text-lg text-gray-900 dark:text-white">
              {ot.mecanico_nombre || (ot.mecanico
                ? `${ot.mecanico.first_name} ${ot.mecanico.last_name}`
                : "Sin asignar")}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Apertura
            </label>
            <p className="text-lg text-gray-900 dark:text-white">
              {new Date(ot.apertura).toLocaleString()}
            </p>
          </div>

          {ot.cierre && (
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Cierre
              </label>
              <p className="text-lg text-gray-900 dark:text-white">
                {new Date(ot.cierre).toLocaleString()}
              </p>
            </div>
          )}

          {ot.motivo && (
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Motivo
              </label>
              <p className="text-lg text-gray-900 dark:text-white">{ot.motivo}</p>
            </div>
          )}

          {ot.diagnostico && (
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Diagnóstico
              </label>
              <p className="text-lg text-gray-900 dark:text-white whitespace-pre-wrap">{ot.diagnostico}</p>
            </div>
          )}
        </div>
      </section>

      {/* Vehículo */}
      <section className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Vehículo</h2>
        {ot.vehiculo ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Patente
              </label>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {ot.vehiculo.patente}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Marca
              </label>
              <p className="text-lg text-gray-900 dark:text-white">{ot.vehiculo.marca}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Modelo
              </label>
              <p className="text-lg text-gray-900 dark:text-white">{ot.vehiculo.modelo}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Año
              </label>
              <p className="text-lg text-gray-900 dark:text-white">{ot.vehiculo.anio}</p>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400">Sin vehículo asignado</p>
        )}
      </section>

      {/* Items */}
      <section className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Items</h2>
          {items.length > 0 && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Total: ${items.reduce((sum: number, i: any) => sum + (i.cantidad * i.costo_unitario), 0).toLocaleString()}
            </span>
          )}
        </div>

        {items.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">No hay items registrados.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100 dark:bg-gray-700">
                  <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Tipo</th>
                  <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Descripción</th>
                  <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Cantidad</th>
                  <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Costo Unit.</th>
                  <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Total</th>
                </tr>
              </thead>
              <tbody>
                {items.map((i: any) => (
                  <tr key={i.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="p-3 text-gray-900 dark:text-white">{i.tipo}</td>
                    <td className="p-3 text-gray-700 dark:text-gray-300">{i.descripcion}</td>
                    <td className="p-3 text-gray-700 dark:text-gray-300">{i.cantidad}</td>
                    <td className="p-3 text-gray-700 dark:text-gray-300">${i.costo_unitario.toLocaleString()}</td>
                    <td className="p-3 font-semibold text-gray-900 dark:text-white">
                      ${(i.cantidad * i.costo_unitario).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Evidencias */}
      <section className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Evidencias</h2>
          {canUploadEvidence && (
            <Link
              href={`/workorders/${id}/evidences/upload`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium text-sm"
            >
              + Subir Evidencia
            </Link>
          )}
        </div>

        {evidencias.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400 mb-4">No hay evidencias registradas.</p>
            {canUploadEvidence && (
              <Link
                href={`/workorders/${id}/evidences/upload`}
                className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
              >
                Subir Primera Evidencia
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evidencias.map((e: any) => (
              <div key={e.id} className="border dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <a
                  href={e.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  {e.descripcion || e.tipo || "Evidencia"}
                </a>
                {e.tipo && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Tipo: {e.tipo}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <div className="pt-4">
        <Link
          href="/workorders"
          className="text-blue-600 dark:text-blue-400 hover:underline"
        >
          ← Volver a órdenes de trabajo
        </Link>
      </div>
    </div>
  );
}


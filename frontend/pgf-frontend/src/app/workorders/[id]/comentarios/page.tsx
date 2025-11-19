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
 * Vista de Comentarios en OT.
 * 
 * Muestra:
 * - Lista de comentarios
 * - Formulario para agregar comentarios
 * - Soporte para menciones (@usuario)
 * - Respuestas a comentarios
 * 
 * Permisos:
 * - Todos los roles con acceso a workorders
 */
export default function ComentariosOTPage() {
  const router = useRouter();
  const params = useParams();
  const otId = params.id as string;
  const toast = useToast();
  const { user } = useAuth();

  const [comentarios, setComentarios] = useState<any[]>([]);
  const [nuevoComentario, setNuevoComentario] = useState("");
  const [comentarioPadre, setComentarioPadre] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (otId) {
      cargarComentarios();
    }
  }, [otId]);

  const cargarComentarios = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${ENDPOINTS.WORK_COMENTARIOS}?ot=${otId}`, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        // Filtrar solo comentarios principales (sin padre)
        const principales = (data.results || data || []).filter((c: any) => !c.comentario_padre);
        setComentarios(principales);
      }
    } catch (error) {
      console.error("Error al cargar comentarios:", error);
      toast.error("Error al cargar comentarios");
    } finally {
      setLoading(false);
    }
  };

  const handleAgregarComentario = async () => {
    if (!nuevoComentario.trim()) {
      toast.error("El comentario no puede estar vacío");
      return;
    }

    try {
      // Extraer menciones del texto (formato: @username)
      const menciones = nuevoComentario.match(/@\w+/g) || [];

      const response = await fetch(ENDPOINTS.WORK_COMENTARIOS, {
        method: "POST",
        ...withSession(),
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ot: otId,
          contenido: nuevoComentario,
          menciones: menciones,
          comentario_padre: comentarioPadre || null,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        toast.error(error.detail || "Error al agregar comentario");
        return;
      }

      toast.success("Comentario agregado correctamente");
      setNuevoComentario("");
      setComentarioPadre(null);
      await cargarComentarios();
    } catch (error) {
      console.error("Error al agregar comentario:", error);
      toast.error("Error al agregar comentario");
    }
  };

  const handleResponder = (comentarioId: string) => {
    setComentarioPadre(comentarioId);
    // Scroll al formulario
    document.getElementById("formulario-comentario")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <RoleGuard allow={["ADMIN", "SUPERVISOR", "MECANICO", "JEFE_TALLER", "CHOFER"]}>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Comentarios de la OT
          </h1>
          <Link
            href={`/workorders/${otId}`}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver a OT
          </Link>
        </div>

        {/* Formulario de Comentario */}
        <div id="formulario-comentario" className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            {comentarioPadre ? "Responder Comentario" : "Agregar Comentario"}
          </h2>
          <div className="space-y-4">
            <textarea
              value={nuevoComentario}
              onChange={(e) => setNuevoComentario(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              rows={4}
              placeholder="Escribe tu comentario... Puedes mencionar usuarios con @username"
            />
            <div className="flex gap-2">
              <button
                onClick={handleAgregarComentario}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
              >
                {comentarioPadre ? "Responder" : "Agregar Comentario"}
              </button>
              {comentarioPadre && (
                <button
                  onClick={() => {
                    setComentarioPadre(null);
                    setNuevoComentario("");
                  }}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
                >
                  Cancelar
                </button>
              )}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Tip: Usa @username para mencionar a otros usuarios
            </p>
          </div>
        </div>

        {/* Lista de Comentarios */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Comentarios ({comentarios.length})
          </h2>
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando comentarios...</p>
            </div>
          ) : comentarios.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">No hay comentarios aún.</p>
          ) : (
            <div className="space-y-4">
              {comentarios.map((comentario) => (
                <ComentarioCard
                  key={comentario.id}
                  comentario={comentario}
                  onResponder={handleResponder}
                  nivel={0}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </RoleGuard>
  );
}

function ComentarioCard({
  comentario,
  onResponder,
  nivel,
}: {
  comentario: any;
  onResponder: (id: string) => void;
  nivel: number;
}) {
  return (
    <div className={`p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 ${nivel > 0 ? "ml-8" : ""}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900 dark:text-white">
            {comentario.usuario_nombre || comentario.usuario?.username || "Usuario"}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            ({comentario.usuario_rol || comentario.usuario?.rol || "N/A"})
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {new Date(comentario.creado_en).toLocaleString()}
          </span>
          {comentario.editado && (
            <span className="text-xs text-gray-400">(editado)</span>
          )}
        </div>
      </div>
      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2 whitespace-pre-wrap">
        {comentario.contenido}
      </p>
      {comentario.menciones && comentario.menciones.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {comentario.menciones.map((mencion: string, idx: number) => (
            <span
              key={idx}
              className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded"
            >
              {mencion}
            </span>
          ))}
        </div>
      )}
      {nivel === 0 && (
        <button
          onClick={() => onResponder(comentario.id)}
          className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          Responder
        </button>
      )}
      {/* Respuestas */}
      {comentario.respuestas && comentario.respuestas.length > 0 && (
        <div className="mt-4 space-y-2">
          {comentario.respuestas.map((respuesta: any) => (
            <ComentarioCard
              key={respuesta.id}
              comentario={respuesta}
              onResponder={onResponder}
              nivel={nivel + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}


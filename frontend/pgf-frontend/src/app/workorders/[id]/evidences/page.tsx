"use client";

import { useEffect, useState } from "react";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import Link from "next/link";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";

/**
 * Página de evidencias de una Orden de Trabajo.
 * 
 * Características:
 * - Lista todas las evidencias de una OT
 * - Filtros por tipo de evidencia
 * - Filtros por fecha (desde/hasta)
 * - Búsqueda por descripción
 * - Ordenamiento por fecha
 * - Vista previa de imágenes
 * - Descarga de archivos
 */
export default function EvidencesPage({ params }: any) {
  const otId = params.id;
  const toast = useToast();
  const { hasRole } = useAuth();

  // Solo MECANICO y JEFE_TALLER pueden subir evidencias
  const canUpload = hasRole(["MECANICO", "JEFE_TALLER", "ADMIN"]);

  const [rows, setRows] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Filtros
  const [filtroTipo, setFiltroTipo] = useState<string>("");
  const [filtroFechaDesde, setFiltroFechaDesde] = useState<string>("");
  const [filtroFechaHasta, setFiltroFechaHasta] = useState<string>("");
  const [busqueda, setBusqueda] = useState<string>("");
  const [orden, setOrden] = useState<"subido_en" | "-subido_en">("-subido_en");

  const load = async () => {
    setLoading(true);
    try {
      // Construir URL con filtros
      let url = `${ENDPOINTS.EVIDENCES}?ot=${otId}`;
      
      if (filtroTipo) {
        url += `&tipo=${filtroTipo}`;
      }
      
      if (filtroFechaDesde) {
        url += `&subido_en__gte=${filtroFechaDesde}`;
      }
      
      if (filtroFechaHasta) {
        url += `&subido_en__lte=${filtroFechaHasta}`;
      }
      
      if (orden) {
        url += `&ordering=${orden}`;
      }

      const r = await fetch(url, withSession());
      if (!r.ok) {
        toast.error("Error al cargar evidencias");
        return;
      }
      
      const j = await r.json();
      let evidencias = j.results ?? j;
      
      // Filtrar por búsqueda en el frontend (descripción)
      if (busqueda) {
        evidencias = evidencias.filter((e: any) =>
          (e.descripcion || "").toLowerCase().includes(busqueda.toLowerCase()) ||
          (e.tipo || "").toLowerCase().includes(busqueda.toLowerCase())
        );
      }
      
      setRows(evidencias);
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al cargar evidencias");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [filtroTipo, filtroFechaDesde, filtroFechaHasta, orden]);

  // Búsqueda con debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      load();
    }, 300);
    return () => clearTimeout(timer);
  }, [busqueda]);

  const limpiarFiltros = () => {
    setFiltroTipo("");
    setFiltroFechaDesde("");
    setFiltroFechaHasta("");
    setBusqueda("");
    setOrden("-subido_en");
  };

  const formatFecha = (fechaStr: string) => {
    if (!fechaStr) return "";
    try {
      const fecha = new Date(fechaStr);
      return fecha.toLocaleDateString("es-CL", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return fechaStr;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* HEADER */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Evidencias</h1>
        {canUpload && (
          <Link
            href={`/workorders/${otId}/evidences/upload`}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            style={{ backgroundColor: '#003DA5' }}
          >
            + Subir Evidencia
          </Link>
        )}
      </div>

      {/* FILTROS Y BÚSQUEDA */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Búsqueda */}
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Buscar
            </label>
            <input
              type="text"
              placeholder="Buscar por descripción o tipo..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="input w-full"
            />
          </div>

          {/* Filtro por tipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tipo
            </label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="input w-full"
            >
              <option value="">Todos</option>
              <option value="FOTO">FOTO</option>
              <option value="PDF">PDF</option>
              <option value="HOJA_CALCULO">HOJA_CALCULO</option>
              <option value="DOCUMENTO">DOCUMENTO</option>
              <option value="COMPRIMIDO">COMPRIMIDO</option>
              <option value="OTRO">OTRO</option>
            </select>
          </div>

          {/* Orden */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Ordenar
            </label>
            <select
              value={orden}
              onChange={(e) => setOrden(e.target.value as any)}
              className="input w-full"
            >
              <option value="-subido_en">Más recientes</option>
              <option value="subido_en">Más antiguas</option>
            </select>
          </div>

          {/* Botón limpiar */}
          <div className="flex items-end">
            <button
              onClick={limpiarFiltros}
              className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Limpiar
            </button>
          </div>
        </div>

        {/* Filtros de fecha */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Desde
            </label>
            <input
              type="date"
              value={filtroFechaDesde}
              onChange={(e) => setFiltroFechaDesde(e.target.value)}
              className="input w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Hasta
            </label>
            <input
              type="date"
              value={filtroFechaHasta}
              onChange={(e) => setFiltroFechaHasta(e.target.value)}
              className="input w-full"
            />
          </div>
        </div>
      </div>

      {/* CONTADOR Y RESULTADOS */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {rows.length} evidencia{rows.length !== 1 ? "s" : ""} encontrada{rows.length !== 1 ? "s" : ""}
        </p>
      </div>

      {/* GRID DE EVIDENCIAS */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando evidencias...</p>
          </div>
        </div>
      ) : rows.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <p className="text-gray-500 dark:text-gray-400">No se encontraron evidencias</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {rows.map((e) => (
            <div
              key={e.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow cursor-pointer hover:shadow-lg transition p-4"
              onClick={() => setSelected(e)}
            >
              {e.tipo === "FOTO" && (
                <img
                  src={e.url}
                  className="w-full h-32 object-cover rounded mb-2"
                  alt="Evidencia"
                />
              )}
              {e.tipo !== "FOTO" && (
                <div className="w-full h-32 bg-gray-100 dark:bg-gray-700 rounded mb-2 flex items-center justify-center">
                  <span className="text-4xl">
                    {e.tipo === "PDF" && "📄"}
                    {e.tipo === "HOJA_CALCULO" && "📊"}
                    {e.tipo === "DOCUMENTO" && "📝"}
                    {e.tipo === "COMPRIMIDO" && "📦"}
                    {!["PDF", "HOJA_CALCULO", "DOCUMENTO", "COMPRIMIDO"].includes(e.tipo) && "📎"}
                  </span>
                </div>
              )}
              <p className="font-semibold text-sm text-gray-900 dark:text-white truncate">
                {e.descripcion || e.tipo}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {formatFecha(e.subido_en)}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                {e.tipo}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* MODAL DE PREVIEW */}
      {selected && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {selected.descripcion || selected.tipo}
              </h2>
              <button
                onClick={() => setSelected(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <p><strong>Tipo:</strong> {selected.tipo}</p>
              <p><strong>Subido:</strong> {formatFecha(selected.subido_en)}</p>
              {selected.descripcion && (
                <p><strong>Descripción:</strong> {selected.descripcion}</p>
              )}
            </div>

            {selected.tipo === "FOTO" ? (
              <img
                src={selected.url}
                className="rounded max-h-[400px] mx-auto w-full object-contain"
                alt={selected.descripcion || "Evidencia"}
              />
            ) : (
              <div className="space-y-2">
                <a
                  href={selected.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium text-center"
                  style={{ backgroundColor: '#003DA5' }}
                >
                  📥 Abrir/Descargar archivo
                </a>
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  El archivo se abrirá en una nueva pestaña
                </p>
              </div>
            )}

            <button
              onClick={() => setSelected(null)}
              className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

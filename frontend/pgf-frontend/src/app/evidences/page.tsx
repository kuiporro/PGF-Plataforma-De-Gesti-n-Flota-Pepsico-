"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";
import Link from "next/link";

/**
 * Página general de evidencias.
 * 
 * Permite:
 * - Ver todas las evidencias del sistema
 * - Filtrar por tipo, OT, fecha
 * - Subir nuevas evidencias
 * - Ver detalles de evidencias
 * 
 * Permisos:
 * - ADMIN, SUPERVISOR, MECANICO, JEFE_TALLER pueden ver y subir
 * - Otros roles según configuración
 */
export default function EvidencesPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [evidencias, setEvidencias] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filtros
  const [filtroTipo, setFiltroTipo] = useState<string>("");
  const [filtroOT, setFiltroOT] = useState<string>("");
  const [filtroFechaDesde, setFiltroFechaDesde] = useState<string>("");
  const [filtroFechaHasta, setFiltroFechaHasta] = useState<string>("");
  const [busqueda, setBusqueda] = useState<string>("");

  const canUpload = hasRole(["ADMIN", "SUPERVISOR", "MECANICO", "JEFE_TALLER", "GUARDIA"]);

  const loadEvidencias = async () => {
    setLoading(true);
    try {
      let url = "/api/proxy/work/evidencias/?";
      const params = new URLSearchParams();
      
      if (filtroTipo) params.append("tipo", filtroTipo);
      if (filtroOT) params.append("ot", filtroOT);
      if (filtroFechaDesde) params.append("subido_en__gte", filtroFechaDesde);
      if (filtroFechaHasta) params.append("subido_en__lte", filtroFechaHasta);
      
      url += params.toString();

      const r = await fetch(url, {
        credentials: "include",
      });

      if (!r.ok) {
        throw new Error(`HTTP ${r.status}`);
      }

      const data = await r.json();
      let results = data.results || data || [];

      // Filtrar por búsqueda en descripción
      if (busqueda) {
        results = results.filter((e: any) =>
          e.descripcion?.toLowerCase().includes(busqueda.toLowerCase()) ||
          e.tipo?.toLowerCase().includes(busqueda.toLowerCase())
        );
      }

      setEvidencias(results);
    } catch (error) {
      console.error("Error al cargar evidencias:", error);
      toast.error("Error al cargar evidencias");
      setEvidencias([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvidencias();
  }, [filtroTipo, filtroOT, filtroFechaDesde, filtroFechaHasta]);

  const handleSearch = () => {
    loadEvidencias();
  };

  return (
    <RoleGuard allow={["ADMIN", "SUPERVISOR", "MECANICO", "JEFE_TALLER", "EJECUTIVO", "COORDINADOR_ZONA"]}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Evidencias</h1>
          {canUpload && (
            <Link
              href="/evidences/upload"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              + Subir Evidencia
            </Link>
          )}
        </div>

        {/* Filtros */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tipo
              </label>
              <select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="FOTO">FOTO</option>
                <option value="PDF">PDF</option>
                <option value="HOJA_CALCULO">Hoja de Cálculo</option>
                <option value="DOCUMENTO">Documento</option>
                <option value="COMPRIMIDO">Comprimido</option>
                <option value="OTRO">Otro</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha Desde
              </label>
              <input
                type="date"
                value={filtroFechaDesde}
                onChange={(e) => setFiltroFechaDesde(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha Hasta
              </label>
              <input
                type="date"
                value={filtroFechaHasta}
                onChange={(e) => setFiltroFechaHasta(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Búsqueda
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  placeholder="Buscar en descripción..."
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                />
                <button
                  onClick={handleSearch}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Buscar
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Lista de evidencias */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando evidencias...</p>
            </div>
          </div>
        ) : evidencias.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <p className="text-gray-500 dark:text-gray-400">No se encontraron evidencias</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {evidencias.map((e) => (
              <div
                key={e.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition p-4"
              >
                {e.tipo === "FOTO" && (
                  <img
                    src={e.url}
                    className="w-full h-48 object-cover rounded mb-3"
                    alt={e.descripcion || "Evidencia"}
                    onError={(img) => {
                      (img.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                )}
                {e.tipo !== "FOTO" && (
                  <div className="w-full h-48 bg-gray-100 dark:bg-gray-700 rounded mb-3 flex items-center justify-center">
                    <span className="text-6xl">
                      {e.tipo === "PDF" && "📄"}
                      {e.tipo === "HOJA_CALCULO" && "📊"}
                      {e.tipo === "DOCUMENTO" && "📝"}
                      {e.tipo === "COMPRIMIDO" && "📦"}
                      {!["PDF", "HOJA_CALCULO", "DOCUMENTO", "COMPRIMIDO"].includes(e.tipo) && "📎"}
                    </span>
                  </div>
                )}
                
                <div className="space-y-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                    {e.descripcion || e.tipo || "Evidencia"}
                  </h3>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                    <span>{e.tipo}</span>
                    <span>{new Date(e.subido_en).toLocaleDateString()}</span>
                  </div>

                  {e.ot ? (
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      OT: <Link href={`/workorders/${e.ot}`} className="text-blue-600 dark:text-blue-400 hover:underline">
                        #{typeof e.ot === 'string' ? e.ot.substring(0, 8) : e.ot.id?.substring(0, 8) || 'N/A'}
                      </Link>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 dark:text-gray-500 italic">
                      Evidencia general
                    </div>
                  )}

                  <a
                    href={e.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-center rounded-lg transition-colors"
                  >
                    Ver/Descargar
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </RoleGuard>
  );
}


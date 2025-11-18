/**
 * Página de listado de Órdenes de Trabajo.
 * 
 * Esta página muestra todas las órdenes de trabajo con:
 * - Filtros por estado (ABIERTA, EN_EJECUCION, EN_QA, CERRADA, TODAS)
 * - Tabla con información de cada OT
 * - Paginación
 * - Acciones según permisos (Ver, Editar, Eliminar)
 * 
 * Características:
 * - Carga datos desde API con paginación
 * - Filtrado por estado
 * - Colores diferenciados por estado
 * - Responsive y soporte dark mode
 * 
 * Dependencias:
 * - next/link: Para navegación
 * - @/components/ToastContainer: Para notificaciones
 * - @/store/auth: Para verificar permisos
 * - @/components/Pagination: Para paginación
 * 
 * Relaciones:
 * - Usa: /api/proxy/work/ordenes/ (endpoint del backend)
 * - Navega a: /workorders/{id} (detalle), /workorders/{id}/edit, /workorders/create
 */

"use client";  // Componente de cliente (usa hooks y estado)

import { useEffect, useState } from "react";  // Hooks de React
import Link from "next/link";  // Componente de Next.js para navegación
import { useToast } from "@/components/ToastContainer";  // Hook para notificaciones
import { useAuth } from "@/store/auth";  // Store de autenticación
import Pagination from "@/components/Pagination";  // Componente de paginación

/**
 * Componente principal de la página de OT.
 * 
 * Estados:
 * - rows: Array de órdenes de trabajo
 * - loading: Indica si está cargando datos
 * - estado: Filtro de estado actual (ABIERTA, EN_EJECUCION, etc.)
 * - currentPage: Página actual
 * - totalPages: Total de páginas
 * - totalItems: Total de items
 */
export default function WorkOrdersPage() {
  // Estado: lista de órdenes de trabajo
  const [rows, setRows] = useState<any[]>([]);
  
  // Estado: indica si está cargando
  const [loading, setLoading] = useState(true);
  
  // Estado: filtro de estado (por defecto: ABIERTA)
  const [estado, setEstado] = useState("ABIERTA");
  
  // Estado: página actual (por defecto: 1)
  const [currentPage, setCurrentPage] = useState(1);
  
  // Estado: total de páginas
  const [totalPages, setTotalPages] = useState(1);
  
  // Estado: total de items
  const [totalItems, setTotalItems] = useState(0);
  
  // Items por página (configuración)
  const itemsPerPage = 20;
  
  // Hook para mostrar notificaciones
  const toast = useToast();
  
  // Hook para verificar permisos
  const { hasRole } = useAuth();

  /**
   * Función para cargar órdenes de trabajo desde la API.
   * 
   * Parámetros:
   * - page: Número de página a cargar (por defecto: 1)
   * 
   * Proceso:
   * 1. Construye URL con filtros y paginación
   * 2. Hace petición a la API
   * 3. Parsea respuesta JSON
   * 4. Actualiza estados (rows, totalPages, totalItems)
   * 5. Maneja errores con notificaciones
   * 
   * Manejo de errores:
   * - 401: No autorizado (limpia datos)
   * - Otros: Muestra error y limpia datos
   */
  const load = async (page: number = 1) => {
    setLoading(true);

    // Construir URL con filtros y paginación
    const url = estado
      ? `/api/proxy/work/ordenes/?estado=${estado}&page=${page}&page_size=${itemsPerPage}`
      : `/api/proxy/work/ordenes/?page=${page}&page_size=${itemsPerPage}`;

    try {
      // Hacer petición a la API
      const r = await fetch(url, { credentials: "include" });
      
      // Manejar errores HTTP
      if (!r.ok) {
        if (r.status === 401) {
          console.warn("No autorizado para ver órdenes de trabajo");
          setRows([]);
          return;
        }
        throw new Error(`HTTP ${r.status}`);
      }
      
      // Leer respuesta como texto primero (para manejar respuestas vacías)
      const text = await r.text();
      if (!text || text.trim() === "") {
        setRows([]);
        return;
      }
      
      // Parsear JSON
      const j = JSON.parse(text);
      
      // Extraer datos (puede venir en results o directamente)
      const data = j.results ?? j ?? [];
      setRows(Array.isArray(data) ? data : []);
      
      // Calcular paginación
      setTotalPages(Math.ceil((j.count || data.length) / itemsPerPage));
      setTotalItems(j.count || data.length);
    } catch (e) {
      console.error("Error cargando OT:", e);
      toast.error("Error al cargar órdenes de trabajo");
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Efecto: Recargar cuando cambia el filtro de estado.
   * 
   * Se ejecuta cuando cambia `estado`.
   * Resetea a página 1 y recarga datos.
   */
  useEffect(() => {
    setCurrentPage(1);  // Resetear a página 1
    load(1);
  }, [estado]);

  /**
   * Efecto: Recargar cuando cambia la página.
   * 
   * Se ejecuta cuando cambia `currentPage`.
   * Carga la nueva página.
   */
  useEffect(() => {
    load(currentPage);
  }, [currentPage]);

  /**
   * Verificar si el usuario puede editar OT.
   * 
   * Solo ADMIN y SUPERVISOR pueden editar/eliminar.
   */
  const canEdit = hasRole(["ADMIN", "SUPERVISOR"]);

  /**
   * Obtener color CSS según el estado de la OT.
   * 
   * Parámetros:
   * - estado: Estado de la OT (ABIERTA, EN_EJECUCION, etc.)
   * 
   * Retorna:
   * - String con clases CSS de Tailwind
   * 
   * Colores:
   * - ABIERTA: Azul
   * - EN_EJECUCION: Amarillo
   * - EN_QA: Morado
   * - CERRADA: Verde
   * - Otros: Gris
   */
  const getEstadoColor = (estado: string) => {
    const colors: Record<string, string> = {
      ABIERTA: "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400",
      EN_EJECUCION: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400",
      EN_QA: "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400",
      CERRADA: "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400",
    };
    return colors[estado] || "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300";
  };

  /**
   * Render de la página.
   * 
   * Estructura:
   * - Header con título y botón "Nueva Orden" (si tiene permisos)
   * - Filtros por estado
   * - Tabla con órdenes de trabajo
   * - Paginación
   */
  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Órdenes de Trabajo</h1>
        {canEdit && (
          <Link 
            href="/workorders/create" 
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium shadow-sm hover:shadow"
          >
            + Nueva Orden
          </Link>
        )}
      </div>

      {/* Filtros por estado */}
      <div className="flex gap-3 mb-6 flex-wrap">
        {["ABIERTA", "EN_EJECUCION", "EN_QA", "CERRADA", "TODAS"].map((e) => (
          <button
            key={e}
            onClick={() => setEstado(e === "TODAS" ? "" : e)}  // "" significa todas
            className={`px-4 py-2 rounded-lg transition-colors font-medium ${
              estado === e || (estado === "" && e === "TODAS")
                ? "bg-blue-600 text-white"  // Botón activo
                : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
            }`}
          >
            {e}
          </button>
        ))}
      </div>

      {/* Tabla de órdenes de trabajo */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        <table className="min-w-full">
          {/* Encabezados de tabla */}
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">ID</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Patente</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Estado</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Tipo</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Responsable</th>
              <th className="p-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Apertura</th>
              <th className="p-3 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">Acciones</th>
            </tr>
          </thead>

          {/* Cuerpo de tabla */}
          <tbody>
            {/* Estado de carga */}
            {loading ? (
              <tr>
                <td colSpan={7} className="p-8 text-center">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando...</span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              // Sin datos
              <tr>
                <td colSpan={7} className="p-8 text-center text-gray-500 dark:text-gray-400">
                  No hay órdenes de trabajo registradas.
                </td>
              </tr>
            ) : (
              // Filas de datos
              rows.map((ot) => (
                <tr key={ot.id} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="p-3 font-medium text-gray-900 dark:text-white">#{ot.id}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{ot.vehiculo?.patente || "N/A"}</td>
                  <td className="p-3">
                    {/* Badge de estado con color */}
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getEstadoColor(ot.estado)}`}>
                      {ot.estado}
                    </span>
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{ot.tipo || "N/A"}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {ot.responsable ? `${ot.responsable.first_name} ${ot.responsable.last_name}` : "Sin responsable"}
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {new Date(ot.apertura).toLocaleDateString()}
                  </td>
                  <td className="p-3">
                    {/* Acciones */}
                    <div className="flex items-center justify-end gap-2">
                      {/* Ver detalle */}
                      <Link 
                        href={`/workorders/${ot.id}`} 
                        className="px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        Ver
                      </Link>
                      {canEdit && (
                        <>
                          {/* Editar (solo si tiene permisos) */}
                          <Link 
                            href={`/workorders/${ot.id}/edit`} 
                            className="px-3 py-1 text-sm text-green-600 dark:text-green-400 hover:underline"
                          >
                            Editar
                          </Link>
                          {/* Eliminar (solo si está ABIERTA y tiene permisos) */}
                          {ot.estado === "ABIERTA" && (
                            <Link 
                              href={`/workorders/${ot.id}/delete`} 
                              className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:underline"
                            >
                              Eliminar
                            </Link>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        
        {/* Componente de paginación */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
        />
      </div>
    </div>
  );
}

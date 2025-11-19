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
 * Vista de Auditoría de Vehículos para Subgerente Nacional.
 * 
 * Muestra:
 * - Historial completo de mantenciones
 * - Evidencias (solo lectura)
 * - OTs agrupadas por tipo
 * 
 * Permisos:
 * - Solo EJECUTIVO, ADMIN pueden acceder
 */
export default function SubgerenteAuditoriaPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [vehiculos, setVehiculos] = useState<any[]>([]);
  const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState<any>(null);
  const [historial, setHistorial] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargarVehiculos();
  }, []);

  const cargarVehiculos = async () => {
    setLoading(true);
    try {
      const response = await fetch(ENDPOINTS.VEHICLES, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        setVehiculos(data.results || data || []);
      }
    } catch (error) {
      console.error("Error al cargar vehículos:", error);
      toast.error("Error al cargar vehículos");
    } finally {
      setLoading(false);
    }
  };

  const cargarHistorial = async (vehiculoId: string) => {
    try {
      const response = await fetch(`${ENDPOINTS.VEHICLES}${vehiculoId}/historial/`, {
        method: "GET",
        ...withSession(),
      });

      if (response.ok) {
        const data = await response.json();
        setHistorial(data.results || data || []);
        
        const vehiculo = vehiculos.find((v) => v.id === vehiculoId);
        setVehiculoSeleccionado(vehiculo);
      }
    } catch (error) {
      console.error("Error al cargar historial:", error);
      toast.error("Error al cargar historial");
    }
  };

  return (
    <RoleGuard allow={["EJECUTIVO", "ADMIN"]}>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Auditoría de Vehículos
          </h1>
          <Link
            href="/subgerente/dashboard"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de Vehículos */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Vehículos
                </h2>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
                {vehiculos.map((vehiculo) => (
                  <button
                    key={vehiculo.id}
                    onClick={() => cargarHistorial(vehiculo.id)}
                    className={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${
                      vehiculoSeleccionado?.id === vehiculo.id ? "bg-blue-50 dark:bg-blue-900/20" : ""
                    }`}
                  >
                    <div className="font-medium text-gray-900 dark:text-white">
                      {vehiculo.patente}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {vehiculo.marca} {vehiculo.modelo}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Historial del Vehículo Seleccionado */}
          <div className="lg:col-span-2">
            {vehiculoSeleccionado ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                  Historial Completo - {vehiculoSeleccionado.patente}
                </h2>
                {historial.length > 0 ? (
                  <div className="space-y-4">
                    {historial.map((evento) => (
                      <div
                        key={evento.id}
                        className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {evento.tipo_evento}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(evento.creado_en || evento.fecha_ingreso).toLocaleString()}
                          </span>
                        </div>
                        {evento.descripcion && (
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {evento.descripcion}
                          </p>
                        )}
                        {evento.ot && (
                          <Link
                            href={`/workorders/${evento.ot.id}`}
                            className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 mt-2 inline-block"
                          >
                            Ver OT #{evento.ot.id.slice(0, 8)}
                          </Link>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400">
                    No hay historial registrado para este vehículo.
                  </p>
                )}
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  Selecciona un vehículo para ver su historial completo.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


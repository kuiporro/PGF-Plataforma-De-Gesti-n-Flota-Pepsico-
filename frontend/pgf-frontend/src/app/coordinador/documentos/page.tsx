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
 * Vista de Soporte de Documentos para Coordinador.
 * 
 * Muestra:
 * - Subida de facturas
 * - Subida de guías
 * - Subida de informes administrativos
 * - Gestión de documentos por vehículo
 * 
 * Permisos:
 * - Solo COORDINADOR_ZONA, ADMIN pueden acceder
 */
export default function CoordinadorDocumentosPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [vehiculos, setVehiculos] = useState<any[]>([]);
  const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState<string>("");
  const [tipoDocumento, setTipoDocumento] = useState("FACTURA");
  const [loading, setLoading] = useState(true);

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

  return (
    <RoleGuard allow={["COORDINADOR_ZONA", "ADMIN"]}>
      <div className="p-6 max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Soporte de Documentos
          </h1>
          <Link
            href="/coordinador"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        {/* Formulario de Subida */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Subir Documento Administrativo
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Vehículo
              </label>
              <select
                value={vehiculoSeleccionado}
                onChange={(e) => setVehiculoSeleccionado(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Seleccionar vehículo...</option>
                {vehiculos.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.patente} - {v.marca} {v.modelo}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Tipo de Documento
              </label>
              <select
                value={tipoDocumento}
                onChange={(e) => setTipoDocumento(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="FACTURA">Factura</option>
                <option value="GUIA">Guía de Despacho</option>
                <option value="INFORME">Informe Administrativo</option>
                <option value="PADRON">Padrón</option>
                <option value="SEGURO">Seguro</option>
                <option value="PERMISO">Permiso de Circulación</option>
              </select>
            </div>
            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Archivo
              </label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium">
              Subir Documento
            </button>
          </div>
        </div>

        {/* Información */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-sm text-blue-800 dark:text-blue-300">
            <strong>Nota:</strong> Los documentos administrativos se almacenan como evidencias 
            generales asociadas al vehículo. Use el sistema de evidencias para gestionar estos documentos.
          </p>
        </div>
      </div>
    </RoleGuard>
  );
}


"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";
import Link from "next/link";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";

/**
 * Página para que el Guardia registre el ingreso de vehículos al taller.
 * 
 * Esta página permite:
 * - Registrar ingreso de vehículo por patente
 * - Crear vehículo si no existe
 * - Generar OT automáticamente
 * - Agregar observaciones y kilometraje
 * 
 * Permisos:
 * - Solo GUARDIA puede acceder
 */
export default function IngresoVehiculoPage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [form, setForm] = useState({
    patente: "",
    marca: "",
    modelo: "",
    anio: "",
    vin: "",
    observaciones: "",
    kilometraje: "",
    motivo: "",
    prioridad: "MEDIA",
    zona: "",
    site: "",
    chofer_nombre: "",
    chofer_rut: "",
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [ingresoRegistrado, setIngresoRegistrado] = useState<{ id: string; ot_generada?: any } | null>(null);

  const canAccess = hasRole(["GUARDIA", "ADMIN"]);

  if (!canAccess) {
    return (
      <RoleGuard allow={["GUARDIA", "ADMIN"]}>
        <div></div>
      </RoleGuard>
    );
  }

  const handleChange = (field: string, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    // Validar patente (requerida)
    if (!form.patente.trim()) {
      setErrors({ patente: "La patente es requerida" });
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/proxy/vehicles/ingreso/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          patente: form.patente.trim().toUpperCase(),
          marca: form.marca.trim() || undefined,
          modelo: form.modelo.trim() || undefined,
          anio: form.anio ? parseInt(form.anio) : undefined,
          vin: form.vin.trim() || undefined,
          observaciones: form.observaciones.trim() || undefined,
          kilometraje: form.kilometraje ? parseInt(form.kilometraje) : undefined,
          motivo: form.motivo.trim() || undefined,
          prioridad: form.prioridad,
          zona: form.zona.trim() || undefined,
          site: form.site.trim() || undefined,
          chofer_nombre: form.chofer_nombre.trim() || undefined,
          chofer_rut: form.chofer_rut.trim() || undefined,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Manejar errores de validación
        if (data.patente) {
          setErrors({ patente: data.patente[0] });
        } else if (data.detail) {
          toast.error(data.detail);
        } else {
          toast.error("Error al registrar ingreso");
        }
        setLoading(false);
        return;
      }

      // Éxito
      toast.success("Ingreso registrado correctamente. OT creada automáticamente.");
      
      // Guardar información del ingreso para mostrar botón de PDF
      setIngresoRegistrado({
        id: data.id,
        ot_generada: data.ot_generada,
      });
      
      // Si se generó una OT, mostrar información
      if (data.ot_generada) {
        toast.success(`OT #${data.ot_generada.id} creada con estado ${data.ot_generada.estado}`);
      }

      // Limpiar formulario
      setForm({
        patente: "",
        marca: "",
        modelo: "",
        anio: "",
        vin: "",
        observaciones: "",
        kilometraje: "",
        motivo: "",
        prioridad: "MEDIA",
        zona: "",
        site: "",
        chofer_nombre: "",
        chofer_rut: "",
      });
    } catch (error) {
      console.error("Error al registrar ingreso:", error);
      toast.error("Error al registrar ingreso del vehículo");
      setLoading(false);
    }
  };

  return (
    <RoleGuard allow={["GUARDIA", "ADMIN"]}>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Registrar Ingreso de Vehículo
          </h1>
          <Link
            href="/vehicles"
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            ← Volver
          </Link>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800 dark:text-blue-300">
            <strong>Nota:</strong> Al registrar el ingreso de un vehículo, se creará automáticamente 
            una Orden de Trabajo (OT) con estado <strong>ABIERTA</strong>. Si el vehículo no existe 
            en el sistema, se creará automáticamente.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
          {/* Información del Vehículo */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Información del Vehículo
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Patente (requerida) */}
              <div className="md:col-span-2">
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Patente <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={form.patente}
                  onChange={(e) => handleChange("patente", e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                    errors.patente ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                  }`}
                  placeholder="ABC123"
                  required
                />
                {errors.patente && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.patente}</p>
                )}
              </div>

              {/* Marca */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Marca
                </label>
                <input
                  type="text"
                  value={form.marca}
                  onChange={(e) => handleChange("marca", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Toyota"
                />
              </div>

              {/* Modelo */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Modelo
                </label>
                <input
                  type="text"
                  value={form.modelo}
                  onChange={(e) => handleChange("modelo", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Hilux"
                />
              </div>

              {/* Año */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Año
                </label>
                <input
                  type="number"
                  value={form.anio}
                  onChange={(e) => handleChange("anio", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="2020"
                  min="1900"
                  max="2100"
                />
              </div>

              {/* VIN */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  VIN (Número de Chasis)
                </label>
                <input
                  type="text"
                  value={form.vin}
                  onChange={(e) => handleChange("vin", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="123456789"
                />
              </div>
            </div>
          </div>

          {/* Información del Ingreso */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Información del Ingreso
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Motivo (para la OT) */}
              <div className="md:col-span-2">
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Motivo del Ingreso (para la OT)
                </label>
                <textarea
                  value={form.motivo}
                  onChange={(e) => handleChange("motivo", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  rows={3}
                  placeholder="Ej: Reparación de parachoques, Mantención preventiva, etc."
                />
              </div>

              {/* Observaciones */}
              <div className="md:col-span-2">
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Observaciones
                </label>
                <textarea
                  value={form.observaciones}
                  onChange={(e) => handleChange("observaciones", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  rows={3}
                  placeholder="Observaciones adicionales sobre el estado del vehículo..."
                />
              </div>

              {/* Kilometraje */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Kilometraje
                </label>
                <input
                  type="number"
                  value={form.kilometraje}
                  onChange={(e) => handleChange("kilometraje", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="50000"
                  min="0"
                />
              </div>

              {/* Prioridad */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Prioridad de la OT
                </label>
                <select
                  value={form.prioridad}
                  onChange={(e) => handleChange("prioridad", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="ALTA">Alta</option>
                  <option value="MEDIA">Media</option>
                  <option value="BAJA">Baja</option>
                </select>
              </div>

              {/* Zona */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Zona
                </label>
                <input
                  type="text"
                  value={form.zona}
                  onChange={(e) => handleChange("zona", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Zona Norte"
                />
              </div>

              {/* Site */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Site
                </label>
                <input
                  type="text"
                  value={form.site}
                  onChange={(e) => handleChange("site", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="SITE_TEST"
                />
              </div>
            </div>
          </div>

          {/* Información del Chofer */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Información del Chofer (Opcional)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Nombre del Chofer */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Nombre del Chofer
                </label>
                <input
                  type="text"
                  value={form.chofer_nombre}
                  onChange={(e) => handleChange("chofer_nombre", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Juan Pérez"
                />
              </div>

              {/* RUT del Chofer */}
              <div>
                <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  RUT del Chofer
                </label>
                <input
                  type="text"
                  value={form.chofer_rut}
                  onChange={(e) => handleChange("chofer_rut", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="12345678-5"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Formato: 12345678-5 o 123456785
                </p>
              </div>
            </div>
          </div>

          {/* Botones */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={() => router.back()}
              className="flex-1 px-4 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Registrando...
                </span>
              ) : (
                "Registrar Ingreso y Crear OT"
              )}
            </button>
          </div>
        </form>

        {/* Botón para descargar PDF del ticket */}
        {ingresoRegistrado && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              ✓ Ingreso Registrado Exitosamente
            </h3>
            <div className="space-y-3">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                El ingreso ha sido registrado correctamente. Puedes descargar el ticket en PDF.
              </p>
              {ingresoRegistrado.ot_generada && (
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <strong>OT Generada:</strong> #{ingresoRegistrado.ot_generada.id.slice(0, 8)} - Estado: {ingresoRegistrado.ot_generada.estado}
                </p>
              )}
              <div className="flex gap-3">
                <button
                  onClick={async () => {
                    try {
                      const response = await fetch(
                        ENDPOINTS.VEHICLES_TICKET_INGRESO(ingresoRegistrado.id),
                        {
                          method: "GET",
                          ...withSession(),
                        }
                      );

                      if (!response.ok) {
                        toast.error("Error al generar el ticket PDF");
                        return;
                      }

                      // Descargar el PDF
                      const blob = await response.blob();
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `ticket_ingreso_${ingresoRegistrado.id.slice(0, 8)}.pdf`;
                      document.body.appendChild(a);
                      a.click();
                      window.URL.revokeObjectURL(url);
                      document.body.removeChild(a);
                      toast.success("Ticket PDF descargado correctamente");
                    } catch (error) {
                      console.error("Error al descargar PDF:", error);
                      toast.error("Error al descargar el ticket PDF");
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                >
                  📄 Descargar Ticket PDF
                </button>
                {ingresoRegistrado.ot_generada && (
                  <Link
                    href={`/workorders/${ingresoRegistrado.ot_generada.id}`}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
                  >
                    Ver OT Generada
                  </Link>
                )}
                <button
                  onClick={() => {
                    setIngresoRegistrado(null);
                  }}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
                >
                  Registrar Otro Ingreso
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </RoleGuard>
  );
}


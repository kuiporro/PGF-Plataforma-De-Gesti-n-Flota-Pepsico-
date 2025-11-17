"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import RoleGuard from "@/components/RoleGuard";

export default function CreateEmergency() {
  const router = useRouter();
  const toast = useToast();
  const [form, setForm] = useState({
    vehiculo: "",
    descripcion: "",
    ubicacion: "",
    prioridad: "MEDIA",
    zona: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [vehiculos, setVehiculos] = useState<any[]>([]);

  useEffect(() => {
    const loadVehicles = async () => {
      try {
        const r = await fetch("/api/proxy/vehicles/", { credentials: "include" });
        if (r.ok) {
          const data = await r.json();
          setVehiculos(data.results || data || []);
        }
      } catch (error) {
        console.error("Error cargando vehículos:", error);
      }
    };
    loadVehicles();
  }, []);

  const updateForm = (k: string, v: any) => {
    setForm({ ...form, [k]: v });
    if (errors[k]) {
      setErrors({ ...errors, [k]: "" });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!form.vehiculo) {
      newErrors.vehiculo = "El vehículo es requerido";
    }

    if (!form.descripcion.trim()) {
      newErrors.descripcion = "La descripción es requerida";
    }

    if (!form.ubicacion.trim()) {
      newErrors.ubicacion = "La ubicación es requerida";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error("Por favor corrige los errores en el formulario");
      return;
    }

    setLoading(true);

    try {
      const r = await fetch("/api/proxy/emergencies/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const text = await r.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { detail: text || "Error desconocido" };
      }

      if (!r.ok) {
        toast.error(data.detail || "Error al crear emergencia");
        if (data.errors) {
          setErrors(data.errors);
        }
        return;
      }

      toast.success("Emergencia creada correctamente");
      router.push("/emergencies");
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al crear emergencia");
    } finally {
      setLoading(false);
    }
  };

  return (
    <RoleGuard allow={["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA"]}>
      <div className="p-8 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Nueva Emergencia en Ruta</h1>

        <form onSubmit={submit} className="space-y-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Vehículo <span className="text-red-500">*</span>
            </label>
            <select
              value={form.vehiculo}
              onChange={(e) => updateForm("vehiculo", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg ${
                errors.vehiculo ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
              required
            >
              <option value="">Seleccionar vehículo...</option>
              {vehiculos.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.patente} - {v.marca} {v.modelo}
                </option>
              ))}
            </select>
            {errors.vehiculo && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.vehiculo}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Prioridad
            </label>
            <select
              value={form.prioridad}
              onChange={(e) => updateForm("prioridad", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="CRITICA">Crítica</option>
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
              <option value="BAJA">Baja</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Ubicación <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.ubicacion}
              onChange={(e) => updateForm("ubicacion", e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg ${
                errors.ubicacion ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
              placeholder="Dirección o ubicación donde ocurrió la emergencia"
              required
            />
            {errors.ubicacion && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.ubicacion}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Descripción <span className="text-red-500">*</span>
            </label>
            <textarea
              value={form.descripcion}
              onChange={(e) => updateForm("descripcion", e.target.value)}
              rows={6}
              className={`w-full px-3 py-2 border rounded-lg ${
                errors.descripcion ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
              placeholder="Describe detalladamente la emergencia..."
              required
            />
            {errors.descripcion && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.descripcion}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Zona
            </label>
            <input
              type="text"
              value={form.zona}
              onChange={(e) => updateForm("zona", e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
              style={{ backgroundColor: '#003DA5' }}
            >
              {loading ? "Guardando..." : "Crear Emergencia"}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </RoleGuard>
  );
}


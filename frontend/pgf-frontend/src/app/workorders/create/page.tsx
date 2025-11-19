"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ENDPOINTS } from "@/lib/constants";
import { useToast } from "@/components/ToastContainer";
import { validateWorkOrder } from "@/lib/validations";
import RoleGuard from "@/components/RoleGuard";
import { useAuth } from "@/store/auth";

export default function CreateWorkOrder() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();
  const [vehiculos, setVehiculos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [form, setForm] = useState({
    vehiculo: "",
    tipo: "MANTENCION",
    prioridad: "MEDIA",
    motivo: "",
  });

  const [items, setItems] = useState<any[]>([
    { tipo: "REPUESTO", descripcion: "", cantidad: 1, costo_unitario: 0 },
  ]);

  // -------------------------
  // CARGAR VEHÍCULOS
  // -------------------------
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
        toast.error("Error al cargar vehículos");
      }
    };
    loadVehicles();
  }, [toast]);

  // -------------------------
  // HANDLERS
  // -------------------------
  const updateForm = (k: string, v: any) => {
    setForm((f) => ({ ...f, [k]: v }));
  };

  const updateItem = (i: number, k: string, v: any) => {
    const newItems = [...items];
    newItems[i][k] = v;
    setItems(newItems);
  };

  const addItem = () => {
    setItems((x) => [
      ...x,
      { tipo: "REPUESTO", descripcion: "", cantidad: 1, costo_unitario: 0 },
    ]);
  };

  const removeItem = (i: number) => {
    setItems((x) => x.filter((_, idx) => idx !== i));
  };

  // -------------------------
  // ENVIAR FORMULARIO
  // -------------------------
  const submit = async () => {
    // Validar formulario
    const validation = validateWorkOrder({ ...form, items });
    if (!validation.isValid) {
      setErrors(validation.errors);
      toast.error("Por favor corrige los errores en el formulario");
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const r = await fetch("/api/work/ordenes/create", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          vehiculo: Number(form.vehiculo),
          items,
        }),
      });

      const text = await r.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { detail: text || "Error desconocido" };
      }

      if (!r.ok) {
        toast.error(data.detail || "Error al crear la orden de trabajo");
        if (data.errors) {
          setErrors(data.errors);
        }
        return;
      }

      toast.success("Orden de trabajo creada correctamente");
      router.push("/workorders");
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al crear la orden de trabajo");
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  // UI
  // -------------------------
  return (
    <RoleGuard allow={["JEFE_TALLER", "ADMIN", "GUARDIA"]}>
      <div className="p-8 space-y-12 max-w-3xl mx-auto">
        <div className="mb-4">
          <h1 className="text-3xl font-bold">Crear Orden de Trabajo</h1>
          {hasRole(["GUARDIA"]) && (
            <div className="mt-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                <strong>Nota para Guardia:</strong> Para crear una OT al registrar el ingreso de un vehículo, 
                usa la opción <Link href="/vehicles/ingreso" className="underline font-medium">"Registrar Ingreso"</Link> 
                que crea la OT automáticamente.
              </p>
            </div>
          )}
        </div>

      {/* Datos principales */}
      <section className="space-y-4 bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Datos principales</h2>

        <div>
          <label className="block mb-1 font-medium">Vehículo *</label>
          <select
            className={`input ${errors.vehiculo ? "border-red-500" : ""}`}
            value={form.vehiculo}
            onChange={(e) => {
              updateForm("vehiculo", e.target.value);
              if (errors.vehiculo) {
                setErrors({ ...errors, vehiculo: "" });
              }
            }}
          >
            <option value="">Selecciona un vehículo...</option>
            {vehiculos.map((v: any) => (
              <option key={v.id} value={v.id}>
                {v.patente} — {v.marca} {v.modelo}
              </option>
            ))}
          </select>
          {errors.vehiculo && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.vehiculo}</p>
          )}
        </div>

        <div>
          <label className="block mb-1">Tipo</label>
          <select
            className="input"
            value={form.tipo}
            onChange={(e) => updateForm("tipo", e.target.value)}
          >
            <option value="MANTENCION">Mantención</option>
            <option value="REPARACION">Reparación</option>
            <option value="OTRO">Otro</option>
          </select>
        </div>

        <div>
          <label className="block mb-1">Prioridad</label>
          <select
            className="input"
            value={form.prioridad}
            onChange={(e) => updateForm("prioridad", e.target.value)}
          >
            <option value="ALTA">Alta</option>
            <option value="MEDIA">Media</option>
            <option value="BAJA">Baja</option>
          </select>
        </div>

        <div>
          <label className="block mb-1 font-medium">Motivo *</label>
          <textarea
            className={`input h-32 ${errors.motivo ? "border-red-500" : ""}`}
            value={form.motivo}
            onChange={(e) => {
              updateForm("motivo", e.target.value);
              if (errors.motivo) {
                setErrors({ ...errors, motivo: "" });
              }
            }}
            placeholder="Describe el motivo de la orden de trabajo..."
          />
          {errors.motivo && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.motivo}</p>
          )}
        </div>
      </section>

      {/* Items */}
      <section className="space-y-4 bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Items</h2>

        {items.map((item, i) => (
          <div key={i} className="border p-4 rounded space-y-3">
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block mb-1 text-sm font-medium">Tipo</label>
                <select
                  className="input"
                  value={item.tipo}
                  onChange={(e) => updateItem(i, "tipo", e.target.value)}
                >
                  <option value="REPUESTO">Repuesto</option>
                  <option value="MANO_OBRA">Mano de obra</option>
                </select>
              </div>

              <div className="flex-1">
                <label className="block mb-1 text-sm font-medium">Cantidad *</label>
                <input
                  type="number"
                  min="1"
                  className={`input ${errors[`items.${i}.cantidad`] ? "border-red-500" : ""}`}
                  value={item.cantidad}
                  onChange={(e) => {
                    updateItem(i, "cantidad", Number(e.target.value));
                    const key = `items.${i}.cantidad`;
                    if (errors[key]) {
                      const newErrors = { ...errors };
                      delete newErrors[key];
                      setErrors(newErrors);
                    }
                  }}
                />
                {errors[`items.${i}.cantidad`] && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                    {errors[`items.${i}.cantidad`]}
                  </p>
                )}
              </div>

              <div className="flex-1">
                <label className="block mb-1 text-sm font-medium">Costo unitario *</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className={`input ${errors[`items.${i}.costo_unitario`] ? "border-red-500" : ""}`}
                  value={item.costo_unitario}
                  onChange={(e) => {
                    updateItem(i, "costo_unitario", Number(e.target.value));
                    const key = `items.${i}.costo_unitario`;
                    if (errors[key]) {
                      const newErrors = { ...errors };
                      delete newErrors[key];
                      setErrors(newErrors);
                    }
                  }}
                />
                {errors[`items.${i}.costo_unitario`] && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                    {errors[`items.${i}.costo_unitario`]}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block mb-1 text-sm font-medium">Descripción *</label>
              <input
                className={`input w-full ${errors[`items.${i}.descripcion`] ? "border-red-500" : ""}`}
                value={item.descripcion}
                onChange={(e) => {
                  updateItem(i, "descripcion", e.target.value);
                  const key = `items.${i}.descripcion`;
                  if (errors[key]) {
                    const newErrors = { ...errors };
                    delete newErrors[key];
                    setErrors(newErrors);
                  }
                }}
                placeholder="Descripción del item..."
              />
              {errors[`items.${i}.descripcion`] && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                  {errors[`items.${i}.descripcion`]}
                </p>
              )}
            </div>

            {items.length > 1 && (
              <button
                className="text-red-600 underline"
                onClick={() => removeItem(i)}
              >
                Eliminar item
              </button>
            )}
          </div>
        ))}

        <button className="btn" onClick={addItem}>
          + Agregar item
        </button>
      </section>

      <div className="flex gap-4">
        <button
          type="button"
          onClick={() => router.back()}
          className="flex-1 px-4 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
        >
          Cancelar
        </button>
        <button
          type="button"
          className="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={submit}
          disabled={loading}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creando...
            </span>
          ) : (
            "Crear Orden de Trabajo"
          )}
        </button>
      </div>
      </div>
    </RoleGuard>
  );
}

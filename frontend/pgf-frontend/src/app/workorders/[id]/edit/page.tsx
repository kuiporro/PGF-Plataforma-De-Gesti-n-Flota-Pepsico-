"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { validateWorkOrder } from "@/lib/validations";
import RoleGuard from "@/components/RoleGuard";

export default function EditWorkOrder() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const toast = useToast();

  const [vehiculos, setVehiculos] = useState<any[]>([]);
  const [form, setForm] = useState<any>(null);
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const load = async () => {
      try {
        // Cargar vehículos
        const vehiclesRes = await fetch("/api/proxy/vehicles/", { credentials: "include" });
        if (vehiclesRes.ok) {
          const vehiclesData = await vehiclesRes.json();
          setVehiculos(vehiclesData.results || vehiclesData || []);
        }

        // Cargar OT
        const otRes = await fetch(`/api/proxy/work/ordenes/${id}/`, {
          credentials: "include",
        });

        if (!otRes.ok) {
          toast.error("Error al cargar la orden de trabajo");
          router.push("/workorders");
          return;
        }

        const text = await otRes.text();
        if (!text || text.trim() === "") {
          toast.error("Orden de trabajo no encontrada");
          router.push("/workorders");
          return;
        }

        const data = JSON.parse(text);
        setForm({
          vehiculo: String(data.vehiculo?.id || ""),
          tipo: data.tipo || "MANTENCION",
          prioridad: data.prioridad || "MEDIA",
          motivo: data.motivo || "",
        });
        setItems(data.items || []);
      } catch (e) {
        console.error("Error:", e);
        toast.error("Error al cargar la orden de trabajo");
        router.push("/workorders");
      } finally {
        setLoading(false);
      }
    };

    if (id) load();
  }, [id, router, toast]);

  const updateForm = (k: string, v: any) => {
    setForm({ ...form, [k]: v });
    if (errors[k]) {
      setErrors({ ...errors, [k]: "" });
    }
  };

  const updateItem = (i: number, k: string, v: any) => {
    const newItems = [...items];
    newItems[i][k] = v;
    setItems(newItems);
    const key = `items.${i}.${k}`;
    if (errors[key]) {
      const newErrors = { ...errors };
      delete newErrors[key];
      setErrors(newErrors);
    }
  };

  const addItem = () => {
    setItems([...items, { tipo: "REPUESTO", descripcion: "", cantidad: 1, costo_unitario: 0 }]);
  };

  const removeItem = (i: number) => {
    setItems(items.filter((_, idx) => idx !== i));
  };

  const submit = async () => {
    // Validar formulario
    const validation = validateWorkOrder({ ...form, items });
    if (!validation.isValid) {
      setErrors(validation.errors);
      toast.error("Por favor corrige los errores en el formulario");
      return;
    }

    setSaving(true);
    setErrors({});

    try {
      const r = await fetch(`/api/proxy/work/ordenes/${id}/`, {
        method: "PUT",
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
        toast.error(data.detail || "Error al actualizar la orden de trabajo");
        if (data.errors) {
          setErrors(data.errors);
        }
        return;
      }

      toast.success("Orden de trabajo actualizada correctamente");
      router.push(`/workorders/${id}`);
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al actualizar la orden de trabajo");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !form) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <RoleGuard allow={["JEFE_TALLER", "ADMIN"]}>
      <div className="p-8 space-y-12 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Editar Orden de Trabajo #{id}</h1>

        {/* Datos principales */}
        <section className="space-y-4 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Datos principales</h2>

          <div>
            <label className="block mb-1 font-medium text-gray-700 dark:text-gray-300">Vehículo *</label>
            <select
              className={`input w-full ${errors.vehiculo ? "border-red-500" : ""}`}
              value={form.vehiculo}
              onChange={(e) => {
                updateForm("vehiculo", e.target.value);
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
            <label className="block mb-1 font-medium text-gray-700 dark:text-gray-300">Tipo</label>
            <select
              className="input w-full"
              value={form.tipo}
              onChange={(e) => updateForm("tipo", e.target.value)}
            >
              <option value="MANTENCION">Mantención</option>
              <option value="REPARACION">Reparación</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700 dark:text-gray-300">Prioridad</label>
            <select
              className="input w-full"
              value={form.prioridad}
              onChange={(e) => updateForm("prioridad", e.target.value)}
            >
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
              <option value="BAJA">Baja</option>
            </select>
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700 dark:text-gray-300">Motivo *</label>
            <textarea
              className={`input h-32 ${errors.motivo ? "border-red-500" : ""}`}
              value={form.motivo}
              onChange={(e) => {
                updateForm("motivo", e.target.value);
              }}
              placeholder="Describe el motivo de la orden de trabajo..."
            />
            {errors.motivo && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.motivo}</p>
            )}
          </div>
        </section>

        {/* Items */}
        <section className="space-y-4 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Items</h2>

          {items.map((item, i) => (
            <div key={i} className="border dark:border-gray-700 p-4 rounded-lg space-y-3">
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Tipo</label>
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
                  <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Cantidad *</label>
                  <input
                    type="number"
                    min="1"
                    className={`input ${errors[`items.${i}.cantidad`] ? "border-red-500" : ""}`}
                    value={item.cantidad}
                    onChange={(e) => {
                      updateItem(i, "cantidad", Number(e.target.value));
                    }}
                  />
                  {errors[`items.${i}.cantidad`] && (
                    <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                      {errors[`items.${i}.cantidad`]}
                    </p>
                  )}
                </div>

                <div className="flex-1">
                  <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Costo unitario *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    className={`input ${errors[`items.${i}.costo_unitario`] ? "border-red-500" : ""}`}
                    value={item.costo_unitario}
                    onChange={(e) => {
                      updateItem(i, "costo_unitario", Number(e.target.value));
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
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Descripción *</label>
                <input
                  className={`input w-full ${errors[`items.${i}.descripcion`] ? "border-red-500" : ""}`}
                  value={item.descripcion}
                  onChange={(e) => {
                    updateItem(i, "descripcion", e.target.value);
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
                  type="button"
                  className="text-red-600 dark:text-red-400 hover:underline text-sm"
                  onClick={() => removeItem(i)}
                >
                  Eliminar item
                </button>
              )}
            </div>
          ))}

          <button
            type="button"
            className="btn w-full"
            onClick={addItem}
          >
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
            disabled={saving}
          >
            {saving ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
              </span>
            ) : (
              "Guardar Cambios"
            )}
          </button>
        </div>
      </div>
    </RoleGuard>
  );
}


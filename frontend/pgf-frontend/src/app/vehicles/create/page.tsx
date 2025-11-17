"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { validateVehicle } from "@/lib/validations";

export default function CreateVehicle() {
  const router = useRouter();
  const toast = useToast();
  const [form, setForm] = useState({
    patente: "",
    marca: "",
    modelo: "",
    anio: "",
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const update = (k: string, v: string) => {
    setForm({ ...form, [k]: v });
    // Limpiar error del campo cuando se modifica
    if (errors[k]) {
      setErrors({ ...errors, [k]: "" });
    }
  };

  async function save() {
    // Validar formulario
    const validation = validateVehicle(form);
    if (!validation.isValid) {
      setErrors(validation.errors);
      toast.error("Por favor corrige los errores en el formulario");
      return;
    }

    setSaving(true);
    setErrors({});

    try {
      const r = await fetch("/api/proxy/vehicles/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          anio: Number(form.anio),
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
        toast.error(data.detail || "Error al crear el vehículo");
        if (data.errors) {
          setErrors(data.errors);
        }
        return;
      }

      toast.success("Vehículo creado correctamente");
      router.push("/vehicles");
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al crear el vehículo");
    } finally {
      setSaving(false);
    }
  }

  const fields = [
    { key: "patente", label: "Patente", placeholder: "ABC123 o ABC-123", type: "text" },
    { key: "marca", label: "Marca", placeholder: "Ej: Toyota", type: "text" },
    { key: "modelo", label: "Modelo", placeholder: "Ej: Corolla", type: "text" },
    { key: "anio", label: "Año", placeholder: "Ej: 2020", type: "number" },
  ];

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Nuevo Vehículo</h1>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
        {fields.map((field) => (
          <div key={field.key}>
            <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              {field.label} *
            </label>
            <input
              type={field.type}
              placeholder={field.placeholder}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white dark:border-gray-600 transition-all ${
                errors[field.key] ? "border-red-500" : "border-gray-300"
              }`}
              value={(form as any)[field.key]}
              onChange={(e) => update(field.key, e.target.value)}
            />
            {errors[field.key] && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors[field.key]}</p>
            )}
          </div>
        ))}

        <div className="flex gap-4 pt-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="flex-1 px-4 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={save}
            disabled={saving}
            className="flex-1 px-4 py-3 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: '#003DA5' }}
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
              "Guardar"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

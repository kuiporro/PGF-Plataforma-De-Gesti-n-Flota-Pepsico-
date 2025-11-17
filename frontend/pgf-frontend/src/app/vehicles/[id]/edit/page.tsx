"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

export default function EditVehicle() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [form, setForm] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch(`/api/proxy/vehicles/${id}`)
      .then((r) => r.json())
      .then(setForm);
  }, [id]);

  if (!form) return <div className="p-6">Cargando...</div>;

  const update = (k: string, v: string) =>
    setForm({ ...form, [k]: v });

  async function save() {
    setSaving(true);

    const r = await fetch(`/api/proxy/vehicles/${id}`, {
      method: "PUT",
      body: JSON.stringify(form),
    });

    if (r.ok) router.push("/vehicles");
    setSaving(false);
  }

  async function remove() {
    if (!confirm("¿Eliminar vehículo?")) return;

    await fetch(`/api/proxy/vehicles/${id}`, { method: "DELETE" });
    router.push("/vehicles");
  }

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Editar Vehículo</h1>

      <div className="space-y-4">
        {["patente", "marca", "modelo", "anio"].map((f) => (
          <input
            key={f}
            placeholder={f.toUpperCase()}
            className="w-full border p-3 rounded"
            value={form[f]}
            onChange={(e) => update(f, e.target.value)}
          />
        ))}

        <button
          onClick={save}
          disabled={saving}
          className="w-full bg-blue-600 text-white py-3 rounded"
        >
          Guardar Cambios
        </button>

        <button
          onClick={remove}
          className="w-full bg-red-600 text-white py-3 rounded mt-2"
        >
          Eliminar Vehículo
        </button>
      </div>
    </div>
  );
}

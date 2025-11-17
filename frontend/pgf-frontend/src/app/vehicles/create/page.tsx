"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateVehicle() {
  const router = useRouter();
  const [form, setForm] = useState({
    patente: "",
    marca: "",
    modelo: "",
    anio: "",
  });
  const [saving, setSaving] = useState(false);

  const update = (k: string, v: string) =>
    setForm({ ...form, [k]: v });

  async function save() {
    setSaving(true);
    const r = await fetch("/api/proxy/vehicles", {
      method: "POST",
      body: JSON.stringify(form),
    });

    if (r.ok) router.push("/vehicles");
    setSaving(false);
  }

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Nuevo Vehículo</h1>

      <div className="space-y-4">
        {["patente", "marca", "modelo", "anio"].map((f) => (
          <input
            key={f}
            placeholder={f.toUpperCase()}
            className="w-full border p-3 rounded"
            value={(form as any)[f]}
            onChange={(e) => update(f, e.target.value)}
          />
        ))}

        <button
          onClick={save}
          disabled={saving}
          className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700"
        >
          {saving ? "Guardando..." : "Guardar"}
        </button>
      </div>
    </div>
  );
}

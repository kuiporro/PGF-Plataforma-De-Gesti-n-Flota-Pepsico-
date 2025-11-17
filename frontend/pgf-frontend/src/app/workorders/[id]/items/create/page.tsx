"use client";

import { useState } from "react";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function CreateItem({ params }: any) {
  const otId = params.id;
  const router = useRouter();

  const [form, setForm] = useState({
    tipo: "SERVICIO",
    descripcion: "",
    cantidad: 1,
    costo_unitario: 0,
    ot: otId,
  });

  const [error, setError] = useState("");

  const handleChange = (e: any) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const save = async () => {
    setError("");

    const r = await fetch(ENDPOINTS.WORK_ITEMS, {
      method: "POST",
      ...withSession(),
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    if (!r.ok) {
      setError("Error guardando ítem.");
      return;
    }

    router.push(`/workorders/${otId}/items`);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold">Agregar Ítem</h1>

      {error && <p className="text-red-600">{error}</p>}

      <div className="max-w-lg space-y-3">

        <div>
          <label className="block font-semibold">Tipo</label>
          <select
            name="tipo"
            value={form.tipo}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          >
            <option value="SERVICIO">SERVICIO</option>
            <option value="REPUESTO">REPUESTO</option>
          </select>
        </div>

        <div>
          <label className="block font-semibold">Descripción</label>
          <input
            name="descripcion"
            value={form.descripcion}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          />
        </div>

        <div>
          <label className="block font-semibold">Cantidad</label>
          <input
            type="number"
            name="cantidad"
            value={form.cantidad}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          />
        </div>

        <div>
          <label className="block font-semibold">Costo Unitario</label>
          <input
            type="number"
            name="costo_unitario"
            value={form.costo_unitario}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          />
        </div>
      </div>

      <button
        onClick={save}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Guardar
      </button>
    </div>
  );
}

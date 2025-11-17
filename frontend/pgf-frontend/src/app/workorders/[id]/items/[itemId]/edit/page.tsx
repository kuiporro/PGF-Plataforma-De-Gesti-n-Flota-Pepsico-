"use client";

import { useEffect, useState } from "react";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function EditItem({ params }: any) {
  const otId = params.id;
  const itemId = params.itemId;

  const router = useRouter();

  const [form, setForm] = useState<any>(null);

  const load = async () => {
    const r = await fetch(`${ENDPOINTS.WORK_ITEMS}${itemId}/`, withSession());
    const j = await r.json();
    setForm(j);
  };

  useEffect(() => {
    load();
  }, []);

  const save = async () => {
    const r = await fetch(`${ENDPOINTS.WORK_ITEMS}${itemId}/`, {
      method: "PUT",
      ...withSession(),
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    if (!r.ok) {
      alert("Error guardando ítem");
      return;
    }

    router.push(`/workorders/${otId}/items`);
  };

  if (!form) return <p className="p-6">Cargando...</p>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold">Editar Ítem</h1>

      <div className="max-w-lg space-y-3">
        <div>
          <label className="block font-semibold">Descripción</label>
          <input
            name="descripcion"
            value={form.descripcion}
            onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>

        <div>
          <label className="block font-semibold">Cantidad</label>
          <input
            type="number"
            name="cantidad"
            value={form.cantidad}
            onChange={(e) => setForm({ ...form, cantidad: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>

        <div>
          <label className="block font-semibold">Costo Unitario</label>
          <input
            type="number"
            name="costo_unitario"
            value={form.costo_unitario}
            onChange={(e) =>
              setForm({ ...form, costo_unitario: e.target.value })
            }
            className="border p-2 rounded w-full"
          />
        </div>
      </div>

      <button
        onClick={save}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Guardar cambios
      </button>
    </div>
  );
}

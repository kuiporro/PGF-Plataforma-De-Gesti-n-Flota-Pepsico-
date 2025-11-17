"use client";

import { useState, useEffect } from "react";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";

export default function CreateWorkOrder() {
  const [vehiculos, setVehiculos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
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
    fetch(ENDPOINTS.VEHICLES, withSession())
      .then((r) => r.json())
      .then((data) => {
        setVehiculos(data.results || data);
      });
  }, []);

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
    setLoading(true);

    const r = await fetch(ENDPOINTS.WORK_ORDERS, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        vehiculo: Number(form.vehiculo),
        items,
      }),
    });

    const data = await r.json();
    setLoading(false);

    if (!r.ok) {
      alert("Error: " + JSON.stringify(data));
      return;
    }

    alert("Orden creada correctamente!");
    window.location.href = "/workorders";
  };

  // -------------------------
  // UI
  // -------------------------
  return (
    <div className="p-8 space-y-12 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold">Crear Orden de Trabajo</h1>

      {/* Datos principales */}
      <section className="space-y-4 bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Datos principales</h2>

        <div>
          <label className="block mb-1">Vehículo</label>
          <select
            className="input"
            value={form.vehiculo}
            onChange={(e) => updateForm("vehiculo", e.target.value)}
          >
            <option value="">Selecciona...</option>
            {vehiculos.map((v: any) => (
              <option key={v.id} value={v.id}>
                {v.patente} — {v.marca} {v.modelo}
              </option>
            ))}
          </select>
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
          <label className="block mb-1">Motivo</label>
          <textarea
            className="input h-32"
            value={form.motivo}
            onChange={(e) => updateForm("motivo", e.target.value)}
          />
        </div>
      </section>

      {/* Items */}
      <section className="space-y-4 bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Items</h2>

        {items.map((item, i) => (
          <div key={i} className="border p-4 rounded space-y-3">
            <div className="flex gap-4">
              <div className="flex-1">
                <label>Tipo</label>
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
                <label>Cantidad</label>
                <input
                  type="number"
                  className="input"
                  value={item.cantidad}
                  onChange={(e) => updateItem(i, "cantidad", e.target.value)}
                />
              </div>

              <div className="flex-1">
                <label>Costo unitario</label>
                <input
                  type="number"
                  className="input"
                  value={item.costo_unitario}
                  onChange={(e) =>
                    updateItem(i, "costo_unitario", Number(e.target.value))
                  }
                />
              </div>
            </div>

            <div>
              <label>Descripción</label>
              <input
                className="input w-full"
                value={item.descripcion}
                onChange={(e) =>
                  updateItem(i, "descripcion", e.target.value)
                }
              />
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

      <button
        className="btn-primary w-full py-3 text-lg"
        onClick={submit}
        disabled={loading}
      >
        {loading ? "Creando..." : "Crear Orden de Trabajo"}
      </button>
    </div>
  );
}

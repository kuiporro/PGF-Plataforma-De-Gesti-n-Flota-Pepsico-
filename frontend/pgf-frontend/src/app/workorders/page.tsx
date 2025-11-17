"use client";

import { useEffect, useState } from "react";

export default function WorkOrdersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [estado, setEstado] = useState("ABIERTA");

  const load = async () => {
    setLoading(true);

    const url = estado
      ? `/api/proxy/work/ordenes/?estado=${estado}`
      : `/api/proxy/work/ordenes/`;

    try {
      const r = await fetch(url, { credentials: "include" });
      const j = await r.json();
      const data = j.results ?? [];
      setRows(data);
    } catch (e) {
      console.error("Error cargando OT:", e);
      setRows([]);
    }

    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [estado]);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Órdenes de Trabajo</h1>

      <div className="flex gap-3 mb-4">
        {["ABIERTA", "EN_EJECUCION", "EN_QA", "CERRADA", "TODAS"].map((e) => (
          <button
            key={e}
            onClick={() => setEstado(e === "TODAS" ? "" : e)}
            className={`filter-btn ${estado === e || (estado === "" && e === "TODAS") ? "active" : ""}`}
          >
            {e}
          </button>
        ))}
      </div>

      <table className="min-w-full bg-white shadow rounded">
        <thead>
          <tr className="border-b">
            <th className="p-3 text-left">Patente</th>
            <th className="p-3 text-left">Estado</th>
            <th className="p-3 text-left">Responsable</th>
            <th className="p-3 text-left">Apertura</th>
            <th className="p-3 text-left">Acciones</th>
          </tr>
        </thead>

        <tbody>
          {loading ? (
            <tr><td colSpan={5} className="p-6 text-center">Cargando...</td></tr>
          ) : rows.length === 0 ? (
            <tr><td colSpan={5} className="p-6 text-center">No hay órdenes de trabajo registradas.</td></tr>
          ) : (
            rows.map((ot) => (
              <tr key={ot.id} className="border-t">
                <td className="p-3">{ot.vehiculo?.patente}</td>
                <td className="p-3">{ot.estado}</td>
                <td className="p-3">{ot.responsable?.first_name}</td>
                <td className="p-3">{new Date(ot.apertura).toLocaleDateString()}</td>
                <td className="p-3">
                  <a href={`/workorders/${ot.id}`} className="text-blue-600 underline">Ver</a>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

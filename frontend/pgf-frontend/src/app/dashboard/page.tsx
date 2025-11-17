"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [kpi, setKpi] = useState({
    abiertas: 0,
    ejecucion: 0,
    qa: 0,
    cerradas: 0,
    ultimas: [],
    vehiculos: 0,
    usuarios: 0,
  });

  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      setLoading(true);

      // Helper function to safely fetch and parse JSON
      const safeFetch = async (url: string, defaultValue: any = {}) => {
        try {
          const response = await fetch(url);
          if (!response.ok) {
            console.warn(`Failed to fetch ${url}:`, response.status);
            return defaultValue;
          }
          const text = await response.text();
          if (!text || text.trim() === "") {
            return defaultValue;
          }
          try {
            return JSON.parse(text);
          } catch (e) {
            console.error(`Invalid JSON from ${url}:`, text);
            return defaultValue;
          }
        } catch (error) {
          console.error(`Error fetching ${url}:`, error);
          return defaultValue;
        }
      };

      const ab = await safeFetch("/api/proxy/work/ordenes/?estado=ABIERTA", { count: 0, length: 0 });
      const en = await safeFetch("/api/proxy/work/ordenes/?estado=EN_EJECUCION", { count: 0, length: 0 });
      const qa = await safeFetch("/api/proxy/work/ordenes/?estado=EN_QA", { count: 0, length: 0 });
      const ce = await safeFetch("/api/proxy/work/ordenes/?estado=CERRADA", { count: 0, length: 0 });
      const ult = await safeFetch("/api/proxy/work/ordenes/?limit=5", { results: [] });
      const veh = await safeFetch("/api/proxy/vehicles/", { count: 0, length: 0 });
      const usr = await safeFetch("/api/proxy/users/", { count: 0 });

      setKpi({
        abiertas: ab.count ?? ab.length ?? 0,
        ejecucion: en.count ?? en.length ?? 0,
        qa: qa.count ?? qa.length ?? 0,
        cerradas: ce.count ?? ce.length ?? 0,
        ultimas: ult.results ?? [],
        vehiculos: veh.count ?? veh.length ?? 0,
        usuarios: usr.count ?? 0,
      });
    } catch (e) {
      console.error("Error cargando dashboard:", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const total = kpi.abiertas + kpi.ejecucion + kpi.qa + kpi.cerradas || 1;

  return (
    <div className="p-6 space-y-8 dashboard-container">

      <h1 className="text-3xl font-bold mb-4">Dashboard General</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard title="Abiertas" value={kpi.abiertas} color="bg-blue-500" />
        <KpiCard title="En Ejecución" value={kpi.ejecucion} color="bg-yellow-500" />
        <KpiCard title="En QA" value={kpi.qa} color="bg-purple-500" />
        <KpiCard title="Cerradas" value={kpi.cerradas} color="bg-green-600" />
      </div>

      <section className="bg-white shadow rounded p-6">
        <h2 className="text-xl font-semibold mb-4">Estado de OT</h2>

        <div className="space-y-4">
          {[["ABIERTA", kpi.abiertas, "bg-blue-500"],
            ["EN EJECUCIÓN", kpi.ejecucion, "bg-yellow-500"],
            ["EN QA", kpi.qa, "bg-purple-500"],
            ["CERRADA", kpi.cerradas, "bg-green-600"],
          ].map(([label, value, color]) => (
            <div key={label}>
              <div className="flex justify-between text-sm mb-1">
                <span>{label}</span>
                <span>{value}</span>
              </div>
              <div className="w-full bg-gray-200 h-3 rounded">
                <div className={`${color} h-3 rounded`} style={{ width: `${((value as number) / total) * 100}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MiniCard title="Total Vehículos" value={kpi.vehiculos} />
        {kpi.usuarios > 0 && <MiniCard title="Usuarios Registrados" value={kpi.usuarios} />}
      </div>

      <section className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Últimas Órdenes</h2>

        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100 text-left">
              <th className="p-3">ID</th>
              <th className="p-3">Estado</th>
              <th className="p-3">Vehículo</th>
              <th className="p-3">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {kpi.ultimas.length === 0 ? (
              <tr>
                <td className="p-3 text-center" colSpan={4}>No hay datos.</td>
              </tr>
            ) : (
              kpi.ultimas.map((o: any) => (
                <tr key={o.id} className="border-t">
                  <td className="p-3">{o.id}</td>
                  <td className="p-3">{o.estado}</td>
                  <td className="p-3">{o.vehiculo?.patente ?? "-"}</td>
                  <td className="p-3">{new Date(o.apertura).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function KpiCard({ title, value, color }: any) {
  return (
    <div className="p-6 bg-white rounded shadow flex flex-col card-animated">
      <span className="text-gray-600">{title}</span>
      <span className={`text-4xl font-bold mt-2 ${color} text-white px-3 py-1 rounded`}>
        {value}
      </span>
    </div>
  );
}

function MiniCard({ title, value }: any) {
  return (
    <div className="bg-white p-6 shadow rounded card-animated">
      <h3 className="text-lg font-semibold text-gray-700">{title}</h3>
      <p className="text-3xl font-bold mt-2">{value}</p>
    </div>
  );
}

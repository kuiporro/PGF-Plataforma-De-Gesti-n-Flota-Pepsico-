"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function VehiclesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const r = await fetch("/api/proxy/vehicles/");
      const j = await r.json();
      setRows(j.results ?? []);
    } catch (e) {
      console.error("Error cargando vehículos", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Vehículos</h1>
        <Link href="/vehicles/create" className="btn-primary">+ Nuevo Vehículo</Link>
      </div>

      <div className="bg-white shadow rounded">
        <table className="min-w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3">Patente</th>
              <th className="p-3">Marca</th>
              <th className="p-3">Modelo</th>
              <th className="p-3">Año</th>
              <th className="p-3"></th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="p-4 text-center">Cargando...</td></tr>
            ) : rows.length === 0 ? (
              <tr><td colSpan={5} className="p-4 text-center">No hay vehículos registrados.</td></tr>
            ) : (
              rows.map((v) => (
                <tr key={v.id} className="border-t">
                  <td className="p-3">{v.patente}</td>
                  <td className="p-3">{v.marca}</td>
                  <td className="p-3">{v.modelo}</td>
                  <td className="p-3">{v.anio}</td>
                  <td className="p-3 text-right">
                    <Link href={`/vehicles/${v.id}/edit`} className="action-link">Editar</Link>
                    <Link href={`/vehicles/${v.id}`} className="action-link ml-3">Ver</Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

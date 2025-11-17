"use client";

import { useEffect, useState } from "react";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import Link from "next/link";

export default function EvidencesPage({ params }: any) {
  const otId = params.id;

  const [rows, setRows] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);

  const load = async () => {
    const r = await fetch(`${ENDPOINTS.EVIDENCES}?ot=${otId}`, withSession());
    const j = await r.json();
    setRows(j.results ?? j);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">

      {/* HEADER */}
      <div className="flex justify-between items-center">
        <h1 className="h1">Evidencias</h1>

        <Link
          href={`/workorders/${otId}/evidences/upload`}
          className="btn btn-primary"
        >
          + Subir Evidencia
        </Link>
      </div>

      {/* GRID DE EVIDENCIAS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {rows.map((e) => (
          <div
            key={e.id}
            className="card cursor-pointer hover:shadow-lg transition"
            onClick={() => setSelected(e)}
          >
            {e.tipo === "FOTO" && (
              <img
                src={e.url}
                className="w-full h-32 object-cover rounded"
                alt="Evidencia"
              />
            )}

            <p className="mt-2 font-semibold">{e.descripcion || e.tipo}</p>
            <p className="text-xs text-gray-500">{e.subido_en}</p>
          </div>
        ))}
      </div>

      {/* MODAL DE PREVIEW */}
      {selected && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-xl w-full space-y-4">

            <h2 className="h2">{selected.descripcion || selected.tipo}</h2>

            {selected.tipo === "FOTO" ? (
              <img
                src={selected.url}
                className="rounded max-h-[300px] mx-auto"
              />
            ) : (
              <a
                href={selected.url}
                target="_blank"
                className="btn btn-primary w-full text-center"
              >
                Abrir archivo
              </a>
            )}

            <button
              onClick={() => setSelected(null)}
              className="btn btn-secondary w-full"
            >
              Cerrar
            </button>

          </div>
        </div>
      )}
    </div>
  );
}

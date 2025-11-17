import { cookies } from "next/headers";
import { ENDPOINTS } from "@/lib/constants";

// =============================
// Obtener OT desde el backend
// =============================
async function obtenerOT(id: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("pgf_token")?.value;
  if (!token) return null;

  const headers = { Authorization: `Bearer ${token}` };

  const r = await fetch(`${ENDPOINTS.WORK_ORDERS}${id}/`, {
    headers,
    cache: "no-store",
  });

  if (!r.ok) return null;
  return r.json();
}

// =============================
// Acciones (transiciones estado)
// =============================

async function moveEstado(id: string, accion: string) {
  "use server";

  const cookieStore = await cookies();
  const token = cookieStore.get("pgf_token")?.value;
  if (!token) return { ok: false };

  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const r = await fetch(`${ENDPOINTS.WORK_ORDERS}${id}/${accion}/`, {
    method: "POST",
    headers,
  });

  return { ok: r.ok };
}

// =============================
// Vista principal
// =============================
export default async function WorkOrderDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const p = await params;
  const id = p.id;

  const ot = await obtenerOT(id);
  if (!ot)
    return (
      <div className="p-8">
        <h1>No se encontró la Orden de Trabajo</h1>
      </div>
    );

  // seguridad
  const evidencias = ot.evidencias ?? [];
  const items = ot.items ?? [];

  // =============================
  // Botones según estado:
  // ABIERTA → EN_EJECUCION → EN_QA → CERRADA
  // =============================

  const BotonesEstado = () => {
    const estado = ot.estado;

    return (
      <form action="">
        <div className="flex gap-3 mt-4">
          {estado === "ABIERTA" && (
            <button
              formAction={async () => {
                "use server";
                await moveEstado(id, "en-ejecucion");
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Iniciar Ejecución
            </button>
          )}

          {estado === "EN_EJECUCION" && (
            <button
              formAction={async () => {
                "use server";
                await moveEstado(id, "en-qa");
              }}
              className="px-4 py-2 bg-yellow-500 text-white rounded"
            >
              Enviar a QA
            </button>
          )}

          {estado === "EN_QA" && (
            <button
              formAction={async () => {
                "use server";
                await moveEstado(id, "cerrar");
              }}
              className="px-4 py-2 bg-green-600 text-white rounded"
            >
              Cerrar OT
            </button>
          )}
        </div>
      </form>
    );
  };

  return (
    <div className="p-8 space-y-10">
      <h1 className="text-3xl font-bold mb-6">Orden de Trabajo #{id}</h1>

      {/* === Estado y botones === */}
      <section className="p-6 bg-white shadow rounded space-y-2">
        <h2 className="text-xl font-bold mb-4">Estado Actual</h2>
        <p className="text-lg">
          <strong>Estado:</strong> {ot.estado}
        </p>

        {/* botones de transición */}
        <BotonesEstado />
      </section>

      {/* Información general */}
      <section className="p-6 bg-white rounded shadow space-y-2">
        <h2 className="text-xl font-bold mb-3">Información General</h2>

        <p><strong>Responsable:</strong>{" "}
          {ot.responsable
            ? `${ot.responsable.first_name} ${ot.responsable.last_name}`
            : "Sin responsable"}
        </p>

        <p><strong>Apertura:</strong> {new Date(ot.apertura).toLocaleString()}</p>

        {ot.cierre && (
          <p><strong>Cierre:</strong> {new Date(ot.cierre).toLocaleString()}</p>
        )}
      </section>

      {/* Vehículo */}
      <section className="p-6 bg-white rounded shadow">
        <h2 className="text-xl font-bold mb-3">Vehículo</h2>
        <p><strong>Patente:</strong> {ot.vehiculo?.patente}</p>
        <p><strong>Marca:</strong> {ot.vehiculo?.marca}</p>
        <p><strong>Modelo:</strong> {ot.vehiculo?.modelo}</p>
        <p><strong>Año:</strong> {ot.vehiculo?.anio}</p>
      </section>

      {/* Items */}
      <section className="p-6 bg-white rounded shadow">
        <h2 className="text-xl font-bold mb-3">Items</h2>

        {items.length === 0 ? (
          <p>No hay items.</p>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2">Tipo</th>
                <th className="p-2">Descripción</th>
                <th className="p-2">Cantidad</th>
                <th className="p-2">Costo</th>
              </tr>
            </thead>
            <tbody>
              {items.map((i: any) => (
                <tr key={i.id} className="border-b">
                  <td className="p-2">{i.tipo}</td>
                  <td className="p-2">{i.descripcion}</td>
                  <td className="p-2">{i.cantidad}</td>
                  <td className="p-2">$ {i.costo_unitario}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* Evidencias */}
      <section className="p-6 bg-white rounded shadow">
        <h2 className="text-xl font-bold mb-3">Evidencias</h2>

        {evidencias.length === 0 ? (
          <p>No hay evidencias.</p>
        ) : (
          <ul className="space-y-2">
            {evidencias.map((e: any) => (
              <li key={e.id}>
                <a
                  href={e.url}
                  className="text-blue-600 underline"
                  target="_blank"
                >
                  {e.descripcion || e.tipo}
                </a>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

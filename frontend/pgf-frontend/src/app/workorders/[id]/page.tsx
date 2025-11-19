import { cookies } from "next/headers";
import { ENDPOINTS } from "@/lib/constants";
import WorkOrderDetailClient from "./WorkOrderDetailClient";

// =============================
// Obtener OT desde el backend
// =============================
async function obtenerOT(id: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("pgf_access")?.value;
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
// Vista principal (Server Component)
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

  return <WorkOrderDetailClient ot={ot} id={id} />;
}

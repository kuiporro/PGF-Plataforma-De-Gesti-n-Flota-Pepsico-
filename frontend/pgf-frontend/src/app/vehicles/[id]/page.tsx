import { cookies } from "next/headers";
import { ENDPOINTS } from "@/lib/constants";

async function loadVehicle(id: string) {
  const token = (await cookies()).get("pgf_token")?.value;
  if (!token) return null;

  const r = await fetch(`${ENDPOINTS.VEHICLES}${id}/`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!r.ok) return null;
  return r.json();
}

export default async function VehicleDetail({ params }: { params: any }) {
  const v = await loadVehicle(params.id);

  if (!v)
    return (
      <div className="p-8">
        <h1>No existe este vehículo.</h1>
      </div>
    );

  return (
    <div className="p-8 space-y-4">
      <h1 className="text-3xl font-bold">Vehículo {v.patente}</h1>

      <p><strong>Marca:</strong> {v.marca}</p>
      <p><strong>Modelo:</strong> {v.modelo}</p>
      <p><strong>Año:</strong> {v.anio}</p>
      <p><strong>Estado:</strong> {v.estado}</p>

      <a
        className="inline-block mt-6 px-4 py-2 bg-blue-600 text-white rounded"
        href={`/vehicles/${v.id}/edit`}
      >
        Editar
      </a>
    </div>
  );
}

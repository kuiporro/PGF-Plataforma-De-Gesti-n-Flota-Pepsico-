"use client";

import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function DeleteVehicle({ params }: any) {
  const id = params.id;
  const router = useRouter();

  const remove = async () => {
    const r = await fetch(`${ENDPOINTS.VEHICLES}${id}/`, {
      method: "DELETE",
      ...withSession(),
    });

    router.push("/vehicles");
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-red-600">
        Eliminar Vehículo
      </h1>

      <p>¿Seguro que deseas eliminar este vehículo? Esta acción no se puede deshacer.</p>

      <button
        onClick={remove}
        className="px-4 py-2 bg-red-600 text-white rounded"
      >
        Sí, eliminar
      </button>

      <button
        onClick={() => router.push("/vehicles")}
        className="px-4 py-2 bg-gray-300 rounded"
      >
        Cancelar
      </button>
    </div>
  );
}

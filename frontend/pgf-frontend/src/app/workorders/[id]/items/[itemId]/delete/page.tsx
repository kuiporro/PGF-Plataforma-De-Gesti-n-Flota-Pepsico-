"use client";

import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function DeleteItem({ params }: any) {
  const otId = params.id;
  const itemId = params.itemId;
  const router = useRouter();

  const remove = async () => {
    await fetch(`${ENDPOINTS.WORK_ITEMS}${itemId}/`, {
      method: "DELETE",
      ...withSession(),
    });

    router.push(`/workorders/${otId}/items`);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold text-red-600">Eliminar Ítem</h1>

      <p>¿Seguro que deseas eliminar este ítem?</p>

      <button
        onClick={remove}
        className="px-4 py-2 bg-red-600 text-white rounded"
      >
        Sí, eliminar
      </button>

      <button
        onClick={() => router.back()}
        className="px-4 py-2 bg-gray-300 rounded"
      >
        Cancelar
      </button>
    </div>
  );
}

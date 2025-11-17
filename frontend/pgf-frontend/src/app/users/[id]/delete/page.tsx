"use client";

import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function DeleteUser({ params }: any) {
  const id = params.id;
  const router = useRouter();

  const remove = async () => {
    await fetch(`${ENDPOINTS.USERS}${id}/`, {
      method: "DELETE",
      ...withSession(),
    });
    router.push("/users");
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-red-600">Eliminar Usuario</h1>

      <p>¿Seguro que deseas eliminar este usuario?</p>

      <div className="flex space-x-4 mt-4">
        <button
          onClick={remove}
          className="px-4 py-2 bg-red-600 text-white rounded"
        >
          Sí, eliminar
        </button>

        <button
          onClick={() => router.push("/users")}
          className="px-4 py-2 bg-gray-300 rounded"
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}

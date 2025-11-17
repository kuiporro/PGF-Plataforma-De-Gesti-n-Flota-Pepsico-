"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import ConfirmDialog from "@/components/ConfirmDialog";
import RoleGuard from "@/components/RoleGuard";

export default function DeleteUser() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();
  const toast = useToast();
  const [showConfirm, setShowConfirm] = useState(true);
  const [loading, setLoading] = useState(false);

  const remove = async () => {
    setLoading(true);
    try {
      const r = await fetch(`/api/proxy/users/${id}/`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!r.ok) {
        const text = await r.text();
        let data;
        try {
          data = JSON.parse(text);
        } catch {
          data = { detail: text || "Error desconocido" };
        }
        toast.error(data.detail || "Error al eliminar el usuario");
        return;
      }

      toast.success("Usuario eliminado correctamente");
      router.push("/users");
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al eliminar el usuario");
    } finally {
      setLoading(false);
      setShowConfirm(false);
    }
  };

  return (
    <RoleGuard allow={["ADMIN", "SUPERVISOR"]}>
      <ConfirmDialog
        isOpen={showConfirm}
        title="Eliminar Usuario"
        message="¿Estás seguro de que deseas eliminar este usuario? Esta acción no se puede deshacer."
        confirmText={loading ? "Eliminando..." : "Sí, eliminar"}
        cancelText="Cancelar"
        onConfirm={remove}
        onCancel={() => router.back()}
        type="danger"
      />
    </RoleGuard>
  );
}

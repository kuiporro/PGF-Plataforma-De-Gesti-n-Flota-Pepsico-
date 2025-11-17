"use client";

import { useEffect, useState } from "react";
import { ENDPOINTS, ALL_ROLES } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function EditUser({ params }: any) {
  const id = params.id;
  const router = useRouter();

  const [form, setForm] = useState<any>(null);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const r = await fetch(`${ENDPOINTS.USERS}${id}/`, withSession());
      const j = await r.json();
      setForm(j);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleChange = (e: any) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const save = async () => {
    setError("");
    try {
      const r = await fetch(`${ENDPOINTS.USERS}${id}/`, {
        method: "PUT",
        ...withSession(),
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!r.ok) {
        const j = await r.json();
        setError(JSON.stringify(j));
        return;
      }

      router.push("/users");
    } catch (e: any) {
      setError(e.message);
    }
  };

  if (!form) return <p className="p-6">Cargando...</p>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Editar Usuario</h1>

      {error && <p className="text-red-600">{error}</p>}

      <div className="space-y-3 max-w-xl">
        {["first_name", "last_name", "email", "username"].map((key) => (
          <div key={key}>
            <label className="block font-semibold capitalize">{key}</label>
            <input
              name={key}
              value={form[key] || ""}
              onChange={handleChange}
              className="border p-2 rounded w-full"
            />
          </div>
        ))}

        <div>
          <label className="block font-semibold">Rol</label>
          <select
            name="rol"
            value={form.rol}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          >
            {ALL_ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={save}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Guardar Cambios
      </button>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateUser() {
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    rol: "USER",
  });
  const [error, setError] = useState("");

  const submit = async (e: any) => {
    e.preventDefault();
    setError("");

    const r = await fetch("/api/proxy/users", {
      method: "POST",
      body: JSON.stringify(form),
    });

    if (!r.ok) {
      setError("Error al crear usuario");
      return;
    }

    router.push("/users");
  };

  return (
    <div className="page max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Crear Usuario</h1>

      {error && <div className="p-3 bg-red-100 text-red-700 mb-4">{error}</div>}

      <form onSubmit={submit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <input
          placeholder="Nombre"
          required
          className="input"
          value={form.first_name}
          onChange={(e) => setForm({ ...form, first_name: e.target.value })}
        />

        <input
          placeholder="Apellido"
          required
          className="input"
          value={form.last_name}
          onChange={(e) => setForm({ ...form, last_name: e.target.value })}
        />

        <input
          type="email"
          placeholder="Email"
          required
          className="input"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />

        <input
          type="password"
          placeholder="Contraseña"
          required
          className="input"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />

        <select
          className="input"
          value={form.rol}
          onChange={(e) => setForm({ ...form, rol: e.target.value })}
        >
          <option value="ADMIN">ADMIN</option>
          <option value="USER">USER</option>
        </select>

        <button className="btn-primary w-full">Crear</button>
      </form>
    </div>
  );
}

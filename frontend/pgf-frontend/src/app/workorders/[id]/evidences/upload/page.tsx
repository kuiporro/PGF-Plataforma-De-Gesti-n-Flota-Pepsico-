"use client";

import { useState } from "react";
import { ENDPOINTS } from "@/lib/constants";
import { withSession } from "@/lib/api.client";
import { useRouter } from "next/navigation";

export default function UploadEvidence({ params }: any) {
  const otId = params.id;
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [descripcion, setDescripcion] = useState("");
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");

  const onFileChange = (e: any) => {
    const f = e.target.files[0];
    setFile(f);

    if (f && f.type.startsWith("image/")) {
      setPreview(URL.createObjectURL(f));
    } else {
      setPreview("");
    }
  };

  const upload = async () => {
    if (!file) {
      setError("Selecciona un archivo");
      return;
    }

    setError("");

    // 1) solicitar presigned URL
    const r = await fetch(ENDPOINTS.EVIDENCE_PRESIGN, {
      method: "POST",
      ...withSession(),
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ot: otId,
        filename: file.name,
        content_type: file.type,
      }),
    });

    const data = await r.json();

    // 2) subir al S3 (LocalStack)
    const formData = new FormData();
    Object.entries(data.upload.fields).forEach(([k, v]) =>
      formData.append(k, v as string)
    );
    formData.append("file", file);

    await fetch(data.upload.url, {
      method: "POST",
      body: formData,
    });

    // 3) guardar metadata en el backend
    await fetch(ENDPOINTS.EVIDENCES, {
      method: "POST",
      ...withSession(),
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ot: otId,
        url: data.file_url,
        tipo: file.type.startsWith("image/") ? "FOTO" : "OTRO",
        descripcion,
      }),
    });

    router.push(`/workorders/${otId}/evidences`);
  };

  return (
    <div className="space-y-6">

      <h1 className="h1">Subir Evidencia</h1>

      <div className="card space-y-4 max-w-xl">

        <div>
          <label className="label">Descripción</label>
          <input
            className="input"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            placeholder="ej: Foto del daño en el motor"
          />
        </div>

        <div>
          <label className="label">Archivo</label>
          <input
            type="file"
            onChange={onFileChange}
            className="input"
            accept="image/*,.pdf"
          />
        </div>

        {preview && (
          <div className="mt-4">
            <p className="label">Vista previa</p>
            <img src={preview} className="rounded shadow max-h-60" />
          </div>
        )}

        {error && <p className="text-red-600">{error}</p>}

        <button onClick={upload} className="btn btn-primary w-full">
          Subir Evidencia
        </button>
      </div>
    </div>
  );
}

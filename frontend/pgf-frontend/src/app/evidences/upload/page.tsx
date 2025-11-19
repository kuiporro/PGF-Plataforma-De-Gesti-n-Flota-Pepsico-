"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";
import Link from "next/link";

/**
 * Página para subir evidencias generales.
 * 
 * Permite subir archivos sin necesidad de una OT específica.
 * La OT es opcional.
 * 
 * Soporta:
 * - Archivos hasta 3GB
 * - Imágenes, PDFs, documentos, etc.
 */
export default function UploadEvidencePage() {
  const router = useRouter();
  const toast = useToast();
  const { hasRole } = useAuth();

  const [file, setFile] = useState<File | null>(null);
  const [descripcion, setDescripcion] = useState("");
  const [tipo, setTipo] = useState<string>("FOTO");
  const [otId, setOtId] = useState<string>("");
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const canUpload = hasRole(["ADMIN", "SUPERVISOR", "MECANICO", "JEFE_TALLER", "GUARDIA"]);

  if (!canUpload) {
    return (
      <RoleGuard allow={["ADMIN", "SUPERVISOR", "MECANICO", "JEFE_TALLER", "GUARDIA"]}>
        <div></div>
      </RoleGuard>
    );
  }

  /**
   * Detecta el tipo de evidencia basado en la extensión del archivo.
   */
  const detectTipoEvidencia = (filename: string, mimeType: string): string => {
    const lowerName = filename.toLowerCase();
    
    // Imágenes
    if (mimeType.startsWith("image/") || /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(lowerName)) {
      return "FOTO";
    }
    
    // PDFs
    if (mimeType === "application/pdf" || lowerName.endsWith(".pdf")) {
      return "PDF";
    }
    
    // Hojas de cálculo
    if (
      mimeType.includes("spreadsheet") ||
      mimeType.includes("excel") ||
      /\.(xlsx|xls|csv)$/i.test(lowerName)
    ) {
      return "HOJA_CALCULO";
    }
    
    // Documentos Word
    if (
      mimeType.includes("word") ||
      mimeType.includes("document") ||
      /\.(doc|docx)$/i.test(lowerName)
    ) {
      return "DOCUMENTO";
    }
    
    // Archivos comprimidos
    if (
      mimeType.includes("zip") ||
      mimeType.includes("rar") ||
      mimeType.includes("7z") ||
      /\.(zip|rar|7z)$/i.test(lowerName)
    ) {
      return "COMPRIMIDO";
    }
    
    return "OTRO";
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setError("");

    // Detectar tipo automáticamente
    const detectedType = detectTipoEvidencia(selectedFile.name, selectedFile.type);
    setTipo(detectedType);

    // Preview para imágenes
    if (selectedFile.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview("");
    }
  };

  const upload = async () => {
    if (!file) {
      setError("Selecciona un archivo");
      return;
    }

    // Si se especificó OT, validar que sea un UUID válido
    if (otId && !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(otId)) {
      setError("El ID de OT no es válido (debe ser un UUID)");
      return;
    }

    setError("");
    setUploading(true);
    setUploadProgress(0);

    try {
      // 1) Solicitar presigned URL del backend
      const r = await fetch("/api/proxy/work/evidencias/presigned/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ot: otId || null, // OT es opcional
          filename: file.name,
          content_type: file.type || "application/octet-stream",
          file_size: file.size,
        }),
      });

      if (!r.ok) {
        const errorData = await r.json().catch(() => ({ detail: "Error al obtener URL de subida" }));
        throw new Error(errorData.detail || "Error al obtener URL de subida");
      }

      const data = await r.json();

      // 2) Subir archivo directamente a S3 con barra de progreso
      const formData = new FormData();
      Object.entries(data.upload.fields).forEach(([k, v]) =>
        formData.append(k, v as string)
      );
      formData.append("file", file);

      // Usar XMLHttpRequest para monitorear progreso
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener("progress", (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            setUploadProgress(percentComplete);
          }
        });

        xhr.addEventListener("load", () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve();
          } else {
            reject(new Error(`Error al subir archivo: ${xhr.statusText}`));
          }
        });

        xhr.addEventListener("error", () => {
          reject(new Error("Error de red al subir archivo"));
        });

        xhr.open("POST", data.upload.url);
        xhr.send(formData);
      });

      // 3) Guardar metadata en el backend
      const saveRes = await fetch("/api/proxy/work/evidencias/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ot: otId || null,
          url: data.file_url,
          tipo: tipo,
          descripcion: descripcion || "",
        }),
      });

      if (!saveRes.ok) {
        const errorData = await saveRes.json().catch(() => ({ detail: "Error al guardar evidencia" }));
        throw new Error(errorData.detail || "Error al guardar evidencia");
      }

      toast.success("Evidencia subida correctamente");
      router.push("/evidences");
    } catch (error) {
      console.error("Error al subir evidencia:", error);
      setError(error instanceof Error ? error.message : "Error al subir evidencia");
      toast.error(error instanceof Error ? error.message : "Error al subir evidencia");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <Link
          href="/evidences"
          className="text-blue-600 dark:text-blue-400 hover:underline mb-4 inline-block"
        >
          ← Volver a Evidencias
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Subir Evidencia</h1>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 max-w-2xl">
        {error && (
          <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-400 rounded">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {/* Archivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Archivo *
            </label>
            <input
              type="file"
              onChange={onFileChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              accept="image/*,application/pdf,.xlsx,.xls,.csv,.doc,.docx,.zip,.rar,.7z"
            />
            {file && (
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
          </div>

          {/* Preview de imagen */}
          {preview && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Vista Previa
              </label>
              <img
                src={preview}
                alt="Preview"
                className="max-w-full h-64 object-contain rounded-lg border border-gray-300 dark:border-gray-600"
              />
            </div>
          )}

          {/* OT (opcional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Orden de Trabajo (Opcional)
            </label>
            <input
              type="text"
              value={otId}
              onChange={(e) => setOtId(e.target.value)}
              placeholder="UUID de la OT (opcional)"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Deja vacío si la evidencia no está relacionada con una OT específica
            </p>
          </div>

          {/* Tipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tipo *
            </label>
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="FOTO">FOTO</option>
              <option value="PDF">PDF</option>
              <option value="HOJA_CALCULO">Hoja de Cálculo</option>
              <option value="DOCUMENTO">Documento</option>
              <option value="COMPRIMIDO">Comprimido</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Descripción
            </label>
            <textarea
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              rows={3}
              placeholder="Descripción de la evidencia..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Barra de progreso */}
          {uploading && (
            <div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 text-center">
                Subiendo... {Math.round(uploadProgress)}%
              </p>
            </div>
          )}

          {/* Botones */}
          <div className="flex gap-4">
            <button
              onClick={upload}
              disabled={uploading || !file}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? "Subiendo..." : "Subir Evidencia"}
            </button>
            <Link
              href="/evidences"
              className="px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors font-medium"
            >
              Cancelar
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}


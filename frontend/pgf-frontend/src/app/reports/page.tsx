"use client";

import { useState } from "react";
import { useToast } from "@/components/ToastContainer";
import { useAuth } from "@/store/auth";
import RoleGuard from "@/components/RoleGuard";

export default function ReportsPage() {
  const toast = useToast();
  const { hasRole } = useAuth();
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [loading, setLoading] = useState(false);

  const canAccess = hasRole(["EJECUTIVO", "ADMIN", "JEFE_TALLER", "SUPERVISOR", "COORDINADOR_ZONA"]);

  const downloadPDF = async (tipo: "diario" | "semanal" | "mensual") => {
    if (!canAccess) {
      toast.error("No tienes permisos para acceder a reportes");
      return;
    }

    setLoading(true);

    try {
      let url = `/api/proxy/reports/pdf/?tipo=${tipo}`;
      
      if (fechaInicio) {
        url += `&fecha_inicio=${fechaInicio}`;
      }
      if (fechaFin) {
        url += `&fecha_fin=${fechaFin}`;
      }

      const r = await fetch(url, {
        credentials: "include",
      });

      if (!r.ok) {
        const error = await r.json().catch(() => ({ detail: "Error al generar reporte" }));
        toast.error(error.detail || "Error al generar reporte");
        return;
      }

      // Descargar PDF
      const blob = await r.blob();
      const urlBlob = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = urlBlob;
      a.download = `reporte_${tipo}_${fechaInicio || new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(urlBlob);

      toast.success("Reporte descargado correctamente");
    } catch (error) {
      console.error("Error:", error);
      toast.error("Error al descargar reporte");
    } finally {
      setLoading(false);
    }
  };

  // Establecer fechas por defecto
  const setDefaultDates = (tipo: "semanal" | "mensual") => {
    const hoy = new Date();
    const fin = hoy.toISOString().split('T')[0];
    
    if (tipo === "semanal") {
      const inicio = new Date(hoy);
      inicio.setDate(hoy.getDate() - 7);
      setFechaInicio(inicio.toISOString().split('T')[0]);
    } else {
      const inicio = new Date(hoy);
      inicio.setMonth(hoy.getMonth() - 1);
      setFechaInicio(inicio.toISOString().split('T')[0]);
    }
    
    setFechaFin(fin);
  };

  return (
    <RoleGuard allow={["EJECUTIVO", "ADMIN", "JEFE_TALLER", "SUPERVISOR", "COORDINADOR_ZONA", "SPONSOR"]}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Reportes</h1>
          {/* Botón rápido de reporte diario */}
          <button
            onClick={() => {
              const hoy = new Date().toISOString().split('T')[0];
              setFechaInicio(hoy);
              downloadPDF("diario");
            }}
            disabled={loading}
            className="px-6 py-3 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
            style={{ backgroundColor: '#003DA5' }}
          >
            {loading ? "Generando..." : "📊 Reporte de Hoy"}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Reporte Diario */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Reporte Diario</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Genera un reporte con la operación del día seleccionado.
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha
              </label>
              <input
                type="date"
                value={fechaInicio}
                onChange={(e) => setFechaInicio(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <button
              onClick={() => downloadPDF("diario")}
              disabled={loading || !fechaInicio}
              className="w-full px-4 py-2 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: '#003DA5' }}
            >
              {loading ? "Generando..." : "Descargar PDF"}
            </button>
          </div>

          {/* Reporte Semanal */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Reporte Semanal</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Genera un reporte con la productividad de la última semana.
            </p>
            <div className="mb-4 space-y-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fecha Inicio
                </label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fecha Fin
                </label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <button
                onClick={() => setDefaultDates("semanal")}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                Últimos 7 días
              </button>
            </div>
            <button
              onClick={() => downloadPDF("semanal")}
              disabled={loading}
              className="w-full px-4 py-2 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: '#003DA5' }}
            >
              {loading ? "Generando..." : "Descargar PDF"}
            </button>
          </div>

          {/* Reporte Mensual */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Reporte Mensual</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Genera un reporte con la productividad del último mes.
            </p>
            <div className="mb-4 space-y-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fecha Inicio
                </label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fecha Fin
                </label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <button
                onClick={() => setDefaultDates("mensual")}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                Últimos 30 días
              </button>
            </div>
            <button
              onClick={() => downloadPDF("mensual")}
              disabled={loading}
              className="w-full px-4 py-2 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: '#003DA5' }}
            >
              {loading ? "Generando..." : "Descargar PDF"}
            </button>
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}


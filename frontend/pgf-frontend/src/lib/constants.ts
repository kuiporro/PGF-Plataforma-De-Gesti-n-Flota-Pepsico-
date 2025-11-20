// location: frontend/pgf-frontend/src/lib/constants.ts
export type Rol =
  | "ADMIN"
  | "SUPERVISOR"
  | "MECANICO"
  | "GUARDIA"
  | "RECEPCIONISTA"
  | "JEFE_TALLER"
  | "EJECUTIVO"
  | "SPONSOR"
  | "COORDINADOR_ZONA"
  | "CHOFER";

export const ALL_ROLES: Rol[] = [
  "ADMIN",
  "SUPERVISOR",
  "MECANICO",
  "GUARDIA",
  "RECEPCIONISTA",
  "JEFE_TALLER",
  "EJECUTIVO",
  "SPONSOR",
  "COORDINADOR_ZONA",
  "CHOFER",
];

// -------------------------------------------
// API BASE  —— DEBE SER SOLO EL HOST
// SIN /api/v1
// -------------------------------------------
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// -------------------------------------------
// ENDPOINTS CORRECTOS
// -------------------------------------------
export const ENDPOINTS = {
  LOGIN: `${API_BASE}/api/v1/auth/login/`,
  REFRESH: `${API_BASE}/api/v1/auth/refresh/`,
  ME: `${API_BASE}/api/v1/users/me/`,
  USERS: `/api/proxy/users/`,

  // Workorders
  WORK_ORDERS: `/api/proxy/work/ordenes/`,
  WORK_ORDER: (id: string) => `/api/proxy/work/ordenes/${id}/`,
  WORK_ORDERS_MOVE: (id: string, accion: string) =>
    `${API_BASE}/api/v1/work/ordenes/${id}/${accion}/`,
  WORK_ORDERS_TIMELINE: (id: string) =>
    `/api/proxy/work/ordenes/${id}/timeline/`,
  WORK_ITEMS: `${API_BASE}/api/v1/work/items/`,
  WORK_COMENTARIOS: `/api/proxy/work/comentarios/`,
  WORK_PAUSAS: `/api/proxy/work/pausas/`,

  // Evidencias
  EVIDENCES: `/api/proxy/work/evidencias/`,
  EVIDENCE_PRESIGN: `/api/proxy/work/evidencias/presigned/`,
  EVIDENCE_INVALIDAR: (id: string) =>
    `/api/proxy/work/evidencias/${id}/invalidar/`,

  // Drivers/Choferes
  DRIVERS: `/api/proxy/drivers/choferes/`,
  DRIVER: (id: string) => `/api/proxy/drivers/choferes/${id}/`,
  DRIVER_ASIGNAR_VEHICULO: (id: string) => `/api/proxy/drivers/choferes/${id}/asignar-vehiculo/`,
  DRIVER_HISTORIAL: (id: string) => `/api/proxy/drivers/choferes/${id}/historial/`,

  // Vehicles
  VEHICLES: `/api/proxy/vehicles/`,
  VEHICLES_INGRESO: `/api/proxy/vehicles/ingreso/`,
  VEHICLES_SALIDA: `/api/proxy/vehicles/salida/`,
  VEHICLES_INGRESOS_HOY: `/api/proxy/vehicles/ingresos-hoy/`,
  VEHICLES_INGRESOS_HISTORIAL: `/api/proxy/vehicles/ingresos-historial/`,
  VEHICLES_TICKET_INGRESO: (ingresoId: string) => `/api/proxy/vehicles/ingreso/${ingresoId}/ticket/`,
  VEHICLES_BLOQUEOS: `${API_BASE}/api/v1/vehicles/bloqueos/`,
  
  
  // Scheduling (Agenda)
  SCHEDULING: `${API_BASE}/api/v1/scheduling/`,
  SCHEDULING_AGENDAS: `${API_BASE}/api/v1/scheduling/agendas/`,
  SCHEDULING_CUPOS: `${API_BASE}/api/v1/scheduling/cupos/`,
  
  // Emergencies
  EMERGENCIES: `${API_BASE}/api/v1/emergencies/`,
  
  // Reports
  REPORTS_PDF: `${API_BASE}/api/v1/reports/pdf/`,
  
  // Notifications
  NOTIFICATIONS: `/api/proxy/notifications/`,
  NOTIFICATIONS_NO_LEIDAS: `/api/proxy/notifications/no-leidas/`,
  NOTIFICATIONS_CONTADOR: `/api/proxy/notifications/contador/`,
  NOTIFICATION: (id: string) => `/api/proxy/notifications/${id}/`,
  NOTIFICATION_MARCAR_LEIDA: (id: string) => `/api/proxy/notifications/${id}/marcar-leida/`,
} as const;

// -------------------------------------------
// ROLE ACCESS
// -------------------------------------------
export const ROLE_ACCESS: Record<Rol, string[]> = {
  ADMIN: ["dashboard","vehicles","workorders","evidences","users","reports","drivers","scheduling","emergencies"],
  SUPERVISOR: ["dashboard","vehicles","workorders","evidences","reports","drivers","scheduling","emergencies"],
  MECANICO: ["dashboard","workorders","evidences"],
  SPONSOR: ["dashboard","workorders"],
  GUARDIA: ["dashboard","vehicles"],
  RECEPCIONISTA: ["dashboard","vehicles","workorders"],
  JEFE_TALLER: ["dashboard","vehicles","workorders","evidences","reports","drivers"],
  EJECUTIVO: ["dashboard","reports"],
  COORDINADOR_ZONA: ["dashboard","vehicles","workorders","scheduling","emergencies"],
  CHOFER: ["dashboard","vehicles"], // Solo visualización
};

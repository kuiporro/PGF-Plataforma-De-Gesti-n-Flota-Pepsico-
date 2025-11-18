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
  USERS: `${API_BASE}/api/v1/users/`,

  // Workorders
  WORK_ORDERS: `${API_BASE}/api/v1/work/ordenes/`,
  WORK_ORDERS_MOVE: (id: string, accion: string) =>
    `${API_BASE}/api/v1/work/ordenes/${id}/${accion}/`,
  WORK_ITEMS: `${API_BASE}/api/v1/work/items/`,

  // Evidencias
  EVIDENCES: `${API_BASE}/api/v1/work/evidencias/`,
  EVIDENCE_PRESIGN: `${API_BASE}/api/v1/work/evidencias/presigned/`,

  // Vehicles
  VEHICLES: `${API_BASE}/api/v1/vehicles`,
  
  // Drivers (Choferes)
  DRIVERS: `${API_BASE}/api/v1/drivers/`,
  
  // Scheduling (Agenda)
  SCHEDULING: `${API_BASE}/api/v1/scheduling/`,
  SCHEDULING_AGENDAS: `${API_BASE}/api/v1/scheduling/agendas/`,
  SCHEDULING_CUPOS: `${API_BASE}/api/v1/scheduling/cupos/`,
  
  // Emergencies
  EMERGENCIES: `${API_BASE}/api/v1/emergencies/`,
  
  // Reports
  REPORTS_PDF: `${API_BASE}/api/v1/reports/pdf/`,
  
  // Notifications
  NOTIFICATIONS: `${API_BASE}/api/v1/notifications/`,
  NOTIFICATIONS_NO_LEIDAS: `${API_BASE}/api/v1/notifications/no-leidas/`,
  NOTIFICATIONS_CONTADOR: `${API_BASE}/api/v1/notifications/contador/`,
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

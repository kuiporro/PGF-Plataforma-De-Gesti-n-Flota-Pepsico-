export const ROLES = ["ADMIN","SUPERVISOR","MECANICO","SPONSOR","RECEPCIONISTA","GUARDIA"] as const;
export type Role = typeof ROLES[number];

export const can = {
  dashboard: (_r: Role) => true,
  workorders: {
    list: (r: Role) => ["ADMIN","SUPERVISOR","MECANICO","RECEPCIONISTA"].includes(r),
    create: (r: Role) => ["ADMIN","SUPERVISOR","RECEPCIONISTA"].includes(r),
    toExec: (r: Role) => ["ADMIN","SUPERVISOR","MECANICO"].includes(r),
    toQA:   (r: Role) => ["ADMIN","SUPERVISOR"].includes(r),
    close:  (r: Role) => ["ADMIN","SUPERVISOR"].includes(r),
    annul:  (r: Role) => ["ADMIN","SUPERVISOR"].includes(r),
  },
  evidences: {
    upload: (r: Role) => ["ADMIN","SUPERVISOR","MECANICO"].includes(r),
  },
};

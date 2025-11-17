"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { useAuth } from "@/store/auth";
import {
  HomeIcon,
  UserIcon,
  WrenchIcon,
  TruckIcon,
  Bars3Icon,
  UserGroupIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

export default function Sidebar() {
  const [open, setOpen] = useState(true);
  const pathname = usePathname();
  const { user, allowed } = useAuth();

  // Menú base - Dashboard ejecutivo solo para ADMIN, SPONSOR y EJECUTIVO
  const allMenuItems = [
    { href: "/dashboard/ejecutivo", label: "Dashboard", icon: HomeIcon, section: "reports", roles: ["EJECUTIVO", "ADMIN", "SPONSOR"] },
    { href: "/vehicles", label: "Vehículos", icon: TruckIcon, section: "vehicles" },
    { href: "/workorders", label: "Órdenes de Trabajo", icon: WrenchIcon, section: "workorders" },
    { href: "/drivers", label: "Choferes", icon: UserGroupIcon, section: "drivers", roles: ["ADMIN", "SUPERVISOR", "JEFE_TALLER"] },
    { href: "/scheduling", label: "Agenda", icon: CalendarIcon, section: "scheduling", roles: ["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA"] },
    { href: "/emergencies", label: "Emergencias", icon: ExclamationTriangleIcon, section: "emergencies", roles: ["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA", "JEFE_TALLER"] },
    { href: "/users", label: "Usuarios", icon: UserIcon, section: "users", roles: ["ADMIN", "SUPERVISOR"] },
  ];

  // Filtrar menú según permisos del usuario
  const menu = allMenuItems.filter((item) => {
    if (item.roles && user) {
      return item.roles.includes(user.rol as any);
    }
    return !item.section || allowed(item.section);
  });

  return (
    <aside
      className={`h-screen bg-white dark:bg-gray-800 shadow-xl 
      transition-all duration-300 border-r dark:border-gray-700
      ${open ? "w-64" : "w-20"} fixed left-0 top-0 z-30 overflow-y-auto`}
    >
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <span className="font-bold text-xl dark:text-white">
          {open ? "PGF" : "P"}
        </span>
        <Bars3Icon
          className="w-6 h-6 cursor-pointer dark:text-gray-200 hover:text-blue-600 transition-colors"
          onClick={() => setOpen(!open)}
        />
      </div>

      <nav className="mt-6">
        {menu.map((m) => {
          const isActive = pathname === m.href || pathname?.startsWith(m.href + "/");
          return (
            <Link
              key={m.href}
              href={m.href}
              className={`flex items-center gap-4 px-4 py-3 my-1 mx-2 rounded-lg
              transition-colors duration-200 group
              ${
                isActive
                  ? "text-white dark:bg-[#003DA5]"
                  : "hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
              }`}
              style={isActive ? { backgroundColor: '#003DA5' } : {}}
            >
              <m.icon className={`w-6 h-6 ${isActive ? "text-white" : "text-gray-600 dark:text-gray-300"}`} />
              {open && (
                <span className={`font-medium ${isActive ? "text-white" : "text-gray-700 dark:text-gray-200"}`}>
                  {m.label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}


// "use client";

// import Link from "next/link";
// import { usePathname } from "next/navigation";
// import { useState } from "react";

// export default function Sidebar() {
//   const path = usePathname();
//   const [open, setOpen] = useState(false);

//   const links = [
//     { name: "Dashboard", href: "/dashboard" },
//     { name: "Vehículos", href: "/vehicles" },
//     { name: "Órdenes de Trabajo", href: "/workorders" },
//     { name: "Usuarios", href: "/users" },
//     { name: "Evidencias", href: "/evidencias" },
//   ];

//   return (
//     <>
//       {/* MOBILE BUTTON */}
//       <button
//         className="lg:hidden fixed top-4 left-4 z-50 bg-white shadow p-2 rounded"
//         onClick={() => setOpen(true)}
//       >
//         ☰
//       </button>

//       {/* OVERLAY MOBILE */}
//       {open && (
//         <div
//           className="fixed inset-0 bg-black/40 z-40 lg:hidden"
//           onClick={() => setOpen(false)}
//         />
//       )}

//       {/* SIDEBAR */}
//       <aside
//         className={`fixed lg:static top-0 left-0 h-full w-64 bg-white shadow-lg z-50 transform transition-transform
//         ${open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
//       `}
//       >
//         <div className="p-6 font-bold text-xl border-b">
//           PGF – Gestión de Flota
//         </div>

//         <nav className="mt-4">
//           {links.map((item) => {
//             const active = path.startsWith(item.href);

//             return (
//               <Link
//                 key={item.href}
//                 href={item.href}
//                 onClick={() => setOpen(false)}
//                 className={`block px-6 py-3 text-sm font-medium border-l-4 transition
//                   ${active ? "bg-blue-50 border-blue-600 text-blue-600" : "border-transparent text-gray-700 hover:bg-gray-100"}
//                 `}
//               >
//                 {item.name}
//               </Link>
//             );
//           })}
//         </nav>
//       </aside>
//     </>
//   );
// }

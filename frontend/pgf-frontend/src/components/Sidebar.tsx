
"use client";

import Link from "next/link";
import { useState } from "react";
import {
  HomeIcon,
  UserIcon,
  WrenchIcon,
  TruckIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";

export default function Sidebar() {
  const [open, setOpen] = useState(true);

  const menu = [
    { href: "/dashboard", label: "Dashboard", icon: HomeIcon },
    { href: "/vehicles", label: "Vehículos", icon: TruckIcon },
    { href: "/workorders", label: "Órdenes de Trabajo", icon: WrenchIcon },
    { href: "/users", label: "Usuarios", icon: UserIcon },
  ];

  return (
    <aside
      className={`h-screen bg-white dark:bg-gray-800 shadow-xl 
      transition-all duration-300 border-r dark:border-gray-700
      ${open ? "w-64" : "w-20"}`}
    >
      <div className="flex items-center justify-between p-4">
        <span className="font-bold text-xl dark:text-white">
          {open ? "PGF" : "P"}
        </span>
        <Bars3Icon
          className="w-6 h-6 cursor-pointer dark:text-gray-200"
          onClick={() => setOpen(!open)}
        />
      </div>

      <nav className="mt-6">
        {menu.map((m) => (
          <Link
            key={m.href}
            href={m.href}
            className="flex items-center gap-4 px-4 py-3 my-1 
            hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg 
            transition-colors duration-200 group"
          >
            <m.icon className="w-6 h-6 text-gray-600 dark:text-gray-300" />
            {open && <span className="text-gray-700 dark:text-gray-200">{m.label}</span>}
          </Link>
        ))}
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

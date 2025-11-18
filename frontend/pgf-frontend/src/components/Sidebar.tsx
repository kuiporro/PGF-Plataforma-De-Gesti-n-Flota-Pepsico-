/**
 * Componente Sidebar - Menú de navegación lateral.
 * 
 * Este componente proporciona la navegación principal de la aplicación,
 * mostrando diferentes opciones según los permisos del usuario.
 * 
 * Características:
 * - Menú colapsable (se puede expandir/contraer)
 * - Filtrado por roles y permisos
 * - Resaltado de ruta activa
 * - Diseño responsive con soporte dark mode
 * - Colores PepsiCo (#003DA5) para elementos activos
 * 
 * Dependencias:
 * - next/link: Para navegación
 * - next/navigation: usePathname para detectar ruta actual
 * - @heroicons/react: Iconos
 * - @/store/auth: useAuth para permisos
 * 
 * Relaciones:
 * - Usado en: layout.tsx (layout principal)
 * - Depende de: useAuth store para verificar permisos
 * - Complementa: Topbar.tsx (barra superior)
 */

"use client";  // Componente de cliente (usa hooks)

import Link from "next/link";  // Componente de Next.js para navegación
import { usePathname } from "next/navigation";  // Hook para obtener ruta actual
import { useState, useEffect } from "react";  // Hooks de React
import { useAuth } from "@/store/auth";  // Store de autenticación
import {
  HomeIcon,        // Icono de dashboard
  UserIcon,        // Icono de usuarios
  WrenchIcon,      // Icono de órdenes de trabajo
  TruckIcon,       // Icono de vehículos
  Bars3Icon,       // Icono de menú hamburguesa
  UserGroupIcon,   // Icono de choferes
  CalendarIcon,    // Icono de agenda
  ExclamationTriangleIcon,  // Icono de emergencias
} from "@heroicons/react/24/outline";  // Iconos outline de Heroicons

/**
 * Componente Sidebar.
 * 
 * Renderiza el menú lateral de navegación con:
 * - Logo/título de la aplicación
 * - Botón para colapsar/expandir
 * - Lista de items de menú filtrados por permisos
 * 
 * Estados:
 * - open: Indica si el sidebar está expandido (true) o colapsado (false)
 */
export default function Sidebar() {
  // Estado: sidebar expandido o colapsado
  const [open, setOpen] = useState(true);
  
  // Ruta actual (para resaltar item activo)
  const pathname = usePathname();
  
  // Obtener usuario y función de verificación de permisos
  const { user, allowed } = useAuth();

  /**
   * Menú base con todos los items disponibles.
   * 
   * Cada item tiene:
   * - href: Ruta a la que navega
   * - label: Texto visible
   * - icon: Componente de icono
   * - section: Sección para verificar permisos (usado con allowed())
   * - roles: Roles específicos que pueden ver este item (opcional)
   * 
   * Nota:
   * - Si tiene roles, solo esos roles pueden verlo
   * - Si no tiene roles, se verifica con section usando allowed()
   */
  const allMenuItems = [
    {
      href: "/dashboard/ejecutivo",
      label: "Dashboard",
      icon: HomeIcon,
      section: "reports",
      roles: ["EJECUTIVO", "ADMIN", "SPONSOR"]  // Solo estos roles ven dashboard ejecutivo
    },
    {
      href: "/vehicles",
      label: "Vehículos",
      icon: TruckIcon,
      section: "vehicles"  // Verifica con allowed("vehicles")
    },
    {
      href: "/workorders",
      label: "Órdenes de Trabajo",
      icon: WrenchIcon,
      section: "workorders"
    },
    {
      href: "/drivers",
      label: "Choferes",
      icon: UserGroupIcon,
      section: "drivers",
      roles: ["ADMIN", "SUPERVISOR", "JEFE_TALLER"]  // Solo estos roles
    },
    {
      href: "/scheduling",
      label: "Agenda",
      icon: CalendarIcon,
      section: "scheduling",
      roles: ["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA"]
    },
    {
      href: "/emergencies",
      label: "Emergencias",
      icon: ExclamationTriangleIcon,
      section: "emergencies",
      roles: ["ADMIN", "SUPERVISOR", "COORDINADOR_ZONA", "JEFE_TALLER"]
    },
    {
      href: "/users",
      label: "Usuarios",
      icon: UserIcon,
      section: "users",
      roles: ["ADMIN", "SUPERVISOR"]  // Solo admin y supervisor
    },
  ];

  /**
   * Filtrar menú según permisos del usuario.
   * 
   * Lógica:
   * 1. Si el item tiene roles específicos:
   *    - Verificar que el usuario tenga uno de esos roles
   * 2. Si no tiene roles:
   *    - Verificar permisos con allowed(section)
   * 
   * Esto asegura que cada usuario solo vea las opciones
   * a las que tiene acceso.
   */
  const menu = allMenuItems.filter((item) => {
    // Si tiene roles específicos, verificar que el usuario tenga uno
    if (item.roles && user) {
      return item.roles.includes(user.rol as any);
    }
    // Si no tiene roles, verificar con allowed()
    return !item.section || allowed(item.section);
  });

  /**
   * Render del sidebar.
   * 
   * Estructura:
   * - Header con logo y botón de colapsar
   * - Nav con items de menú
   * 
   * Clases CSS:
   * - w-64: Ancho expandido (256px)
   * - w-20: Ancho colapsado (80px)
   * - fixed: Posición fija en la izquierda
   * - z-30: Z-index para estar sobre otros elementos
   */
  return (
    <aside
      className={`h-screen bg-white dark:bg-gray-800 shadow-xl 
      transition-all duration-300 border-r dark:border-gray-700
      ${open ? "w-64" : "w-20"} fixed left-0 top-0 z-30 overflow-y-auto`}
    >
      {/* Header con logo y botón de colapsar */}
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <span className="font-bold text-xl dark:text-white">
          {open ? "PGF" : "P"}  {/* Mostrar "PGF" si está expandido, "P" si está colapsado */}
        </span>
        <Bars3Icon
          className="w-6 h-6 cursor-pointer dark:text-gray-200 hover:text-blue-600 transition-colors"
          onClick={() => setOpen(!open)}  // Toggle de estado
        />
      </div>

      {/* Navegación */}
      <nav className="mt-6">
        {menu.map((m) => {
          // Verificar si esta ruta está activa
          // Está activa si coincide exactamente o es una subruta
          const isActive = pathname === m.href || pathname?.startsWith(m.href + "/");
          
          return (
            <Link
              key={m.href}
              href={m.href}
              className={`flex items-center gap-4 px-4 py-3 my-1 mx-2 rounded-lg
              transition-colors duration-200 group
              ${
                isActive
                  ? "text-white dark:bg-[#003DA5]"  // Color PepsiCo para activo
                  : "hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
              }`}
              style={isActive ? { backgroundColor: '#003DA5' } : {}}  // Color PepsiCo inline
            >
              {/* Icono del item */}
              <m.icon className={`w-6 h-6 ${isActive ? "text-white" : "text-gray-600 dark:text-gray-300"}`} />
              
              {/* Label solo visible si está expandido */}
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

/**
 * Utilidades para manejo de permisos y redirecciones por rol.
 * 
 * Este módulo proporciona funciones para:
 * - Verificar permisos según roles
 * - Redirigir a la página principal de cada rol cuando hay permisos insuficientes
 * - Mostrar alertas de permisos insuficientes
 */

import { useRouter } from "next/navigation";
import { useToast } from "@/components/ToastContainer";

/**
 * Mapeo de roles a sus páginas principales.
 */
export const ROLE_HOME_PAGES: Record<string, string> = {
  ADMIN: "/dashboard",
  SUPERVISOR: "/supervisor/dashboard",
  MECANICO: "/mecanico/dashboard",
  GUARDIA: "/vehicles/ingresos-hoy",
  JEFE_TALLER: "/jefe-taller/dashboard",
  COORDINADOR_ZONA: "/coordinador/dashboard",
  CHOFER: "/chofer",
  EJECUTIVO: "/dashboard/ejecutivo",
  SPONSOR: "/dashboard",
  AUDITOR_INTERNO: "/auditor/dashboard",
  SUBGERENTE_NACIONAL: "/subgerente/dashboard",
};

/**
 * Obtiene la página principal de un rol.
 * 
 * @param rol - El rol del usuario
 * @returns La ruta de la página principal del rol, o "/dashboard" por defecto
 */
export function getRoleHomePage(rol: string | null | undefined): string {
  if (!rol) return "/dashboard";
  return ROLE_HOME_PAGES[rol] || "/dashboard";
}

/**
 * Hook para manejar errores de permisos insuficientes.
 * 
 * Muestra una alerta y redirige a la página principal del rol del usuario.
 * 
 * @returns Función para manejar errores de permisos
 */
export function usePermissionErrorHandler() {
  const router = useRouter();
  const toast = useToast();

  return (error: any, userRole?: string | null) => {
    // Verificar si es un error de permisos
    const isPermissionError = 
      error?.status === 403 ||
      error?.response?.status === 403 ||
      error?.message?.includes("Permisos insuficientes") ||
      error?.message?.includes("No autorizado") ||
      error?.detail?.includes("Permisos insuficientes") ||
      error?.detail?.includes("No autorizado");

    if (isPermissionError) {
      toast.error("Permisos insuficientes. No tiene acceso a esta funcionalidad.");
      
      // Redirigir a la página principal del rol
      const homePage = getRoleHomePage(userRole);
      setTimeout(() => {
        router.push(homePage);
      }, 2000); // Esperar 2 segundos para que el usuario vea el mensaje
      
      return true; // Indica que se manejó el error
    }
    
    return false; // No se manejó el error
  };
}

/**
 * Verifica si un rol tiene permisos para una acción específica.
 * 
 * @param userRole - El rol del usuario
 * @param allowedRoles - Array de roles permitidos
 * @returns true si el usuario tiene permisos, false en caso contrario
 */
export function hasPermission(userRole: string | null | undefined, allowedRoles: string[]): boolean {
  if (!userRole) return false;
  return allowedRoles.includes(userRole);
}

/**
 * Maneja errores de API y muestra alertas apropiadas.
 * 
 * @param error - El error recibido de la API
 * @param router - Router de Next.js para redirecciones
 * @param toast - Hook de toast para mostrar mensajes
 * @param userRole - Rol del usuario actual
 */
export function handleApiError(
  error: any,
  router: ReturnType<typeof useRouter>,
  toast: ReturnType<typeof useToast>,
  userRole?: string | null
) {
  const errorMessage = 
    error?.response?.data?.detail ||
    error?.data?.detail ||
    error?.detail ||
    error?.message ||
    "Error desconocido";

  // Verificar si es un error de permisos
  if (
    error?.status === 403 ||
    error?.response?.status === 403 ||
    errorMessage.includes("Permisos insuficientes") ||
    errorMessage.includes("No autorizado")
  ) {
    toast.error("Permisos insuficientes. No tiene acceso a esta funcionalidad.");
    
    // Redirigir a la página principal del rol
    const homePage = getRoleHomePage(userRole);
    setTimeout(() => {
      router.push(homePage);
    }, 2000);
    
    return;
  }

  // Otros errores
  toast.error(errorMessage);
}


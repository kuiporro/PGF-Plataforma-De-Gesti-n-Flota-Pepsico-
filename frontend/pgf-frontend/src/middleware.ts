import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Rutas que requieren autenticación
const protectedRoutes = [
  "/dashboard",
  "/users",
  "/vehicles",
  "/workorders",
  "/profile",
];

// Rutas públicas (no requieren autenticación)
const publicRoutes = [
  "/auth/login",
  "/auth/reset-password",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("pgf_access");

  // Permitir acceso a rutas de API
  if (pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  // Si es una ruta pública, permitir acceso
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Si es la raíz, permitir (ya tiene su propia lógica de redirección)
  if (pathname === "/") {
    return NextResponse.next();
  }

  // Si es una ruta protegida y no hay token, redirigir al login
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    if (!token) {
      const loginUrl = new URL("/auth/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes) - pero las manejamos dentro del middleware
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};

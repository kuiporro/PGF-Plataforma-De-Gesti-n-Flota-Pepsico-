import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC = ["/auth/login", "/favicon.ico", "/"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  if (PUBLIC.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const token = req.cookies.get("pgf_access")?.value;  // ← CAMBIO CLAVE

  if (!token) {
    const url = new URL("/auth/login", req.url);
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next|static).*)"],
};

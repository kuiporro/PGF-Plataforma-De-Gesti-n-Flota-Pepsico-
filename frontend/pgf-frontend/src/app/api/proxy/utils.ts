import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export const API_BASE =
  process.env.API_BASE ?? "http://pgf-api:8000/api/v1";

export async function proxyFetch(
  endpoint: string,
  init: RequestInit = {}
) {
  const cookieStore = await cookies();
  const token = cookieStore.get("pgf_access")?.value;

  if (!token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const url = `${API_BASE}${endpoint}`;

  const r = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init.headers ?? {}),
    },
    cache: "no-store",
  });

  // Respuesta cruda (texto)
  const text = await r.text();

  // Handle empty responses
  if (!text || text.trim() === "") {
    if (!r.ok) {
      return NextResponse.json(
        { detail: "Empty response from backend" },
        { status: r.status }
      );
    }
    // For successful empty responses, return empty object
    return NextResponse.json({});
  }

  // Si no es JSON válido → devolvemos error limpio
  let json: any = null;
  try {
    json = JSON.parse(text);
  } catch {
    return NextResponse.json(
      { detail: "Invalid response from backend", raw: text },
      { status: r.status }
    );
  }

  if (!r.ok) {
    return NextResponse.json(
      { detail: "Backend error", raw: json },
      { status: r.status }
    );
  }

  return NextResponse.json(json);
}

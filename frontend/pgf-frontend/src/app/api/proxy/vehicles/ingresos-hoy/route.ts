import { NextRequest } from "next/server";
import { proxyFetch } from "../../utils";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const patente = searchParams.get("patente");
  const endpoint = patente
    ? `/vehicles/ingresos-hoy/?patente=${encodeURIComponent(patente)}`
    : "/vehicles/ingresos-hoy/";
  return proxyFetch(endpoint, {
    method: "GET",
  });
}


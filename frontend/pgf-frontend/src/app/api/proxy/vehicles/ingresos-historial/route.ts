import { NextRequest } from "next/server";
import { proxyFetch } from "../../utils";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const queryString = searchParams.toString();
  const endpoint = queryString ? `/vehicles/ingresos-historial/?${queryString}` : "/vehicles/ingresos-historial/";
  
  return proxyFetch(endpoint, {
    method: "GET",
  });
}


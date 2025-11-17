import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../utils";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  let endpoint = "/reports/pdf/";
  if (searchParams.toString()) {
    endpoint += `?${searchParams.toString()}`;
  }
  
  const response = await proxyFetch(endpoint, {
    method: "GET",
  });

  // Si es un PDF, devolverlo directamente
  if (response.headers.get("content-type")?.includes("application/pdf")) {
    const blob = await response.blob();
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": response.headers.get("Content-Disposition") || 'attachment; filename="reporte.pdf"',
      },
    });
  }

  return response;
}


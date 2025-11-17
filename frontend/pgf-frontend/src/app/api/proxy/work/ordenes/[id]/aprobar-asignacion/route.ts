import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../../../utils";

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json();
  return proxyFetch(`/work/ordenes/${params.id}/aprobar-asignacion/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}


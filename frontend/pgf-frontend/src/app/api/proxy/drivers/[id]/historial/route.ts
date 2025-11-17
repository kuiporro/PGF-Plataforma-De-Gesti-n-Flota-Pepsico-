import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../../../utils";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyFetch(`/drivers/choferes/${params.id}/historial/`, {
    method: "GET",
  });
}


import { proxyFetch } from "../../../utils";
import { NextRequest } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const p = await params;
  return proxyFetch(`/vehicles/${p.id}/historial/`);
}


import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../../utils";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  return proxyFetch(`/emergencies/${id}/cerrar/`, {
    method: "POST",
  });
}


import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../../utils";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return proxyFetch(`/emergencies/${id}/aprobar/`, {
    method: "POST",
  });
}


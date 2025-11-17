import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../utils";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyFetch(`/emergencies/${params.id}/`, {
    method: "GET",
  });
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json();
  return proxyFetch(`/emergencies/${params.id}/`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}


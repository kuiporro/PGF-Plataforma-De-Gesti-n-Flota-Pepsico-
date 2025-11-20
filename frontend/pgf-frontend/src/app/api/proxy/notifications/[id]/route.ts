import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../utils";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyFetch(`/notifications/${params.id}/`);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json();
  return proxyFetch(`/notifications/${params.id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyFetch(`/notifications/${params.id}/`, {
    method: "DELETE",
  });
}


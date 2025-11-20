import { NextRequest } from "next/server";
import { proxyFetch } from "../../../utils";

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyFetch(`/notifications/${params.id}/marcar-leida/`, {
    method: "POST",
  });
}


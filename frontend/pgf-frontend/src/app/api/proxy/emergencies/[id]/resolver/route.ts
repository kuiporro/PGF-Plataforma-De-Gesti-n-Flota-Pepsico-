import { NextRequest, NextResponse } from "next/server";
import { proxyFetch } from "../../../utils";

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyFetch(`/emergencies/${params.id}/resolver/`, {
    method: "POST",
  });
}


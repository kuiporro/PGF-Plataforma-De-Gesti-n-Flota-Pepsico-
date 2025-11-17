import { NextRequest } from "next/server";
import { proxyFetch } from "../utils";

export async function GET() {
  return proxyFetch("/vehicles/");
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  return proxyFetch("/vehicles/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
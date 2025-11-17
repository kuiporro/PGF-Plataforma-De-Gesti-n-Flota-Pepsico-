import { proxyFetch } from "../utils";

export async function GET() {
  return proxyFetch("/vehicles/");
}
export async function POST(request: Request) {
  return proxyFetch("/vehicles/", {
    method: "POST",
    body: request.body,
  });
}
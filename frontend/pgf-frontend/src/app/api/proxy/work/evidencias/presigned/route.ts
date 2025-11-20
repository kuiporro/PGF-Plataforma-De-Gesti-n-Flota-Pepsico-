import { NextRequest } from "next/server";
import { proxyFetch } from "../../../utils";

/**
 * Proxy route para obtener URL presigned para subir evidencias a S3.
 * 
 * POST /api/proxy/work/evidencias/presigned/
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return proxyFetch("/work/evidencias/presigned/", {
      method: "POST",
      body: JSON.stringify(body),
    });
  } catch (error) {
    console.error("Error parsing request body:", error);
    return proxyFetch("/work/evidencias/presigned/", {
      method: "POST",
      body: await request.text(),
    });
  }
}


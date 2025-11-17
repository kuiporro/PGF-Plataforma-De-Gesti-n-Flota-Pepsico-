import { cookies } from "next/headers";
import { ENDPOINTS } from "@/lib/constants";

export async function GET() {
  const cookieStore = await cookies();
  const token = cookieStore.get("pgf_access")?.value;

  if (!token)
    return Response.json({ detail: "Unauthorized" }, { status: 401 });

  try {
    const r = await fetch(`${ENDPOINTS.ME}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const text = await r.text();
    
    // Handle empty responses
    if (!text || text.trim() === "") {
      return Response.json({ detail: "Empty response from backend" }, { status: r.status || 500 });
    }

    let json;
    try {
      json = JSON.parse(text);
    } catch (e) {
      return Response.json(
        { detail: "Invalid JSON response from backend", raw: text },
        { status: r.status || 500 }
      );
    }

    return Response.json(json, { status: r.status });
  } catch (error) {
    console.error("Error in /api/auth/me:", error);
    return Response.json(
      { detail: "Failed to fetch user data", error: String(error) },
      { status: 500 }
    );
  }
}

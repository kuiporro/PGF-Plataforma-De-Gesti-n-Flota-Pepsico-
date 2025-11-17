import { proxyFetch } from "../utils";

export async function GET() {
  return proxyFetch("/users/");
}
export async function POST(request: Request) {
  return proxyFetch("/users/", {
    method: "POST",
    body: request.body,
  });
}
// import { NextResponse as Response } from "next/server";

// import { cookies } from "next/headers";
// import { ENDPOINTS } from "@/lib/constants";
// import { proxyFetch } from "../utils";


// export async function GET() {
  
//   const cookieStore = await cookies();
//   const token = cookieStore.get("pgf_token")?.value;

//   if (!token)
//     return Response.json({ detail: "Unauthorized" }, { status: 401 });

//   const r = await fetch(ENDPOINTS.USERS, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//     cache: "no-store",
//   });

//   return Response.json(await r.json(), { status: r.status });
  
// }

// export async function POST(req: Request) {
//   const cookieStore = await cookies();
//   const token = cookieStore.get("pgf_token")?.value;

//   if (!token)
//     return Response.json({ detail: "Unauthorized" }, { status: 401 });

//   const body = await req.json();

//   const r = await fetch(ENDPOINTS.USERS, {
//     method: "POST",
//     headers: {
//       Authorization: `Bearer ${token}`,
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify(body),
//   });

//   return Response.json(await r.json(), { status: r.status });
// }

import "server-only";
import { cookies } from "next/headers";

const ACCESS = "pgf_token";
const REFRESH = "pgf_refresh";

export async function getServerToken(): Promise<string | null> {
  try {
    const store = await cookies();   // ASYNC CORRECTO
    return store.get(ACCESS)?.value ?? null;
  } catch {
    return null;
  }
}

export async function getServerRefresh(): Promise<string | null> {
  try {
    const store = await cookies();
    return store.get(REFRESH)?.value ?? null;
  } catch {
    return null;
  }
}

export async function getServerAuthHeader() {
  const token = await getServerToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

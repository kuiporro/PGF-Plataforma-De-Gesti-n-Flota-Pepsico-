'use client'


export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

// Helper function to safely parse JSON
async function safeJsonParse<T>(response: Response): Promise<T> {
  const text = await response.text();
  
  if (!text || text.trim() === "") {
    return {} as T;
  }
  
  try {
    return JSON.parse(text) as T;
  } catch (e) {
    console.error("Invalid JSON response:", text);
    throw new Error(`Invalid JSON response: ${text.substring(0, 100)}`);
  }
}

export async function apiGet<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api/proxy?path=${encodeURIComponent(path)}` , {
    method: 'GET',
    credentials: 'include',
    ...init,
  })
  
  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    throw new Error(errorText || `HTTP ${res.status}`);
  }
  
  return safeJsonParse<T>(res);
}

export async function apiPost<T>(path: string, body?: unknown, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api/proxy?path=${encodeURIComponent(path)}` , {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(init.headers||{}) },
    body: body ? JSON.stringify(body) : undefined,
    ...init,
  })
  
  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    throw new Error(errorText || `HTTP ${res.status}`);
  }
  
  return safeJsonParse<T>(res);
}

export async function apiAction(path: string, method: 'POST'|'PATCH'|'DELETE' = 'POST', body?: unknown) {
  const res = await fetch(`/api/proxy?path=${encodeURIComponent(path)}`, {
    method,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  
  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    throw new Error(errorText || `HTTP ${res.status}`);
  }
  
  try {
    return await safeJsonParse(res);
  } catch {
    return {};
  }
}
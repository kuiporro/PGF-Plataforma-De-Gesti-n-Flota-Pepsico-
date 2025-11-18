// src/lib/cookies.client.ts
"use client";
import Cookies from "js-cookie";
const COOKIE = "pgf_token";

export function getToken(): string | null {
  return Cookies.get(COOKIE) ?? null;
}
export function setToken(value: string) {
  Cookies.set(COOKIE, value, { sameSite: "lax" });
}
export function clearToken() {
  Cookies.remove(COOKIE);
}

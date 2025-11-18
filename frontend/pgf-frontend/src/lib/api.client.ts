export const withSession = (init: RequestInit = {}): RequestInit => ({
  credentials: "include",
  ...init,
  headers: {
    "Content-Type": "application/json",
    ...(init.headers || {}),
  },
});

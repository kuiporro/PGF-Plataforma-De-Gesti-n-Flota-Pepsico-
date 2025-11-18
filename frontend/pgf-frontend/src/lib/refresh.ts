export async function tryRefresh() {
  await fetch("/api/auth/refresh", {
    method: "POST",
    credentials: "include",
  });
}

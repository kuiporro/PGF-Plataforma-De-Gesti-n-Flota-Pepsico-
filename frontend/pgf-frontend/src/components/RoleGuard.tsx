"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/store/auth";
import type { Rol } from "@/lib/constants";

export default function RoleGuard({
  allow = [],
  children,
}: {
  allow: Rol[];
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isLogged, hasRole, refreshMe } = useAuth();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      // refresca usuario solo si NO está en memoria
      if (!user) {
        await refreshMe();
      }

      if (!isLogged()) {
        router.replace("/auth/token");
        return;
      }

      if (allow.length && !hasRole(allow)) {
        router.replace("/dashboard");
        return;
      }

      setReady(true);
    })();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!ready) return null;
  return <>{children}</>;
}

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/store/auth";
import type { Rol } from "@/lib/constants";

export default function RoleGuard({
  allow = [],
  children,
  redirectTo = "/dashboard",
}: {
  allow: Rol[];
  children: React.ReactNode;
  redirectTo?: string;
}) {
  const router = useRouter();
  const { user, isLogged, hasRole, refreshMe } = useAuth();
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      // refresca usuario solo si NO está en memoria
      if (!user) {
        await refreshMe();
      }

      if (!isLogged()) {
        router.replace("/auth/login");
        return;
      }

      if (allow.length && !hasRole(allow)) {
        router.replace(redirectTo);
        return;
      }

      setReady(true);
      setLoading(false);
    })();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading || !ready) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Verificando permisos...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

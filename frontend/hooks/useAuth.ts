"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/components/auth-context";

/** Current auth state only — no redirects. */
export function useAuth() {
  return useAuthContext();
}

/**
 * Auth state plus a redirect to /login once we know the session is absent.
 * A transport failure (backend down) does NOT redirect — that would look
 * like a login loop instead of an outage.
 */
export function useRequireAuth() {
  const router = useRouter();
  const { student, loading, offline } = useAuthContext();

  useEffect(() => {
    if (!loading && !offline && student === null) {
      router.replace("/login");
    }
  }, [loading, offline, student, router]);

  return { student, loading, offline };
}

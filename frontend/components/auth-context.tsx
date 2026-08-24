"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { ApiError, api, type Student } from "@/lib/api";

interface AuthContextValue {
  student: Student | null;
  loading: boolean;
  /** Transport-level failure (backend unreachable) vs plain logged-out. */
  offline: boolean;
  setStudent: (student: Student | null) => void;
}

const AuthContext = createContext<AuthContextValue>({
  student: null,
  loading: true,
  offline: false,
  setStudent: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [student, setStudent] = useState<Student | null>(null);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api
      .me()
      .then((me) => {
        if (!cancelled) {
          setStudent(me);
          setLoading(false);
        }
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        // 401 is a normal logged-out state; anything else means we could
        // not reach the backend at all.
        if (!(error instanceof ApiError && error.status === 401)) {
          setOffline(true);
        }
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AuthContext.Provider value={{ student, loading, offline, setStudent }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  return useContext(AuthContext);
}

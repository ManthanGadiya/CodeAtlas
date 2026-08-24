"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, api } from "@/lib/api";
import { useAuthContext } from "@/components/auth-context";

type Mode = "loading" | "register" | "login";

export default function LoginPage() {
  const router = useRouter();
  const { setStudent } = useAuthContext();
  const [mode, setMode] = useState<Mode>("loading");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api
      .accountStatus()
      .then((status) => {
        if (!cancelled) setMode(status.has_account ? "login" : "register");
      })
      .catch(() => {
        if (!cancelled) {
          setError("Cannot reach the CodeAtlas backend. Is it running on port 8000?");
          setMode("login");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "register") {
        const student = await api.register(email, password);
        setStudent(student);
      } else {
        const student = await api.login(email, password);
        setStudent(student);
      }
      router.replace("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm py-16">
      <h1 className="text-2xl font-semibold tracking-tight">
        {mode === "register" ? "Create your account" : "Welcome back"}
      </h1>
      <p className="mt-2 text-sm text-neutral-500">
        {mode === "register"
          ? "CodeAtlas has a single student account — yours."
          : "Sign in to continue your practice."}
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:border-neutral-900 focus:outline-none"
            placeholder="you@example.com"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium">Password</span>
          <input
            type="password"
            required
            minLength={mode === "register" ? 10 : undefined}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 focus:border-neutral-900 focus:outline-none"
            placeholder={mode === "register" ? "at least 10 characters" : ""}
          />
        </label>

        {error && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy || mode === "loading"}
          className="w-full rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700 disabled:opacity-50"
        >
          {busy
            ? "…"
            : mode === "register"
              ? "Create account"
              : "Log in"}
        </button>
      </form>
    </div>
  );
}

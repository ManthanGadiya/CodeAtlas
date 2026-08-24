"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, api } from "@/lib/api";
import { useAuthContext } from "@/components/auth-context";

type Mode = "login" | "register";

export default function LoginPage() {
  const router = useRouter();
  const { setStudent } = useAuthContext();
  const [mode, setMode] = useState<Mode>("login");
  const [statusChecked, setStatusChecked] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Pre-select the likely mode, but the toggle below always stays
  // available — a failed backend check must never hide registration.
  useEffect(() => {
    let cancelled = false;
    api
      .accountStatus()
      .then((status) => {
        if (!cancelled && !status.has_account) setMode("register");
      })
      .catch(() => {
        /* offline: keep login default; submit will surface the error */
      })
      .finally(() => {
        if (!cancelled) setStatusChecked(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function switchMode(next: Mode) {
    setMode(next);
    setError(null);
    setNotice(null);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      if (mode === "register") {
        try {
          const student = await api.register(email, password);
          setStudent(student);
          router.replace("/");
          return;
        } catch (err) {
          if (err instanceof ApiError && err.status === 409) {
            switchMode("login");
            setNotice(
              "An account already exists on this machine. Log in instead.",
            );
            return;
          }
          throw err;
        }
      }
      const student = await api.login(email, password);
      setStudent(student);
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(
          "Could not reach the CodeAtlas backend. Is it running on port 8000?",
        );
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm py-16">
      <h1 className="text-xl font-semibold tracking-tight text-balance">
        {mode === "register"
          ? "Create your CodeAtlas account"
          : "Welcome back"}
      </h1>
      <p className="mt-2 text-sm leading-relaxed text-[var(--ink-muted)]">
        {mode === "register"
          ? "One student, one account. Everything you practice becomes evidence for what you learn next."
          : "Sign in to continue your practice."}
      </p>

      <div
        role="tablist"
        aria-label="Authentication mode"
        className="mt-6 grid grid-cols-2 rounded-lg border border-[var(--line)] bg-white p-1"
      >
        {(["login", "register"] as const).map((option) => (
          <button
            key={option}
            role="tab"
            aria-selected={mode === option}
            onClick={() => switchMode(option)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-150 ${
              mode === option
                ? "bg-neutral-900 text-white"
                : "text-neutral-500 hover:text-neutral-900"
            }`}
          >
            {option === "login" ? "Log in" : "Create account"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="field mt-1"
            placeholder="you@example.com"
            autoComplete="email"
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
            className="field mt-1"
            placeholder={
              mode === "register" ? "At least 10 characters" : undefined
            }
            autoComplete={
              mode === "register" ? "new-password" : "current-password"
            }
          />
          {mode === "register" && (
            <span className="mt-1 block text-xs text-[var(--ink-faint)]">
              Minimum 10 characters.
            </span>
          )}
        </label>

        {error && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}
        {notice && (
          <p className="rounded-md bg-sky-50 px-3 py-2 text-sm text-sky-800">{notice}</p>
        )}

        <button
          type="submit"
          disabled={busy || !statusChecked}
          className="btn-primary w-full justify-center"
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

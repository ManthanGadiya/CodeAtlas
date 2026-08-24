"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, api, type ProblemSummary } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useAuth";

const DIFFICULTY_STYLES: Record<string, string> = {
  easy: "bg-emerald-100 text-emerald-800",
  medium: "bg-amber-100 text-amber-800",
  hard: "bg-red-100 text-red-800",
};

export default function ProblemsPage() {
  const { student, loading: authLoading, offline } = useRequireAuth();
  const [problems, setProblems] = useState<ProblemSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!student) return;
    let cancelled = false;
    api
      .listProblems()
      .then((data) => {
        if (!cancelled) setProblems(data);
      })
      .catch((err: ApiError) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [student]);

  if (authLoading || !student) {
    return (
      <p className="text-neutral-500">
        {offline ? "Cannot reach the CodeAtlas backend — is it running?" : "…"}
      </p>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Practice</h1>
      <p className="mt-1 text-sm text-neutral-500">
        Curated problems. Hidden tests grade your generalisation — visible examples are only the start.
      </p>

      {error && (
        <p className="mt-6 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      {!error && problems === null && <p className="mt-6 text-neutral-500">Loading…</p>}

      {problems !== null && (
        <ul className="mt-6 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white">
          {problems.map((problem) => (
            <li key={problem.slug}>
              <Link
                href={`/problems/${problem.slug}`}
                className="flex items-center gap-4 px-5 py-4 hover:bg-neutral-50"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{problem.title}</p>
                  <p className="text-sm text-neutral-500">
                    {problem.language}
                    {problem.estimated_minutes !== null
                      ? ` · ~${problem.estimated_minutes} min`
                      : ""}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${
                    DIFFICULTY_STYLES[problem.difficulty] ?? "bg-neutral-100 text-neutral-700"
                  }`}
                >
                  {problem.difficulty}
                </span>
              </Link>
            </li>
          ))}
          {problems.length === 0 && (
            <li className="px-5 py-8 text-center text-sm text-neutral-500">
              No problems seeded yet. Run{" "}
              <code className="rounded bg-neutral-100 px-1">python -m scripts.seed_problems</code>{" "}
              in backend/.
            </li>
          )}
        </ul>
      )}
    </div>
  );
}

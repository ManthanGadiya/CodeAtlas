"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, api, type AnalyticsSummary } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useAuth";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5">
      <p className="text-sm text-neutral-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const { student, loading: authLoading, offline } = useRequireAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!student) return;
    let cancelled = false;
    api
      .analyticsSummary()
      .then((data) => {
        if (!cancelled) setSummary(data);
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

  const greeting = student.display_name ?? student.email.split("@")[0];

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">
        Welcome back, {greeting}
      </h1>
      <p className="mt-1 text-sm text-neutral-500">
        Observations of your practice — honest numbers, no pretend intelligence.
      </p>

      {error && (
        <p role="alert" className="mt-6 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      {!error && summary === null && <p className="mt-6 text-neutral-500">Loading…</p>}

      {summary !== null && (
        <>
          {summary.totals.executions === 0 ? (
            <div className="mt-8 rounded-lg border border-dashed border-neutral-300 bg-white p-10 text-center">
              <p className="font-medium">No practice recorded yet.</p>
              <p className="mt-1 text-sm text-neutral-500">
                Solve your first problem and this dashboard will start telling you
                what the system observed.
              </p>
              <Link
                href="/problems"
                className="mt-4 inline-block rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700"
              >
                Start practicing
              </Link>
            </div>
          ) : (
            <>
              <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <StatCard label="Runs" value={summary.totals.runs} />
                <StatCard label="Submits" value={summary.totals.submits} />
                <StatCard
                  label="Submit success"
                  value={
                    summary.totals.success_rate === null
                      ? "—"
                      : `${Math.round(summary.totals.success_rate * 100)}%`
                  }
                />
                <StatCard
                  label="Problems completed"
                  value={`${summary.problems.completed}/${summary.problems.attempted}`}
                />
              </div>

              <h2 className="mt-10 text-sm font-semibold uppercase tracking-wide text-neutral-500">
                Per problem
              </h2>
              <ul className="mt-3 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white">
                {summary.per_problem.map((entry) => (
                  <li key={entry.problem_slug} className="flex items-center gap-4 px-5 py-4">
                    <Link
                      href={`/problems/${entry.problem_slug}`}
                      className="min-w-0 flex-1 truncate font-medium hover:underline"
                    >
                      {entry.problem_title}
                    </Link>
                    <span className="text-sm text-neutral-500">
                      {entry.attempts} attempt{entry.attempts === 1 ? "" : "s"} ·{" "}
                      {entry.submits} submit{entry.submits === 1 ? "" : "s"}
                    </span>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        entry.completed
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-neutral-100 text-neutral-600"
                      }`}
                    >
                      {entry.completed ? "completed" : "in progress"}
                    </span>
                  </li>
                ))}
              </ul>

              <h2 className="mt-10 text-sm font-semibold uppercase tracking-wide text-neutral-500">
                Recent activity
              </h2>
              <ul className="mt-3 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white text-sm">
                {summary.recent_activity.map((activity, index) => (
                  <li key={index} className="flex items-center gap-3 px-5 py-3">
                    <span
                      className={`inline-block h-2 w-2 rounded-full ${
                        activity.status === "SUCCESS" ? "bg-emerald-500" : "bg-red-400"
                      }`}
                    />
                    <span className="font-medium">{activity.problem_title}</span>
                    <span className="text-neutral-500">{activity.mode}</span>
                    <span className="ml-auto text-neutral-400">
                      {activity.passed}/{activity.total}
                      {activity.runtime_ms !== null && ` · ${activity.runtime_ms} ms`}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
}

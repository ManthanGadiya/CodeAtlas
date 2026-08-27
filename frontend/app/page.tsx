"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, api, type AnalyticsSummary, type LearnerSummary } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useAuth";
import { Skeleton } from "@/components/Skeleton";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5">
      <p className="text-sm text-neutral-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}

function masteryLabel(mastery: number): string {
  if (mastery < 0.2) return "Unknown";
  if (mastery < 0.4) return "Emerging";
  if (mastery < 0.6) return "Developing";
  if (mastery < 0.75) return "Functional";
  if (mastery < 0.9) return "Strong";
  return "Highly reliable";
}

function severityBadge(severity: string) {
  if (severity === "HIGH") return "bg-red-100 text-red-800";
  if (severity === "MEDIUM") return "bg-amber-100 text-amber-800";
  return "bg-neutral-100 text-neutral-600";
}

export default function DashboardPage() {
  const { student, loading: authLoading, offline } = useRequireAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [learner, setLearner] = useState<LearnerSummary | null>(null);
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
    api
      .learnerSummary()
      .then((data) => {
        if (!cancelled) setLearner(data);
      })
      .catch(() => {
        // learner endpoint is additive — dashboard stays useful without it
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

      {!error && summary === null && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[0, 1, 2, 3].map((index) => (
              <Skeleton key={index} className="h-20" />
            ))}
          </div>
          <Skeleton className="h-40" />
        </div>
      )}

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
                className="btn-primary mt-4"
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

      {/* Personalized learner model — only after we have evidence */}
      {learner !== null && (
        <div className="mt-12 border-t border-neutral-200 pt-10">
          <h2 className="text-lg font-semibold tracking-tight">Your learning model</h2>
          <p className="mt-1 text-sm text-neutral-500">
            Derived from your submissions — mastery, mistakes, and how you work. Low-confidence
            estimates are labelled unknown, not weak.
          </p>

          {/* Skills */}
          <h3 className="mt-8 text-sm font-semibold uppercase tracking-wide text-neutral-500">
            Skills
          </h3>
          {learner.skills.length === 0 ? (
            <p className="mt-3 rounded-lg border border-dashed border-neutral-300 bg-white px-5 py-8 text-center text-sm text-neutral-500">
              Not enough evidence yet. Submit a few solutions and your skill estimates will appear here,
              weakest first.
            </p>
          ) : (
            <ul className="mt-3 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white">
              {learner.skills.map((skill) => (
                <li key={skill.skill_slug} className="px-5 py-4">
                  <div className="flex items-center gap-3">
                    <span className="min-w-0 flex-1 truncate font-medium">{skill.skill_name}</span>
                    <span className="text-xs text-neutral-500">{masteryLabel(skill.mastery)}</span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        skill.reliability === "unknown"
                          ? "bg-neutral-100 text-neutral-600"
                          : "bg-sky-100 text-sky-800"
                      }`}
                    >
                      {skill.reliability === "unknown" ? "unknown" : "estimated"}
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-neutral-100">
                    <div
                      className="h-full rounded-full bg-neutral-900 transition-all"
                      style={{ width: `${Math.round(skill.mastery * 100)}%` }}
                    />
                  </div>
                  <p className="mt-1.5 text-xs text-neutral-500">
                    mastery {skill.mastery.toFixed(2)} · confidence {skill.confidence.toFixed(2)} ·{" "}
                    {skill.evidence_count} evidence ·{" "}
                    {skill.last_practiced_at
                      ? new Date(skill.last_practiced_at).toLocaleDateString()
                      : "never practiced"}
                  </p>
                </li>
              ))}
            </ul>
          )}

          {/* Open mistakes */}
          <h3 className="mt-8 text-sm font-semibold uppercase tracking-wide text-neutral-500">
            Open mistakes
          </h3>
          {learner.open_mistakes.length === 0 ? (
            <p className="mt-3 rounded-lg border border-neutral-200 bg-white px-5 py-6 text-center text-sm text-neutral-500">
              No open mistakes — keep it up.
            </p>
          ) : (
            <ul className="mt-3 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white">
              {learner.open_mistakes.map((mistake, index) => (
                <li key={index} className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityBadge(mistake.severity)}`}
                    >
                      {mistake.severity}
                    </span>
                    <span className="font-medium">{mistake.category_name}</span>
                    <span className="text-xs text-neutral-400">· {mistake.category_code}</span>
                    <Link
                      href={`/problems/${mistake.problem_slug}`}
                      className="ml-auto text-xs text-neutral-500 hover:underline"
                    >
                      {mistake.problem_slug}
                    </Link>
                  </div>
                  {mistake.evidence_note && (
                    <p className="mt-1.5 text-sm text-neutral-600">{mistake.evidence_note}</p>
                  )}
                  <p className="mt-1 text-xs text-neutral-400">
                    confidence {mistake.confidence.toFixed(2)} ·{" "}
                    {new Date(mistake.detected_at).toLocaleDateString()}
                  </p>
                </li>
              ))}
            </ul>
          )}

          {/* Recurring mistake patterns */}
          {learner.mistake_patterns.length > 0 && (
            <>
              <h3 className="mt-8 text-sm font-semibold uppercase tracking-wide text-neutral-500">
                Recurring patterns
              </h3>
              <ul className="mt-3 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white">
                {learner.mistake_patterns.map((pattern, index) => (
                  <li key={index} className="flex items-center gap-3 px-5 py-4 text-sm">
                    <span className="font-medium">{pattern.category_name}</span>
                    <span className="text-neutral-500">on {pattern.skill_slug}</span>
                    <span className="ml-auto rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                      ×{pattern.occurrence_count}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}

          {/* Behavior patterns */}
          {learner.behavior_patterns.length > 0 && (
            <>
              <h3 className="mt-8 text-sm font-semibold uppercase tracking-wide text-neutral-500">
                How you work
              </h3>
              <ul className="mt-3 divide-y divide-neutral-200 rounded-lg border border-neutral-200 bg-white">
                {learner.behavior_patterns.map((pattern, index) => (
                  <li key={index} className="flex items-center gap-3 px-5 py-4 text-sm">
                    <span className="font-medium">
                      {pattern.behavior_type.replace(/_/g, " ").toLowerCase()}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityBadge(pattern.severity)}`}
                    >
                      {pattern.severity}
                    </span>
                    <span className="ml-auto text-xs text-neutral-500">
                      ×{pattern.frequency} · confidence {pattern.confidence.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

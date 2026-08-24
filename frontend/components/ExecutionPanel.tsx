"use client";

import type { CaseResult, ExecutionResult } from "@/lib/api";

const STATUS_STYLES: Record<string, string> = {
  SUCCESS: "bg-emerald-100 text-emerald-800",
  COMPILE_ERROR: "bg-red-100 text-red-800",
  RUNTIME_ERROR: "bg-red-100 text-red-800",
  TIMEOUT: "bg-amber-100 text-amber-800",
  MEMORY_LIMIT: "bg-amber-100 text-amber-800",
  SYSTEM_ERROR: "bg-neutral-200 text-neutral-700",
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
        STATUS_STYLES[status] ?? "bg-neutral-100"
      }`}
    >
      {status.replaceAll("_", " ")}
    </span>
  );
}

export function ExecutionPanel({ result }: { result: ExecutionResult }) {
  const allPassed =
    result.summary.total > 0 && result.summary.passed === result.summary.total;

  return (
    <section className="mt-6 rounded-lg border border-neutral-200 bg-white p-5">
      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge status={result.status} />
        <span className="text-sm text-neutral-600">
          {result.summary.passed}/{result.summary.total} passed
        </span>
        {result.runtime_ms !== null && (
          <span className="text-sm text-neutral-400">{result.runtime_ms} ms</span>
        )}
        <span className="ml-auto rounded-full bg-neutral-100 px-2.5 py-0.5 text-xs uppercase tracking-wide text-neutral-500">
          {result.mode}
        </span>
      </div>

      {result.message && (
        <p
          className={`mt-4 rounded-md px-3 py-2 text-sm ${
            result.status === "SUCCESS"
              ? "bg-sky-50 text-sky-800"
              : "bg-red-50 font-mono text-red-800"
          }`}
        >
          {result.message}
        </p>
      )}

      <ul className="mt-4 space-y-2">
        {result.results.map((entry: CaseResult, index) =>
          entry.visibility === "visible" ? (
            <li
              key={entry.name ?? index}
              className={`rounded-md border px-3 py-2 text-sm ${
                entry.passed
                  ? "border-emerald-200 bg-emerald-50/50"
                  : "border-red-200 bg-red-50/50"
              }`}
            >
              <span className="font-medium">{entry.passed ? "✓" : "✗"}</span>{" "}
              {entry.name}
              {!entry.passed && (
                <div className="mt-1 space-y-0.5 text-neutral-600">
                  {"expected_output" in entry && (
                    <p>
                      expected{" "}
                      <code className="rounded bg-white px-1">
                        {JSON.stringify(entry.expected_output)}
                      </code>
                    </p>
                  )}
                  {"actual_output" in entry && entry.actual_output !== undefined && entry.actual_output !== null && (
                    <p>
                      got{" "}
                      <code className="rounded bg-white px-1">
                        {JSON.stringify(entry.actual_output)}
                      </code>
                    </p>
                  )}
                  {entry.error && <p className="font-mono">{entry.error}</p>}
                </div>
              )}
            </li>
          ) : (
            <li
              key={index}
              className={`rounded-md border px-3 py-2 text-sm ${
                entry.passed
                  ? "border-emerald-200 bg-emerald-50/50 text-neutral-500"
                  : "border-amber-300 bg-amber-50"
              }`}
            >
              {entry.passed ? "✓" : "✗"} hidden case
              {entry.error && !entry.passed && (
                <span className="ml-2 font-mono text-xs text-neutral-500">
                  {entry.error}
                </span>
              )}
            </li>
          ),
        )}
      </ul>

      {allPassed && result.mode === "submit" && (
        <p className="mt-4 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          All cases passed — including the hidden ones. That is evidence of real
          understanding, not just pattern matching.
        </p>
      )}

      {(result.stdout_tail || result.stderr_tail) && (
        <details className="mt-4">
          <summary className="cursor-pointer text-sm text-neutral-500">
            Program output
          </summary>
          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-neutral-900 p-3 text-xs leading-relaxed text-neutral-100">
            {result.stdout_tail}
            {result.stderr_tail && `\n[stderr]\n${result.stderr_tail}`}
          </pre>
        </details>
      )}
    </section>
  );
}

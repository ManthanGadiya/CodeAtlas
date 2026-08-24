"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { ApiError, api, type ExecutionResult, type ProblemDetail } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useAuth";
import { ExecutionPanel } from "@/components/ExecutionPanel";
import { Skeleton } from "@/components/Skeleton";

export default function ProblemPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const { student, loading: authLoading, offline } = useRequireAuth();

  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [running, setRunning] = useState<"run" | "submit" | null>(null);
  // Slug-scoped so client-side navigation between problems re-emits.
  const openedForSlugRef = useRef<string | null>(null);

  useEffect(() => {
    if (!student || !slug) return;
    let cancelled = false;
    api
      .getProblem(slug)
      .then((detail) => {
        if (cancelled) return;
        setProblem(detail);
        setCode(detail.starter_code);
        // Evidence: the learning stream records which problems get attempted.
        if (openedForSlugRef.current !== slug) {
          openedForSlugRef.current = slug;
          api.recordEvent("PROBLEM_OPENED", { problem_slug: slug }).catch(() => {
            /* observational only — never block the learner */
          });
        }
      })
      .catch((err: ApiError) => {
        if (!cancelled) setLoadError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [student, slug]);

  function handleTabKey(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Tab") return;
    event.preventDefault();
    const editor = event.currentTarget;
    const { selectionStart, selectionEnd } = editor;
    const next = `${code.slice(0, selectionStart)}    ${code.slice(selectionEnd)}`;
    setCode(next);
    requestAnimationFrame(() => {
      editor.selectionStart = editor.selectionEnd = selectionStart + 4;
    });
  }

  async function execute(kind: "run" | "submit") {
    if (!slug) return;
    setRunning(kind);
    setResult(null);
    try {
      const outcome =
        kind === "run"
          ? await api.runCode(slug, code)
          : await api.submitCode(slug, code);
      setResult(outcome);
    } catch (err) {
      setResult({
        status: "SYSTEM_ERROR",
        mode: kind,
        runtime_ms: null,
        summary: { passed: 0, total: 0 },
        results: [],
        stdout_tail: "",
        stderr_tail: "",
        message:
          err instanceof ApiError ? err.message : "Request failed unexpectedly.",
      });
    } finally {
      setRunning(null);
    }
  }

  if (authLoading || !student) {
    return (
      <p className="text-neutral-500">
        {offline ? "Cannot reach the CodeAtlas backend — is it running?" : "…"}
      </p>
    );
  }

  if (loadError) {
    return (
      <p className="mt-6 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
        {loadError}
      </p>
    );
  }

  if (!problem) {
    return (
      <div className="grid gap-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
        <div className="space-y-4">
          <Skeleton className="h-7 w-2/3" />
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-32" />
          <Skeleton className="h-20" />
        </div>
        <Skeleton className="h-[22rem]" />
      </div>
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
      <section>
        <h1 className="text-2xl font-semibold tracking-tight">{problem.title}</h1>
        <p className="mt-1 flex gap-2 text-sm text-neutral-500">
          <span className="capitalize">{problem.difficulty}</span>
          <span>·</span>
          <span>{problem.language}</span>
          {problem.estimated_minutes !== null && (
            <>
              <span>·</span>
              <span>~{problem.estimated_minutes} min</span>
            </>
          )}
        </p>

        <div className="prose prose-sm mt-4 max-w-none whitespace-pre-wrap text-neutral-800">
          {problem.description}
        </div>

        {problem.examples.length > 0 && (
          <div className="mt-6">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
              Examples
            </h2>
            <ul className="mt-2 space-y-3">
              {problem.examples.map((example) => (
                <li key={example.name} className="rounded-md bg-white p-3 text-sm shadow-sm">
                  <p className="font-medium">{example.name}</p>
                  <p className="mt-1 font-mono text-xs text-neutral-600">
                    in: {JSON.stringify(example.input_args)}
                  </p>
                  <p className="font-mono text-xs text-emerald-700">
                    out: {JSON.stringify(example.expected_output)}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section>
        <textarea
          value={code}
          onChange={(event) => setCode(event.target.value)}
          onKeyDown={handleTabKey}
          spellCheck={false}
          rows={18}
          className="w-full resize-y rounded-lg border border-neutral-300 bg-white p-4 font-mono text-sm leading-relaxed focus:border-neutral-900 focus:outline-none"
          aria-label="Code editor"
        />

        <div className="mt-3 flex gap-3">
          <button
            onClick={() => execute("run")}
            disabled={running !== null}
            className="btn-secondary"
          >
            {running === "run" ? "Running…" : "▶ Run examples"}
          </button>
          <button
            onClick={() => execute("submit")}
            disabled={running !== null}
            className="btn-primary"
          >
            {running === "submit" ? "Submitting…" : "Submit"}
          </button>
          <span className="ml-auto self-center text-xs text-[var(--ink-faint)]">
            Submit grades hidden cases too
          </span>
        </div>

        {result && <ExecutionPanel result={result} />}
      </section>
    </div>
  );
}

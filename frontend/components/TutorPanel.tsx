"use client";

import { useState } from "react";
import { ApiError, api } from "@/lib/api";

interface HintState {
  content: string;
  hint_level: number;
  intervention: string;
  provider: string;
  is_fallback: boolean;
}

export function TutorPanel({
  slug,
  code,
}: {
  slug: string;
  code: string;
}) {
  const [hint, setHint] = useState<HintState | null>(null);
  const [history, setHistory] = useState<HintState[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [explicitLevel, setExplicitLevel] = useState<number | null>(null);

  async function askHint(requestedLevel: number | null) {
    setLoading(true);
    setError(null);
    try {
      const res = await api.tutorHint(slug, code, requestedLevel);
      const next: HintState = {
        content: res.content,
        hint_level: res.hint_level,
        intervention: res.intervention,
        provider: res.provider,
        is_fallback: res.is_fallback,
      };
      setHint(next);
      setHistory((prev) => [next, ...prev].slice(0, 5));
      if (res.hint_level >= 7) {
        setExplicitLevel(null);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Hint request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-6 rounded-lg border border-neutral-200 bg-white">
      <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-3">
        <h2 className="text-sm font-semibold tracking-wide text-neutral-700">
          Tutor
        </h2>
        <span className="text-xs text-neutral-500">
          Socratic first — minimal help that restores progress
        </span>
      </div>

      <div className="space-y-3 px-4 py-4">
        {/* Contextual actions (DESIGN.md §14) */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => askHint(null)}
            disabled={loading}
            className="rounded-full border border-neutral-900 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {loading ? "Thinking…" : "💡 Need a hint"}
          </button>
          <button
            onClick={() => askHint(2)}
            disabled={loading}
            className="rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
          >
            🔍 Explain this error
          </button>
          <button
            onClick={() => askHint(4)}
            disabled={loading}
            className="rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
          >
            🧠 What concept am I missing?
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs text-neutral-500">
          <label className="flex items-center gap-1">
            <span>Level</span>
            <select
              value={explicitLevel ?? ""}
              onChange={(e) => {
                const v = e.target.value;
                setExplicitLevel(v === "" ? null : Number(v));
              }}
              className="rounded border border-neutral-300 bg-white px-2 py-1"
            >
              <option value="">auto-escalate</option>
              {[0, 1, 2, 3, 4, 5, 6, 7].map((n) => (
                <option key={n} value={n}>
                  {n} — {levelLabel(n)}
                </option>
              ))}
            </select>
          </label>
          {explicitLevel !== null && (
            <button
              onClick={() => askHint(explicitLevel)}
              disabled={loading}
              className="rounded bg-neutral-100 px-3 py-1 hover:bg-neutral-200 disabled:opacity-50"
            >
              Ask level {explicitLevel}
            </button>
          )}
        </div>

        {error && (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}

        {hint && (
          <div className="rounded-md border border-sky-200 bg-sky-50 px-4 py-3">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="rounded-full bg-sky-900 px-2 py-0.5 font-medium text-white">
                Level {hint.hint_level}
              </span>
              <span className="rounded-full bg-white px-2 py-0.5 font-medium text-sky-900">
                {hint.intervention.replace(/_/g, " ").toLowerCase()}
              </span>
              <span className="text-neutral-500">via {hint.provider}</span>
              {hint.is_fallback && (
                <span className="text-neutral-400">· template</span>
              )}
            </div>
            <p className="mt-2 text-sm leading-relaxed text-neutral-800">
              {hint.content}
            </p>
          </div>
        )}

        {history.length > 1 && (
          <details className="rounded-md border border-neutral-200">
            <summary className="cursor-pointer px-3 py-2 text-sm font-medium text-neutral-700">
              Recent hints ({history.length})
            </summary>
            <ul className="divide-y divide-neutral-200 px-3 pb-2 text-sm">
              {history.slice(1).map((h, i) => (
                <li key={i} className="py-2">
                  <span className="text-xs text-neutral-500">
                    L{h.hint_level} · {h.intervention}
                  </span>
                  <p className="text-neutral-700">{h.content}</p>
                </li>
              ))}
            </ul>
          </details>
        )}

        <p className="text-xs leading-relaxed text-neutral-500">
          Hints are socratic by default. Each request escalates one level
          unless you pick a level. The tutor remembers your mistake and
          skill context — <span className="font-medium">template hints</span>{" "}
          work offline; LLM hints arrive when keys are configured.
        </p>
      </div>
    </div>
  );
}

function levelLabel(n: number): string {
  if (n === 0) return "observe silently";
  if (n === 1) return "directional question";
  if (n === 2) return "conceptual hint";
  if (n === 3) return "targeted hint";
  if (n === 4) return "explanation";
  if (n === 5) return "guided reasoning";
  if (n === 6) return "partial solution";
  return "full solution";
}

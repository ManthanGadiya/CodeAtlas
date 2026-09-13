// Typed API client for the CodeAtlas backend.
// All requests carry credentials so the HttpOnly session cookie flows.

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api${path}`, {
    credentials: "include",
    headers: init?.body ? { "Content-Type": "application/json" } : undefined,
    ...init,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // non-JSON error body; fall back to statusText
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export interface Student {
  id: string;
  email: string;
  display_name: string | null;
  preferred_language: string;
}

export interface ProblemSummary {
  slug: string;
  title: string;
  difficulty: string;
  language: string;
  estimated_minutes: number | null;
}

export interface VisibleExample {
  name: string;
  input_args: unknown[];
  expected_output: unknown;
}

export interface ProblemDetail extends ProblemSummary {
  description: string;
  starter_code: string;
  function_name: string;
  skills: string[];
  examples: VisibleExample[];
}

export interface CaseResult {
  name: string | null;
  visibility: "visible" | "hidden";
  passed: boolean;
  actual_output?: unknown;
  expected_output?: unknown;
  error?: string | null;
}

export interface ExecutionResult {
  status: string;
  mode: string;
  runtime_ms: number | null;
  summary: { passed: number; total: number };
  results: CaseResult[];
  stdout_tail: string;
  stderr_tail: string;
  message: string;
}

export interface AnalyticsSummary {
  totals: {
    runs: number;
    submits: number;
    executions: number;
    success_rate: number | null;
  };
  problems: { attempted: number; completed: number };
  recent_activity: Array<{
    problem_slug: string;
    problem_title: string;
    mode: string;
    status: string;
    passed: number;
    total: number;
    runtime_ms: number | null;
    at: string;
  }>;
  per_problem: Array<{
    problem_slug: string;
    problem_title: string;
    attempts: number;
    submits: number;
    completed: boolean;
  }>;
}

export interface LearnerSummary {
  skills: Array<{
    skill_slug: string;
    skill_name: string;
    mastery: number;
    confidence: number;
    reliability: "unknown" | "estimated";
    evidence_count: number;
    retention: number | null;
    last_practiced_at: string | null;
  }>;
  open_mistakes: Array<{
    category_code: string;
    category_name: string;
    problem_slug: string;
    severity: string;
    confidence: number;
    evidence_note: string | null;
    detected_at: string;
  }>;
  mistake_patterns: Array<{
    category_code: string;
    category_name: string;
    skill_slug: string;
    occurrence_count: number;
    confidence: number;
    last_seen_at: string;
  }>;
  behavior_patterns: Array<{
    behavior_type: string;
    frequency: number;
    severity: string;
    trend: string;
    confidence: number;
    last_observed_at: string;
  }>;
}

export const api = {
  accountStatus: () =>
    apiFetch<{ has_account: boolean }>("/auth/status"),

  register: (email: string, password: string) =>
    apiFetch<Student>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    apiFetch<Student>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () => apiFetch<void>("/auth/logout", { method: "POST" }),

  me: () => apiFetch<Student>("/auth/me"),

  listProblems: () => apiFetch<ProblemSummary[]>("/problems"),

  getProblem: (slug: string) => apiFetch<ProblemDetail>(`/problems/${slug}`),

  runCode: (slug: string, code: string) =>
    apiFetch<ExecutionResult>(`/problems/${slug}/run`, {
      method: "POST",
      body: JSON.stringify({ code }),
    }),

  submitCode: (slug: string, code: string) =>
    apiFetch<ExecutionResult>(`/problems/${slug}/submit`, {
      method: "POST",
      body: JSON.stringify({ code }),
    }),

  analyticsSummary: () => apiFetch<AnalyticsSummary>("/analytics/summary"),

  learnerSummary: () => apiFetch<LearnerSummary>("/analytics/learner"),

  recordEvent: (eventType: string, payload: Record<string, unknown>) =>
    apiFetch<{ id: string }>("/events", {
      method: "POST",
      body: JSON.stringify({ event_type: eventType, payload }),
    }),

  tutorHint: (slug: string, code: string | null, hintLevel: number | null) =>
    apiFetch<{
      interaction_id: string;
      problem_slug: string;
      hint_level: number;
      intervention: string;
      content: string;
      provider: string;
      is_fallback: boolean;
    }>("/tutor/hint", {
      method: "POST",
      body: JSON.stringify({
        problem_slug: slug,
        code: code ?? null,
        hint_level: hintLevel,
      }),
    }),

  tutorHistory: (problemSlug?: string, limit = 10) => {
    const qs = new URLSearchParams();
    if (problemSlug) qs.set("problem_slug", problemSlug);
    qs.set("limit", String(limit));
    return apiFetch<
      Array<{
        id: string;
        problem_slug: string | null;
        hint_level: number;
        intervention: string;
        provider: string;
        response: string;
        created_at: string;
      }>
    >(`/tutor/history?${qs.toString()}`);
  },

  retentionOverview: () =>
    apiFetch<
      Array<{
        skill_id: string;
        skill_slug: string;
        skill_name: string;
        mastery: number;
        stability: number;
        retrieval_probability: number;
        last_successful_retrieval: string | null;
        next_recommended_review: string | null;
        retrieval_count: number;
        due: boolean;
      }>
    >("/retention/overview"),

  retentionReview: (skillSlug: string, success: boolean) =>
    apiFetch<{
      skill_id: string;
      skill_slug: string;
      skill_name: string;
      mastery: number;
      stability: number;
      retrieval_probability: number;
      last_successful_retrieval: string | null;
      next_recommended_review: string | null;
      retrieval_count: number;
      due: boolean;
    }>("/retention/review", {
      method: "POST",
      body: JSON.stringify({ skill_slug: skillSlug, success }),
    }),

  curriculumNext: () =>
    apiFetch<{
      problem_slug: string;
      problem_title: string;
      difficulty: string;
      decision_type: string;
      target_skill_slug: string | null;
      reason: string;
      confidence: number;
      alternatives: Array<{
        problem_slug: string;
        problem_title: string;
        score: number;
        decision_type: string;
        reason: string;
      }>;
    }>("/curriculum/next"),

  curriculumDecisions: () =>
    apiFetch<
      Array<{
        id: string;
        problem_slug: string;
        decision_type: string;
        reason: string;
        confidence: number;
        created_at: string;
      }>
    >("/curriculum/decisions"),

  difficultyOverview: () =>
    apiFetch<
      Array<{
        slug: string;
        title: string;
        difficulty: string;
        overall: number;
        vector: {
          conceptual: number;
          implementation: number;
          reasoning: number;
          debugging: number;
          constraints: number;
          transfer: number;
        };
        confidence: number;
      }>
    >("/difficulty/overview"),

  difficultyEstimate: (slug: string) =>
    apiFetch<{
      slug: string;
      overall: number;
      vector: Record<string, number>;
      confidence: number;
      model_version: string;
      student_mastery: number;
      p_success: number;
      student_specific_difficulty: number;
      zone: string;
    }>(`/difficulty/estimate/${slug}`),

  difficultyRecommend: () =>
    apiFetch<{
      target_overall: number;
      band: string;
      avg_mastery: number;
      productive_problems: number;
      total_problems: number;
      reason: string;
    }>("/difficulty/recommend"),

  retrievalDue: () =>
    apiFetch<
      Array<{
        skill_id: string;
        skill_slug: string;
        skill_name: string;
        mastery: number;
        stability: number;
        retrieval_probability: number;
        due: boolean;
        recommended_problem_slug: string | null;
        ladder: string;
      }>
    >("/retrieval/due"),

  retrievalSchedule: (skillId?: string) =>
    apiFetch<{
      id: string;
      skill_id: string;
      problem_id: string | null;
      ladder_level: string;
      scheduled_for: string;
      status: string;
    }>("/retrieval/schedule", {
      method: "POST",
      body: JSON.stringify(skillId ? { skill_id: skillId } : {}),
    }),

  retrievalHistory: () =>
    apiFetch<
      Array<{
        id: string;
        skill_id: string;
        problem_id: string | null;
        ladder_level: string;
        scheduled_for: string;
        status: string;
        result: string | null;
        created_at: string;
      }>
    >("/retrieval/history"),

  transferDue: () =>
    apiFetch<
      Array<{
        skill_id: string;
        skill_slug: string;
        skill_name: string;
        mastery: number;
        evidence_count: number;
        source_problem_slug: string | null;
        suggested_level: string;
        level_desc: string;
      }>
    >("/transfer/due"),

  transferSchedule: (skillId?: string, level: string = "T2") =>
    apiFetch<{
      id: string;
      skill_id: string;
      source_problem_id: string | null;
      transfer_problem_id: string;
      transfer_level: string;
    }>("/transfer/schedule", {
      method: "POST",
      body: JSON.stringify(skillId ? { skill_id: skillId, transfer_level: level } : { transfer_level: level }),
    }),

  transferHistory: () =>
    apiFetch<
      Array<{
        id: string;
        skill_id: string;
        source_problem_id: string | null;
        transfer_problem_id: string;
        transfer_level: string;
        result: string | null;
        created_at: string;
        completed_at: string | null;
      }>
    >("/transfer/history"),
};

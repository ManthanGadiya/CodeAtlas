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
};

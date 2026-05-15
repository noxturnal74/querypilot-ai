export type Suggestion = {
  category: string;
  severity: string;
  message: string;
  rationale: string;
};

export type Risk = {
  level: string;
  code: string;
  message: string;
};

export type IndexRecommendation = {
  table_name: string;
  columns: string[];
  statement: string;
  confidence: number;
  reason: string;
};

export type Analysis = {
  id: number;
  title: string;
  query: string;
  dialect: string;
  status: string;
  risk_level: string;
  score: number;
  summary: string;
  plan_notes: string;
  ai_summary: string;
  created_at: string;
  suggestions: Suggestion[];
  risks: Risk[];
  indexes: IndexRecommendation[];
};

export type AnalysisListItem = Pick<
  Analysis,
  "id" | "title" | "dialect" | "risk_level" | "score" | "summary" | "created_at"
>;

export type SchemaContext = {
  id: number;
  name: string;
  description: string | null;
  ddl: string;
  created_at: string;
};

export type AnalyzePayload = {
  title?: string;
  query: string;
  dialect: string;
  schema_context_id?: number;
  schema_text?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function listAnalyses() {
  return request<AnalysisListItem[]>("/analyses");
}

export function getAnalysis(id: number) {
  return request<Analysis>(`/analyses/${id}`);
}

export function analyzeQuery(payload: AnalyzePayload) {
  return request<Analysis>("/analyze", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listSchemas() {
  return request<SchemaContext[]>("/schemas");
}

export function createSchema(payload: Pick<SchemaContext, "name" | "description" | "ddl">) {
  return request<SchemaContext>("/schemas", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

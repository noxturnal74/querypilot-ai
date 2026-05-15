"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Database, History, Loader2, Play, Save, SearchCode, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/Badge";
import { Metric } from "@/components/Metric";
import {
  Analysis,
  AnalysisListItem,
  SchemaContext,
  analyzeQuery,
  createSchema,
  getAnalysis,
  listAnalyses,
  listSchemas
} from "@/lib/api";

const SAMPLE_QUERY = `SELECT *
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE c.status = 'active'
ORDER BY o.created_at DESC`;

const SAMPLE_SCHEMA = `CREATE TABLE customers (
  id bigint PRIMARY KEY,
  email text NOT NULL,
  status text NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE orders (
  id bigint PRIMARY KEY,
  customer_id bigint NOT NULL REFERENCES customers(id),
  total numeric(12,2) NOT NULL,
  status text NOT NULL,
  created_at timestamptz NOT NULL
);`;

export function QueryPilotDashboard() {
  const [query, setQuery] = useState(SAMPLE_QUERY);
  const [schemaText, setSchemaText] = useState(SAMPLE_SCHEMA);
  const [title, setTitle] = useState("Active customers with recent orders");
  const [dialect, setDialect] = useState("postgresql");
  const [history, setHistory] = useState<AnalysisListItem[]>([]);
  const [schemas, setSchemas] = useState<SchemaContext[]>([]);
  const [selectedSchemaId, setSelectedSchemaId] = useState<number | "inline">("inline");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSavingSchema, setIsSavingSchema] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refreshData();
  }, []);

  async function refreshData() {
    try {
      const [analysisHistory, schemaContexts] = await Promise.all([listAnalyses(), listSchemas()]);
      setHistory(analysisHistory);
      setSchemas(schemaContexts);
      if (!analysis && analysisHistory.length > 0) {
        setAnalysis(await getAnalysis(analysisHistory[0].id));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard data.");
    }
  }

  async function handleAnalyze() {
    setIsAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeQuery({
        title,
        query,
        dialect,
        schema_context_id: selectedSchemaId === "inline" ? undefined : selectedSchemaId,
        schema_text: selectedSchemaId === "inline" ? schemaText : undefined
      });
      setAnalysis(result);
      setHistory(await listAnalyses());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleSaveSchema() {
    setIsSavingSchema(true);
    setError(null);
    try {
      const schema = await createSchema({
        name: title ? `${title} schema` : "Uploaded schema",
        description: "Saved from dashboard schema context editor.",
        ddl: schemaText
      });
      const updated = await listSchemas();
      setSchemas(updated);
      setSelectedSchemaId(schema.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Schema save failed.");
    } finally {
      setIsSavingSchema(false);
    }
  }

  const riskTone = useMemo(() => {
    if (!analysis) return "neutral";
    return analysis.risk_level as "low" | "medium" | "high";
  }, [analysis]);

  return (
    <main className="min-h-screen bg-[#f4f6f8] text-ink">
      <div className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div>
            <h1 className="text-2xl font-semibold">QueryPilot AI</h1>
            <p className="mt-1 text-sm text-slate-600">AI SQL Performance Copilot</p>
          </div>
          <div className="hidden items-center gap-3 md:flex">
            <Badge tone="neutral">Mock AI mode</Badge>
            <Badge tone={analysis ? riskTone : "neutral"}>{analysis ? `${analysis.risk_level} risk` : "Ready"}</Badge>
          </div>
        </div>
      </div>

      <div className="mx-auto grid max-w-7xl gap-5 px-5 py-5 lg:grid-cols-[360px_minmax(0,1fr)_300px]">
        <aside className="space-y-5">
          <section className="rounded border border-line bg-white p-4">
            <div className="mb-3 flex items-center gap-2">
              <SearchCode className="h-5 w-5 text-accent" />
              <h2 className="text-base font-semibold">Analyze Query</h2>
            </div>
            <label className="text-xs font-medium uppercase tracking-normal text-slate-500">Title</label>
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="mt-1 h-10 w-full rounded border border-line bg-white px-3 text-sm outline-none focus:border-accent"
            />
            <label className="mt-4 block text-xs font-medium uppercase tracking-normal text-slate-500">Dialect</label>
            <select
              value={dialect}
              onChange={(event) => setDialect(event.target.value)}
              className="mt-1 h-10 w-full rounded border border-line bg-white px-3 text-sm outline-none focus:border-accent"
            >
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="sqlserver">SQL Server</option>
            </select>
            <label className="mt-4 block text-xs font-medium uppercase tracking-normal text-slate-500">SQL</label>
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="mt-1 min-h-[260px] w-full resize-y rounded border border-line bg-[#101828] p-3 font-mono text-sm leading-6 text-slate-50 outline-none focus:border-accent"
              spellCheck={false}
            />
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || query.trim().length === 0}
              className="mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded bg-accent px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {isAnalyzing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              Run Analysis
            </button>
          </section>

          <section className="rounded border border-line bg-white p-4">
            <div className="mb-3 flex items-center gap-2">
              <Database className="h-5 w-5 text-accent" />
              <h2 className="text-base font-semibold">Schema Context</h2>
            </div>
            <select
              value={selectedSchemaId}
              onChange={(event) =>
                setSelectedSchemaId(event.target.value === "inline" ? "inline" : Number(event.target.value))
              }
              className="h-10 w-full rounded border border-line bg-white px-3 text-sm outline-none focus:border-accent"
            >
              <option value="inline">Inline schema text</option>
              {schemas.map((schema) => (
                <option key={schema.id} value={schema.id}>
                  {schema.name}
                </option>
              ))}
            </select>
            <textarea
              value={schemaText}
              onChange={(event) => setSchemaText(event.target.value)}
              className="mt-3 min-h-[180px] w-full resize-y rounded border border-line p-3 font-mono text-xs leading-5 outline-none focus:border-accent"
              spellCheck={false}
            />
            <button
              onClick={handleSaveSchema}
              disabled={isSavingSchema || schemaText.trim().length === 0}
              className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:text-slate-400"
            >
              {isSavingSchema ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save Schema
            </button>
          </section>
        </aside>

        <section className="space-y-5">
          {error ? (
            <div className="rounded border border-red-200 bg-red-50 p-4 text-sm text-danger">{error}</div>
          ) : null}

          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded border border-line bg-white p-4">
              <Metric label="Performance Score" value={analysis ? `${Math.round(analysis.score)}` : "--"} />
            </div>
            <div className="rounded border border-line bg-white p-4">
              <Metric label="Risk Level" value={analysis ? analysis.risk_level.toUpperCase() : "--"} />
            </div>
            <div className="rounded border border-line bg-white p-4">
              <Metric label="Index Ideas" value={analysis ? `${analysis.indexes.length}` : "--"} />
            </div>
          </div>

          <section className="rounded border border-line bg-white p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold">{analysis?.title ?? "No analysis selected"}</h2>
                <p className="mt-1 text-sm text-slate-600">{analysis?.summary ?? "Run a SQL analysis to populate results."}</p>
              </div>
              <ShieldCheck className="h-6 w-6 shrink-0 text-accent" />
            </div>
            {analysis ? (
              <div className="mt-4 rounded border border-line bg-panel p-3 text-sm text-slate-700">{analysis.ai_summary}</div>
            ) : null}
          </section>

          <section className="grid gap-5 xl:grid-cols-2">
            <ResultList
              title="Optimization Suggestions"
              empty="No suggestions yet."
              items={analysis?.suggestions.map((item) => ({
                key: `${item.category}-${item.message}`,
                badge: item.severity,
                title: item.message,
                body: item.rationale
              }))}
            />
            <ResultList
              title="Risk Detection"
              empty="No risk signals yet."
              icon={<AlertTriangle className="h-5 w-5 text-warning" />}
              items={analysis?.risks.map((item) => ({
                key: item.code,
                badge: item.level,
                title: item.message,
                body: item.code
              }))}
            />
          </section>

          <section className="rounded border border-line bg-white p-5">
            <h2 className="text-lg font-semibold">Index Recommendations</h2>
            <div className="mt-4 space-y-3">
              {analysis?.indexes.length ? (
                analysis.indexes.map((index) => (
                  <div key={index.statement} className="rounded border border-line bg-panel p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="font-semibold">{index.table_name}</div>
                      <Badge tone="neutral">{Math.round(index.confidence * 100)}% confidence</Badge>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{index.reason}</p>
                    <pre className="mt-3 overflow-x-auto rounded bg-[#101828] p-3 text-xs leading-5 text-slate-50">
                      {index.statement}
                    </pre>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-600">No index recommendations yet.</p>
              )}
            </div>
          </section>
        </section>

        <aside className="rounded border border-line bg-white p-4">
          <div className="mb-3 flex items-center gap-2">
            <History className="h-5 w-5 text-accent" />
            <h2 className="text-base font-semibold">Analysis History</h2>
          </div>
          <div className="space-y-2">
            {history.map((item) => (
              <button
                key={item.id}
                onClick={async () => setAnalysis(await getAnalysis(item.id))}
                className="w-full rounded border border-line bg-white p-3 text-left hover:border-accent"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="line-clamp-1 text-sm font-semibold">{item.title}</span>
                  <Badge tone={item.risk_level as "low" | "medium" | "high"}>{item.risk_level}</Badge>
                </div>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-600">{item.summary}</p>
              </button>
            ))}
            {history.length === 0 ? <p className="text-sm text-slate-600">No saved analyses yet.</p> : null}
          </div>
        </aside>
      </div>
    </main>
  );
}

function ResultList({
  title,
  empty,
  items,
  icon
}: {
  title: string;
  empty: string;
  items?: { key: string; badge: string; title: string; body: string }[];
  icon?: React.ReactNode;
}) {
  return (
    <section className="rounded border border-line bg-white p-5">
      <div className="flex items-center gap-2">
        {icon}
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="mt-4 space-y-3">
        {items?.length ? (
          items.map((item) => (
            <div key={item.key} className="rounded border border-line bg-panel p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="font-semibold">{item.title}</div>
                <Badge tone={item.badge as "low" | "medium" | "high"}>{item.badge}</Badge>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.body}</p>
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-600">{empty}</p>
        )}
      </div>
    </section>
  );
}

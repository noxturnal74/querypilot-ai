import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Suggestion:
    category: str
    severity: str
    message: str
    rationale: str


@dataclass(frozen=True)
class Risk:
    level: str
    code: str
    message: str


@dataclass(frozen=True)
class IndexRecommendation:
    table_name: str
    columns: list[str]
    statement: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class AnalysisResult:
    score: float
    risk_level: str
    summary: str
    plan_notes: str
    suggestions: list[Suggestion]
    risks: list[Risk]
    indexes: list[IndexRecommendation]


TABLE_PATTERN = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][\w.]*)", re.IGNORECASE)
WHERE_PATTERN = re.compile(r"\bwhere\b(.+?)(?:\bgroup\s+by\b|\border\s+by\b|\blimit\b|$)", re.IGNORECASE | re.DOTALL)
JOIN_CONDITION_PATTERN = re.compile(r"\bjoin\s+([a-zA-Z_][\w.]*)\s+(?:as\s+)?([a-zA-Z_]\w*)?.*?\bon\s+(.+?)(?:\bjoin\b|\bwhere\b|\bgroup\s+by\b|\border\s+by\b|$)", re.IGNORECASE | re.DOTALL)
COLUMN_COMPARISON_PATTERN = re.compile(r"([a-zA-Z_][\w.]*?)\s*(=|>|<|>=|<=|in\s*\(|like)\s*[:?$'\w.(]", re.IGNORECASE)


class SQLAnalyzer:
    def analyze(self, query: str, schema_text: str | None = None) -> AnalysisResult:
        normalized = " ".join(query.strip().split())
        lowered = normalized.lower()
        suggestions: list[Suggestion] = []
        risks: list[Risk] = []
        indexes: list[IndexRecommendation] = []

        tables = self._extract_tables(normalized)
        filter_columns = self._extract_filter_columns(normalized)
        join_columns = self._extract_join_columns(normalized)

        if "select *" in lowered:
            suggestions.append(
                Suggestion(
                    "projection",
                    "medium",
                    "Avoid SELECT * in production queries.",
                    "Selecting only required columns reduces I/O, memory pressure, and network transfer.",
                )
            )
            risks.append(Risk("medium", "wide_projection", "SELECT * can amplify scan cost and expose unnecessary data."))

        if " where " not in f" {lowered} " and any(token in lowered for token in ["select", "update", "delete"]):
            risks.append(Risk("high", "missing_filter", "Query has no WHERE clause and may scan or mutate a large table."))
            suggestions.append(
                Suggestion(
                    "filtering",
                    "high",
                    "Add selective predicates or an intentional LIMIT for exploratory reads.",
                    "Unbounded queries are a common source of latency spikes and lock contention.",
                )
            )

        if " like '%" in lowered or " ilike '%" in lowered:
            risks.append(Risk("medium", "leading_wildcard", "Leading wildcard pattern prevents normal b-tree index seeks."))
            suggestions.append(
                Suggestion(
                    "search",
                    "medium",
                    "Use full-text search, trigram indexes, or prefix-search patterns for wildcard lookups.",
                    "A leading wildcard usually forces a sequential scan even when an index exists.",
                )
            )

        if " order by " in lowered and " limit " not in lowered:
            suggestions.append(
                Suggestion(
                    "sorting",
                    "medium",
                    "Pair ORDER BY with LIMIT or a supporting index when only top results are needed.",
                    "Large sorts can spill to disk and dominate query runtime.",
                )
            )

        if lowered.count(" join ") >= 3:
            risks.append(Risk("medium", "join_complexity", "Query joins several tables; review join cardinality and join keys."))

        if " not in " in lowered:
            suggestions.append(
                Suggestion(
                    "predicate",
                    "medium",
                    "Consider NOT EXISTS instead of NOT IN when nullable values are possible.",
                    "NOT IN has surprising NULL semantics and can produce inefficient plans.",
                )
            )

        index_targets = self._build_index_targets(tables, filter_columns, join_columns)
        for table, columns, reason, confidence in index_targets:
            index_name = f"idx_{table.replace('.', '_')}_{'_'.join(columns)}"
            col_sql = ", ".join(columns)
            indexes.append(
                IndexRecommendation(
                    table,
                    columns,
                    f"CREATE INDEX CONCURRENTLY {index_name} ON {table} ({col_sql});",
                    confidence,
                    reason,
                )
            )

        if schema_text and tables:
            suggestions.append(
                Suggestion(
                    "schema_context",
                    "low",
                    "Validate recommendations against existing indexes before creating new ones.",
                    "Schema context improves targeting, but duplicate or overlapping indexes should be avoided.",
                )
            )

        score = self._score(risks, suggestions)
        risk_level = self._risk_level(risks, score)
        summary = self._summary(tables, risks, suggestions, indexes)
        plan_notes = self._plan_notes(tables, filter_columns, join_columns)

        return AnalysisResult(score, risk_level, summary, plan_notes, suggestions, risks, indexes)

    def _extract_tables(self, query: str) -> list[str]:
        return list(dict.fromkeys(match.group(1) for match in TABLE_PATTERN.finditer(query)))

    def _extract_filter_columns(self, query: str) -> list[str]:
        match = WHERE_PATTERN.search(query)
        if not match:
            return []
        return self._clean_columns([m.group(1) for m in COLUMN_COMPARISON_PATTERN.finditer(match.group(1))])

    def _extract_join_columns(self, query: str) -> list[str]:
        columns: list[str] = []
        for match in JOIN_CONDITION_PATTERN.finditer(query):
            columns.extend(re.findall(r"([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)", match.group(3)))
        return self._clean_columns([column for _, column in columns])

    def _clean_columns(self, columns: list[str]) -> list[str]:
        cleaned: list[str] = []
        for column in columns:
            simple = column.split(".")[-1].strip().strip("()")
            if simple and simple.lower() not in {"and", "or", "not", "null"}:
                cleaned.append(simple)
        return list(dict.fromkeys(cleaned))

    def _build_index_targets(
        self, tables: list[str], filter_columns: list[str], join_columns: list[str]
    ) -> list[tuple[str, list[str], str, float]]:
        if not tables:
            return []
        targets: list[tuple[str, list[str], str, float]] = []
        primary_table = tables[0]
        if filter_columns:
            targets.append((primary_table, filter_columns[:3], "Supports selective WHERE predicates.", 0.82))
        for table in tables[1:]:
            if join_columns:
                targets.append((table, join_columns[:2], "Supports join key lookups and reduces nested loop cost.", 0.76))
        return targets

    def _score(self, risks: list[Risk], suggestions: list[Suggestion]) -> float:
        penalty = 0
        for risk in risks:
            penalty += {"high": 30, "medium": 15, "low": 5}.get(risk.level, 5)
        for suggestion in suggestions:
            penalty += {"high": 10, "medium": 6, "low": 2}.get(suggestion.severity, 2)
        return max(0.0, min(100.0, 100 - penalty))

    def _risk_level(self, risks: list[Risk], score: float) -> str:
        if any(risk.level == "high" for risk in risks) or score < 55:
            return "high"
        if any(risk.level == "medium" for risk in risks) or score < 80:
            return "medium"
        return "low"

    def _summary(
        self,
        tables: list[str],
        risks: list[Risk],
        suggestions: list[Suggestion],
        indexes: list[IndexRecommendation],
    ) -> str:
        table_text = ", ".join(tables) if tables else "unknown tables"
        return (
            f"Analyzed query against {table_text}. Found {len(risks)} risk signal(s), "
            f"{len(suggestions)} optimization suggestion(s), and {len(indexes)} index recommendation(s)."
        )

    def _plan_notes(self, tables: list[str], filter_columns: list[str], join_columns: list[str]) -> str:
        parts = [
            f"Tables: {', '.join(tables) if tables else 'not detected'}",
            f"Filter columns: {', '.join(filter_columns) if filter_columns else 'none detected'}",
            f"Join columns: {', '.join(join_columns) if join_columns else 'none detected'}",
        ]
        return " | ".join(parts)

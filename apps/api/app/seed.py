from sqlalchemy.orm import Session

from app.db.models import Analysis, IndexRecommendation, Risk, SchemaContext, Suggestion
from app.services.sql_analyzer import SQLAnalyzer

DEMO_SCHEMA = """
CREATE TABLE customers (
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
);
"""

DEMO_QUERY = """
SELECT *
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE c.status = 'active'
ORDER BY o.created_at DESC
"""


def seed_demo_data(db: Session) -> None:
    if db.query(SchemaContext).count() > 0 or db.query(Analysis).count() > 0:
        return
    schema = SchemaContext(name="Demo ecommerce schema", description="Customers and orders demo schema.", ddl=DEMO_SCHEMA)
    result = SQLAnalyzer().analyze(DEMO_QUERY, DEMO_SCHEMA)
    analysis = Analysis(
        title="Active customers with recent orders",
        query=DEMO_QUERY,
        dialect="postgresql",
        risk_level=result.risk_level,
        score=result.score,
        summary=result.summary,
        plan_notes=result.plan_notes,
        ai_summary="Mock AI review: validate with EXPLAIN ANALYZE and compare index write overhead before rollout.",
        schema_context=schema,
    )
    analysis.suggestions = [Suggestion(**item.__dict__) for item in result.suggestions]
    analysis.risks = [Risk(**item.__dict__) for item in result.risks]
    analysis.indexes = [
        IndexRecommendation(
            table_name=item.table_name,
            columns=",".join(item.columns),
            statement=item.statement,
            confidence=item.confidence,
            reason=item.reason,
        )
        for item in result.indexes
    ]
    db.add(schema)
    db.add(analysis)
    db.commit()

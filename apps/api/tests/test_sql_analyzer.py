from app.services.sql_analyzer import SQLAnalyzer


def test_analyzer_detects_wide_projection_and_index_candidates():
    query = """
    SELECT *
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE c.status = 'active'
    ORDER BY o.created_at DESC
    """

    result = SQLAnalyzer().analyze(query)

    assert result.risk_level in {"medium", "high"}
    assert any(risk.code == "wide_projection" for risk in result.risks)
    assert any(suggestion.category == "projection" for suggestion in result.suggestions)
    assert result.indexes
    assert "CREATE INDEX CONCURRENTLY" in result.indexes[0].statement


def test_analyzer_flags_unbounded_query():
    result = SQLAnalyzer().analyze("SELECT id, email FROM customers")

    assert result.risk_level == "high"
    assert any(risk.code == "missing_filter" for risk in result.risks)
    assert result.score < 80


def test_analyzer_warns_on_leading_wildcard():
    result = SQLAnalyzer().analyze("SELECT id FROM customers WHERE email LIKE '%@example.com'")

    assert any(risk.code == "leading_wildcard" for risk in result.risks)
    assert any(suggestion.category == "search" for suggestion in result.suggestions)

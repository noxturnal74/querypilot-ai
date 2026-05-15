# API Reference

Base path: `/api`

## Health

`GET /health`

Returns service status and application name.

## Analyze SQL

`POST /analyze`

Request:

```json
{
  "title": "Active customers with recent orders",
  "dialect": "postgresql",
  "query": "SELECT * FROM customers WHERE status = 'active'",
  "schema_context_id": 1,
  "schema_text": "CREATE TABLE customers (...);"
}
```

Use either `schema_context_id` or inline `schema_text`. The response includes:

- performance score
- risk level
- deterministic summary
- AI adapter summary
- optimization suggestions
- risk detections
- index recommendations

## Analysis History

`GET /analyses`

Returns recent analyses for the dashboard.

`GET /analyses/{analysis_id}`

Returns one complete analysis result.

## Schema Context

`POST /schemas`

Stores reusable schema DDL/context.

`GET /schemas`

Lists saved schema contexts.

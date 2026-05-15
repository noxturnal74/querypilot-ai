# QueryPilot AI Architecture

QueryPilot AI is split into a FastAPI backend, a Next.js dashboard, and PostgreSQL persistence.

## Backend

The API owns SQL analysis, risk detection, index recommendations, schema context, history persistence, and the provider-agnostic AI adapter.

Core modules:

- `app.api.routes`: REST endpoints.
- `app.core.config`: environment-driven settings.
- `app.db`: SQLAlchemy session and models.
- `app.services.sql_analyzer`: deterministic SQL analysis engine.
- `app.services.ai`: AI adapter interface and mock implementation.
- `app.seed`: demo data creation.

## Frontend

The web app provides a SaaS-style dashboard for:

- submitting SQL for analysis
- uploading schema/context text
- viewing optimization suggestions
- reviewing risk signals
- browsing historical analyses

## Data Flow

1. User submits SQL and optional schema context from the dashboard.
2. FastAPI validates the request and persists an analysis record.
3. SQL analyzer extracts query traits, risks, optimization opportunities, and index candidates.
4. AI adapter enriches the response in mock mode or via a future provider implementation.
5. Results are returned to the UI and remain available through history endpoints.

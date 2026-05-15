# QueryPilot AI

AI SQL Performance Copilot SaaS for analyzing SQL queries, detecting risk, recommending indexes, and tracking optimization history.

This repository contains a production-oriented MVP monorepo:

- `apps/api`: FastAPI backend with provider-agnostic AI adapter and SQL analysis engine.
- `apps/web`: Next.js, TypeScript, TailwindCSS dashboard.
- `docker-compose.yml`: PostgreSQL, backend API, and frontend web services.
- `docs`: architecture and operating notes.

## Quick Start

```bash
docker compose up --build
```

Open:

- Web: http://localhost:3000
- API docs: http://localhost:8000/docs

## Local Development

Backend:

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

## Tests

Backend:

```bash
cd apps/api
pytest
```

Frontend type check:

```bash
cd apps/web
npm install
npm run test
```

## AI Provider

The backend defaults to mock mode so development and tests do not require a paid AI provider.

Set `AI_PROVIDER=mock` for deterministic responses. Provider-specific adapters can be added behind `app.services.ai.base.AIAdapter`.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Deployment Notes](docs/DEPLOYMENT.md)

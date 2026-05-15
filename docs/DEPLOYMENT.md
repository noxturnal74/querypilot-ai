# Deployment Notes

## Docker Compose

The default deployment path is:

```bash
docker compose up --build
```

Services:

- `postgres`: PostgreSQL 16 with a persistent Docker volume.
- `api`: FastAPI on port `8000`.
- `web`: Next.js on port `3000`.

## Environment

Backend:

- `DATABASE_URL`: SQLAlchemy database URL.
- `AI_PROVIDER`: currently `mock`; future providers should implement the adapter interface.
- `CORS_ORIGINS`: comma-separated allowed browser origins.

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`: public API origin, for example `http://localhost:8000`.

## Production Hardening Checklist

- Move secrets to managed secret storage.
- Use managed PostgreSQL with backups and point-in-time recovery.
- Put API and web behind TLS.
- Add auth, tenant isolation, and rate limits before accepting real customer workloads.
- Replace automatic `create_all` migrations with Alembic migrations before iterative production schema changes.

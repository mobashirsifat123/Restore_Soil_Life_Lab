# Bio Soil Supabase Deployment Checklist

This project now treats Supabase as the production PostgreSQL database for the FastAPI API.
Authentication is handled by the Bio Soil backend itself, not by Supabase Auth.

## 1. Database

Create a Supabase project and use the PostgreSQL session URI, not the transaction pooler.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

Run migrations:

```bash
cd /Users/mobashirsifat/Desktop/bio_lab
pnpm db:migrate
```

## 2. API Environment

Configure [services/api/.env](/Users/mobashirsifat/Desktop/bio_lab/services/api/.env) with:

```env
API_ENV=production
API_DEBUG=false
DEBUG_AUTH_ENABLED=false
AUTH_SESSION_COOKIE_NAME=bio_session
AUTH_SESSION_SECURE_COOKIE=true
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
REDIS_URL=redis://<user>:<password>@<host>:6379/0
ALLOWED_ORIGINS=["https://your-web-domain.com"]
```

Notes:

- `DEBUG_AUTH_ENABLED` must stay `false`.
- `AUTH_SESSION_SECURE_COOKIE` should be `true` in production HTTPS environments.
- Redis is still required for background job publishing and worker execution.

## 3. Web Environment

Configure [apps/web/.env.local](/Users/mobashirsifat/Desktop/bio_lab/apps/web/.env.local) or your hosting provider envs with:

```env
API_BASE_URL=https://api.your-domain.com
```

The Next.js proxy now forwards auth requests directly to the real FastAPI backend.

## 4. Deployment Readiness Checks

Before deploying, verify:

1. Database migrations completed successfully against Supabase.
2. API can reach both Supabase Postgres and Redis.
3. Web can reach the deployed API base URL.
4. CORS origin list matches the real frontend domain.
5. Session cookies are secure in production.

## 5. End-to-End Verification

After deploy, test:

1. Register a new account.
2. Log in and refresh the page.
3. Create a project.
4. Add a soil sample.
5. Create a scenario.
6. Submit a run.
7. Poll run status.
8. Open run results.

## 6. Current Architecture

- Supabase: PostgreSQL database only
- FastAPI: API and session auth
- Next.js: frontend and API proxy
- Redis: run queue transport
- Worker: background execution

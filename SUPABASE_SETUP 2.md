# ============================================================

# Supabase Configuration Guide for Bio Soil API

# ============================================================

#

# STEP 1: Create a Supabase project

# → Go to https://supabase.com → New project

# → Pick a name (e.g. bio-soil-lab), choose a region, set a strong DB password

# → Wait ~2 minutes for it to provision

#

# STEP 2: Get your connection string

# → Project Settings → Database → Connection string

# → Choose "URI" tab

# → Select Mode: "Session" (port 5432) — NOT "Transaction" pooler

# → Copy the URI, it looks like:

# postgresql://postgres.[project-ref]:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

#

# STEP 3: Replace DATABASE_URL in services/api/.env with the Supabase URI

# Change the line:

# DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/bio_lab

# To (psycopg driver prefix is required by SQLAlchemy):

# DATABASE_URL=postgresql+psycopg://postgres.[project-ref]:[your-password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

#

# STEP 4: Run the database migrations to create all tables

# pnpm db:migrate

#

# STEP 5: Restart the API

# cd services/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

#

# ============================================================

# EXAMPLE services/api/.env after Supabase setup:

# ============================================================

#

# DATABASE_URL=postgresql+psycopg://postgres.abcdefghij:MyPassword123@aws-0-us-east-1.pooler.supabase.com:5432/postgres

#

# ============================================================

# IMPORTANT: after migrations run, the proxy mock layer in

# apps/web/src/app/api/bio/[...path]/route.ts can be removed

# and replaced with real API calls once the backend is live.

# ============================================================

# Changelog

## v0.1.0-audit - 2026-04-14

### What works

- Browser auth flows now cover login, registration, forgot password, and reset password.
- The simulation pipeline happy path now runs through a real browser login before project, sample, scenario, and run creation.
- Root `pnpm test` now includes the frontend Playwright suite, backed by an isolated mock API stack for deterministic local verification.
- The backend supports reset-link password recovery with session-cookie auth that behaves correctly on local HTTP and HTTPS.

### Fixed in this baseline

- Aligned frontend auth requests and success/error handling with the backend contract.
- Added a real `/reset-password` page and token-based reset flow.
- Added auth and pipeline Playwright coverage under `apps/web/tests/e2e`.
- Documented required API environment variables in `services/api/.env.example`, including auth, SMTP, database, Redis, and Supabase settings.
- Confirmed `services/api/.env` is not tracked in git history for the current repository state.

### Known incomplete

- Production forgot-password still needs real SMTP credentials and mailbox-level delivery testing.
- CMS/media-related local changes remain in the worktree but are not part of this verified baseline.
- The repo still contains separate in-flight or unknown local changes outside the auth/release-readiness slice; those need their own review before release.

begin;

create table if not exists password_reset_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  code_hash varchar(64) not null,
  user_agent varchar(255),
  ip_address varchar(64),
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists ix_password_reset_tokens_user_id
  on password_reset_tokens (user_id);
create index if not exists ix_password_reset_tokens_expires_at
  on password_reset_tokens (expires_at);
create index if not exists ix_password_reset_tokens_code_hash
  on password_reset_tokens (code_hash);

create table if not exists user_activity_logs (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid references organizations(id) on delete set null,
  user_id uuid references users(id) on delete set null,
  user_email varchar(320),
  activity_type varchar(100) not null,
  activity_label varchar(255) not null,
  details text,
  metadata_json jsonb not null default '{}'::jsonb,
  happened_at timestamptz not null default now()
);

create index if not exists ix_user_activity_logs_org_happened_at
  on user_activity_logs (organization_id, happened_at desc);
create index if not exists ix_user_activity_logs_user_id
  on user_activity_logs (user_id);

commit;

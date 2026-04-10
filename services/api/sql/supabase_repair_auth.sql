begin;

alter table if exists org_memberships rename to organization_memberships;

alter index if exists org_memberships_pkey rename to organization_memberships_pkey;
alter index if exists org_memberships_user_id_organization_id_key rename to uq_organization_memberships_user_org;
alter index if exists ix_org_memberships_org_active rename to ix_organization_memberships_org_active;
alter index if exists ix_org_memberships_user_active rename to ix_organization_memberships_user_active;
alter index if exists ix_org_memberships_organization_id rename to ix_organization_memberships_organization_id;
alter index if exists ix_org_memberships_user_id rename to ix_organization_memberships_user_id;

alter table if exists organization_memberships
  add column if not exists is_default boolean not null default false,
  add column if not exists metadata_json jsonb not null default '{}'::jsonb;

update organization_memberships
set is_default = true
where not exists (
  select 1
  from organization_memberships om2
  where om2.user_id = organization_memberships.user_id
    and om2.is_default = true
);

create index if not exists ix_organization_memberships_organization_id
  on organization_memberships (organization_id);
create index if not exists ix_organization_memberships_user_id
  on organization_memberships (user_id);
create unique index if not exists uq_organization_memberships_user_org
  on organization_memberships (user_id, organization_id);
create index if not exists ix_organization_memberships_org_active
  on organization_memberships (organization_id, is_active);
create index if not exists ix_organization_memberships_user_active
  on organization_memberships (user_id, is_active);

alter table if exists auth_sessions
  add column if not exists metadata_json jsonb not null default '{}'::jsonb,
  add column if not exists updated_at timestamptz not null default now();

create index if not exists ix_auth_sessions_user_id on auth_sessions (user_id);
create index if not exists ix_auth_sessions_organization_id on auth_sessions (organization_id);
create unique index if not exists uq_auth_sessions_token_hash on auth_sessions (token_hash);
create index if not exists ix_auth_sessions_user_active on auth_sessions (user_id, revoked_at);
create index if not exists ix_auth_sessions_org_active on auth_sessions (organization_id, revoked_at);

insert into organization_memberships (
  organization_id,
  user_id,
  role,
  permissions_json,
  is_default,
  is_active,
  metadata_json,
  created_at,
  updated_at
)
select
  u.organization_id,
  u.id,
  'org_admin',
  '["projects:read","projects:write","soil_samples:read","soil_samples:write","scenarios:read","scenarios:write","runs:read","runs:write","reports:read","reports:write"]'::jsonb,
  true,
  true,
  '{}'::jsonb,
  now(),
  now()
from users u
where not exists (
  select 1
  from organization_memberships m
  where m.user_id = u.id
    and m.organization_id = u.organization_id
);

commit;

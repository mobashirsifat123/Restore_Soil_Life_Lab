-- Bio Soil Supabase bootstrap
-- Run this in the Supabase SQL editor against a fresh project database.
-- It creates the full application schema and seeds the CMS/blog/calculator content.

begin;

create extension if not exists pgcrypto;

do $$
begin
  create type project_status as enum ('active', 'archived');
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type scenario_status as enum ('active', 'archived');
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type run_status as enum (
    'draft',
    'queued',
    'running',
    'succeeded',
    'failed',
    'cancel_requested',
    'canceled'
  );
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type artifact_type as enum (
    'result_json',
    'summary_json',
    'csv_export',
    'plot_image',
    'report_pdf',
    'log_bundle',
    'other'
  );
exception
  when duplicate_object then null;
end $$;

create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name varchar(255) not null,
  slug varchar(100) not null,
  description text,
  is_active boolean not null default true,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create unique index if not exists uq_organizations_slug_active
  on organizations (slug)
  where deleted_at is null;

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  email varchar(320) not null,
  full_name varchar(255),
  password_hash varchar(255),
  is_active boolean not null default true,
  last_login_at timestamptz,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create index if not exists ix_users_organization_id on users (organization_id);
create index if not exists ix_users_organization_active on users (organization_id, is_active);
create unique index if not exists uq_users_email_active
  on users (email)
  where deleted_at is null;

create table if not exists organization_memberships (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  role varchar(100) not null default 'org_member',
  permissions_json jsonb not null default '[]'::jsonb,
  is_default boolean not null default false,
  is_active boolean not null default true,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
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

create table if not exists auth_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  organization_id uuid not null references organizations(id) on delete cascade,
  token_hash varchar(64) not null,
  expires_at timestamptz not null,
  last_used_at timestamptz,
  revoked_at timestamptz,
  user_agent varchar(255),
  ip_address varchar(64),
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ix_auth_sessions_user_id on auth_sessions (user_id);
create index if not exists ix_auth_sessions_organization_id on auth_sessions (organization_id);
create unique index if not exists uq_auth_sessions_token_hash on auth_sessions (token_hash);
create index if not exists ix_auth_sessions_user_active on auth_sessions (user_id, revoked_at);
create index if not exists ix_auth_sessions_org_active on auth_sessions (organization_id, revoked_at);

create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  name varchar(255) not null,
  slug varchar(100) not null,
  description text,
  status project_status not null default 'active',
  metadata_json jsonb not null default '{}'::jsonb,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create index if not exists ix_projects_organization_id on projects (organization_id);
create index if not exists ix_projects_created_by_user_id on projects (created_by_user_id);
create unique index if not exists uq_projects_org_slug_active
  on projects (organization_id, slug)
  where deleted_at is null;

create table if not exists soil_samples (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  project_id uuid not null references projects(id) on delete restrict,
  sample_code varchar(100) not null,
  name varchar(255),
  description text,
  collected_on date,
  location_json jsonb not null default '{}'::jsonb,
  measurements_json jsonb not null default '{}'::jsonb,
  metadata_json jsonb not null default '{}'::jsonb,
  current_version integer not null default 1,
  current_version_id uuid,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create index if not exists ix_soil_samples_organization_id on soil_samples (organization_id);
create index if not exists ix_soil_samples_project_id on soil_samples (project_id);
create index if not exists ix_soil_samples_created_by_user_id on soil_samples (created_by_user_id);
create unique index if not exists uq_soil_samples_project_code_active
  on soil_samples (project_id, sample_code)
  where deleted_at is null;

create table if not exists food_web_definitions (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  project_id uuid not null references projects(id) on delete restrict,
  stable_key uuid not null default gen_random_uuid(),
  version integer not null default 1,
  name varchar(255) not null,
  description text,
  nodes_json jsonb not null default '[]'::jsonb,
  links_json jsonb not null default '[]'::jsonb,
  metadata_json jsonb not null default '{}'::jsonb,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ix_food_web_definitions_organization_id
  on food_web_definitions (organization_id);
create index if not exists ix_food_web_definitions_project_id
  on food_web_definitions (project_id);
create index if not exists ix_food_web_definitions_created_by_user_id
  on food_web_definitions (created_by_user_id);
create index if not exists ix_food_web_definitions_stable_key
  on food_web_definitions (stable_key);

create table if not exists parameter_sets (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  project_id uuid not null references projects(id) on delete restrict,
  stable_key uuid not null default gen_random_uuid(),
  version integer not null default 1,
  name varchar(255) not null,
  description text,
  parameters_json jsonb not null default '{}'::jsonb,
  metadata_json jsonb not null default '{}'::jsonb,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ix_parameter_sets_organization_id on parameter_sets (organization_id);
create index if not exists ix_parameter_sets_project_id on parameter_sets (project_id);
create index if not exists ix_parameter_sets_created_by_user_id on parameter_sets (created_by_user_id);
create index if not exists ix_parameter_sets_stable_key on parameter_sets (stable_key);

create table if not exists soil_sample_versions (
  id uuid primary key default gen_random_uuid(),
  soil_sample_id uuid not null references soil_samples(id) on delete cascade,
  organization_id uuid not null references organizations(id) on delete restrict,
  project_id uuid not null references projects(id) on delete restrict,
  version integer not null,
  sample_code varchar(100) not null,
  name varchar(255),
  description text,
  collected_on date,
  location_json jsonb not null default '{}'::jsonb,
  measurements_json jsonb not null default '{}'::jsonb,
  metadata_json jsonb not null default '{}'::jsonb,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now()
);

create index if not exists ix_soil_sample_versions_soil_sample_id on soil_sample_versions (soil_sample_id);
create index if not exists ix_soil_sample_versions_organization_id on soil_sample_versions (organization_id);
create index if not exists ix_soil_sample_versions_project_id on soil_sample_versions (project_id);
create index if not exists ix_soil_sample_versions_org_project
  on soil_sample_versions (organization_id, project_id);
create unique index if not exists uq_soil_sample_versions_sample_version
  on soil_sample_versions (soil_sample_id, version);

create index if not exists ix_soil_samples_current_version_id on soil_samples (current_version_id);

do $$
begin
  alter table soil_samples
    add constraint fk_soil_samples_current_version_id
    foreign key (current_version_id) references soil_sample_versions(id) on delete restrict;
exception
  when duplicate_object then null;
end $$;

create table if not exists simulation_scenarios (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  project_id uuid not null references projects(id) on delete restrict,
  stable_key uuid not null default gen_random_uuid(),
  version integer not null default 1,
  name varchar(255) not null,
  description text,
  status scenario_status not null default 'active',
  soil_sample_id uuid not null references soil_samples(id) on delete restrict,
  soil_sample_version_id uuid not null references soil_sample_versions(id) on delete restrict,
  food_web_definition_id uuid not null references food_web_definitions(id) on delete restrict,
  parameter_set_id uuid not null references parameter_sets(id) on delete restrict,
  scenario_config_json jsonb not null default '{}'::jsonb,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create index if not exists ix_simulation_scenarios_organization_id on simulation_scenarios (organization_id);
create index if not exists ix_simulation_scenarios_project_id on simulation_scenarios (project_id);
create index if not exists ix_simulation_scenarios_soil_sample_id on simulation_scenarios (soil_sample_id);
create index if not exists ix_simulation_scenarios_soil_sample_version_id
  on simulation_scenarios (soil_sample_version_id);
create index if not exists ix_simulation_scenarios_created_by_user_id
  on simulation_scenarios (created_by_user_id);
create index if not exists ix_simulation_scenarios_stable_key on simulation_scenarios (stable_key);

create table if not exists simulation_runs (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  project_id uuid not null references projects(id) on delete restrict,
  scenario_id uuid not null references simulation_scenarios(id) on delete restrict,
  status run_status not null default 'queued',
  engine_name varchar(100) not null,
  engine_version varchar(50) not null,
  input_schema_version varchar(50) not null,
  input_hash varchar(64) not null,
  result_hash varchar(64),
  execution_options_json jsonb not null default '{}'::jsonb,
  input_snapshot_json jsonb not null,
  result_summary_json jsonb,
  queue_name varchar(100) not null,
  idempotency_key varchar(100),
  attempt_count integer not null default 0,
  worker_id varchar(100),
  queued_at timestamptz,
  started_at timestamptz,
  completed_at timestamptz,
  canceled_at timestamptz,
  failure_code varchar(100),
  failure_message text,
  failure_details_json jsonb not null default '{}'::jsonb,
  created_by_user_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ix_simulation_runs_organization_id on simulation_runs (organization_id);
create index if not exists ix_simulation_runs_project_id on simulation_runs (project_id);
create index if not exists ix_simulation_runs_scenario_id on simulation_runs (scenario_id);
create index if not exists ix_simulation_runs_created_by_user_id on simulation_runs (created_by_user_id);
create index if not exists ix_simulation_runs_input_hash on simulation_runs (input_hash);
create index if not exists ix_simulation_runs_org_status on simulation_runs (organization_id, status);
create unique index if not exists uq_simulation_runs_idempotency_active
  on simulation_runs (organization_id, scenario_id, idempotency_key)
  where idempotency_key is not null;

create table if not exists run_artifacts (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  run_id uuid not null references simulation_runs(id) on delete cascade,
  artifact_type artifact_type not null,
  label varchar(255) not null,
  content_type varchar(100) not null,
  storage_key varchar(1024) not null,
  byte_size integer,
  checksum_sha256 varchar(64),
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists ix_run_artifacts_organization_id on run_artifacts (organization_id);
create index if not exists ix_run_artifacts_run on run_artifacts (run_id);

create table if not exists cms_pages (
  id uuid primary key default gen_random_uuid(),
  slug varchar(100) not null,
  title varchar(255) not null,
  meta_description text,
  hero_kicker varchar(255),
  hero_heading text,
  hero_subheading text,
  hero_image_url text,
  updated_at timestamptz not null default now(),
  updated_by_user_id uuid references users(id) on delete set null
);

create unique index if not exists uq_cms_pages_slug on cms_pages (slug);

create table if not exists cms_sections (
  id uuid primary key default gen_random_uuid(),
  page_slug varchar(100) not null,
  section_key varchar(100) not null,
  content_json jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  updated_by_user_id uuid references users(id) on delete set null
);

create unique index if not exists uq_cms_sections_page_key
  on cms_sections (page_slug, section_key);
create index if not exists ix_cms_sections_page_slug on cms_sections (page_slug);

create table if not exists blog_posts (
  id uuid primary key default gen_random_uuid(),
  slug varchar(200) not null,
  category varchar(100) not null,
  title varchar(500) not null,
  excerpt text,
  body_markdown text,
  cover_image_url text,
  author varchar(255),
  published_at timestamptz,
  is_featured boolean not null default false,
  read_time_minutes integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by_user_id uuid references users(id) on delete set null
);

create unique index if not exists uq_blog_posts_slug on blog_posts (slug);
create index if not exists ix_blog_posts_published_at on blog_posts (published_at);
create index if not exists ix_blog_posts_category on blog_posts (category);
create index if not exists ix_blog_posts_is_featured on blog_posts (is_featured);

create table if not exists calculator_formulas (
  id uuid primary key default gen_random_uuid(),
  name varchar(255) not null,
  is_active boolean not null default false,
  formula_json jsonb not null default '{}'::jsonb,
  changelog text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  updated_by_user_id uuid references users(id) on delete set null
);

create index if not exists ix_calculator_formulas_is_active
  on calculator_formulas (is_active);

create table if not exists media_assets (
  id uuid primary key default gen_random_uuid(),
  filename varchar(500) not null,
  url text not null,
  alt_text text,
  mime_type varchar(100),
  byte_size integer,
  uploaded_at timestamptz not null default now(),
  uploaded_by_user_id uuid references users(id) on delete set null
);

create index if not exists ix_media_assets_uploaded_at on media_assets (uploaded_at);

insert into cms_pages (
  slug,
  title,
  meta_description,
  hero_kicker,
  hero_heading,
  hero_subheading,
  hero_image_url
)
values
  (
    'home',
    'Bio Soil — Soil Food Web Science, Education & Tools',
    'Bio Soil brings together soil biology education, a free soil health calculator, and a scientific member platform so farmers, consultants, and ecologists can restore the soil food web.',
    'Soil Food Web Science · Education · Precision Tools',
    'Healthy soil starts with understanding the living community beneath your feet.',
    'Bio Soil brings together soil biology education, a free soil health calculator, and a scientific member platform so farmers, consultants, and ecologists can restore the soil food web and see measurable results.',
    '/images/soil-hero-bg.png'
  ),
  (
    'about',
    'About Bio Soil',
    'Learn how Bio Soil helps communities regenerate living soil through practical soil food web education, diagnostics, and field-ready guidance.',
    'About',
    'Our mission is to help people and organizations regenerate the soils that sustain their communities.',
    'Bio Soil turns soil food web science into clear education, measurable diagnostics, and practical next steps for the people doing the work on the ground.',
    '/images/soil-scientist-hands.png'
  ),
  (
    'science',
    'The Science — Bio Soil',
    'Understand how the soil food web works — nutrient cycling, carbon sequestration, pest suppression — and why restoring it transforms agriculture.',
    'Peer-reviewed science, practical results',
    'How the Soil Food Web Works',
    'Understanding the science behind the soil food web is the foundation of everything we do. Explore the key ecological mechanisms that govern soil health, nutrition, and productivity.',
    null
  ),
  (
    'blog',
    'News, Science & Stories — Bio Soil',
    'Insights from our soil scientists, case studies from the field, and updates from the Bio Soil community around the world.',
    'From the field',
    'News, Science & Stories',
    'Insights from our soil scientists, case studies from the field, and updates from the Bio Soil community around the world.',
    null
  )
on conflict (slug) do update
set
  title = excluded.title,
  meta_description = excluded.meta_description,
  hero_kicker = excluded.hero_kicker,
  hero_heading = excluded.hero_heading,
  hero_subheading = excluded.hero_subheading,
  hero_image_url = excluded.hero_image_url,
  updated_at = now();

insert into cms_sections (page_slug, section_key, content_json)
values
  ('home', 'problems', $json$[
    {"icon":"🌿","title":"Diminishing Soil Fertility","subtitle":"The Soil-ution","body":"With a restored soil food web in place, plants can control nutrient cycling in their root zones, accessing minerals stored in organic matter and parent material. Plants get a constant flow of nutrients they control.","link":"/science/nutrient-cycling"},
    {"icon":"🛡️","title":"Diseases, Pests & Weeds","subtitle":"Problem Solved","body":"The soil food web provides natural protection against pests and diseases and also inhibits the growth of weeds — without chemical intervention.","link":"/science"},
    {"icon":"📈","title":"Declining Farm Profits","subtitle":"How We Help","body":"When the soil food web is restored, farmers no longer need chemicals. Reduced irrigation and plowing requirements also result in significant cost savings.","link":"/science"},
    {"icon":"🌍","title":"Climate Change","subtitle":"Carbon Sequestration","body":"Plants absorb carbon and invest ~40% into the soil to feed microorganisms. By regenerating the world's soils we could halt and reverse climate change within 15–20 years.","link":"/science/carbon-sequestration"},
    {"icon":"🦋","title":"Bird & Insect Decline","subtitle":"Ecosystem Restoration","body":"With the soil food web in place and natural farming practices, pesticides aren't required. The soil food web naturally protects plants, and the entire ecosystem flourishes.","link":"/science"},
    {"icon":"⛰️","title":"Soil Erosion","subtitle":"Structure Formation","body":"Soil food web microorganisms build soil structure that prevents erosion by wind and rain. Compaction layers break up, allowing water and plant roots to penetrate deeper.","link":"/science"}
  ]$json$::jsonb),
  ('home', 'stats', $json$[
    {"number":"150%","label":"Reported yield increase","sub":"In the first growing season"},
    {"number":"100%","label":"Reduction in pest damage","sub":"Using natural food web protection"},
    {"number":"60%","label":"Cut in fertilizer costs","sub":"After soil biology restored"},
    {"number":"6","label":"Continents with proven results","sub":"Farmers transformed worldwide"}
  ]$json$::jsonb),
  ('home', 'testimonials', $json$[
    {"quote":"Our farm was in serious trouble, but after implementing the soil food web approach we increased our yield by 150% in a single season. We also cut fertilizer costs by at least 60%. We continue to monitor and move our soils to a much better place.","author":"Hassan A.","role":"Grain Farmer, Morocco"},
    {"quote":"I'm learning so much I never knew before — even after receiving a degree in Horticulture. Bio Soil explains everything so precisely. I'm excited to start this journey with the soil food web approach!","author":"Meredith L.","role":"Horticulturist, New Zealand"},
    {"quote":"It was one of the greatest courses I have ever taken. The potential of being able to help farmers transition to biology-first agriculture is incredibly exciting.","author":"Thomas B.","role":"Agricultural Consultant, Germany"},
    {"quote":"Great information. It has given me a new outlook for the future of farming. The soil health calculator alone saved me weeks of guesswork.","author":"Sara M.","role":"Regenerative Farmer, Oregon"},
    {"quote":"I've taken many professional certifications throughout my career and I do appreciate this format. Obviously the content is invaluable.","author":"Akira T.","role":"Soil Scientist, Japan"},
    {"quote":"I have greatly appreciated this approach. It has filled in gaps in my knowledge on how to heal depleted soil. Bio Soil's tools make it practical.","author":"Camille R.","role":"Permaculture Designer, France"}
  ]$json$::jsonb),
  ('home', 'calculator_spotlight', $json${"kicker":"New Feature","heading":"SilkSoil","body":"Enter your soil measurements — pH, organic matter, temperature, moisture, microbial indicators — and receive a comprehensive Soil Health Score with actionable recommendations.","features":["Fungal-to-Bacterial ratio analysis","Nutrient availability scoring","Biological activity index","Predictive yield improvement estimate","Personalised restoration roadmap"],"cta_text":"Open SilkSoil — Member Access","cta_link":"/silksoil","image_url":"/images/soil-hero-bg.png"}$json$::jsonb),
  ('home', 'about_section', $json${"kicker":"Our Approach","heading":"The Bio Soil Approach to Soil Regeneration","body1":"The complete soil food web can be found in virgin soils around the world. Once disrupted by chemical inputs, tillage, and monoculture, it must be deliberately and methodically restored.","body2":"Using BioComplete™ soil amendments aligned with the soil food web science, most soils can be regenerated in the first growing season — with measurable, quantifiable results tracked through our analysis platform.","video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","video_image":"/images/soil-microorganism-microscope.png","video_caption":"Soil food web under fluorescence microscopy"}$json$::jsonb),
  ('home', 'photo_feature', $json${"left":{"image":"/images/soil-scientist-hands.png","alt":"Scientist holding healthy soil showing living root and fungi networks","kicker":"In the field","heading":"Living soil you can see and feel","caption":"Healthy soil teems with organisms visible to the naked eye — earthworms, fungi strands, and structured aggregates."},"right":{"image":"/images/healthy-farm-field.png","alt":"Healthy regenerative farm field at golden hour showing thriving crops","kicker":"Results on six continents","heading":"Measurable yield improvements","caption":"Farmers report yield increases of up to 150% in the first season after restoring their soil food web."}}$json$::jsonb),
  ('about', 'founder', $json${"eyebrow":"Our Founder","label":"Dr. Lu Hongyan","name":"A soil scientist devoted to rebuilding living agricultural systems.","image_url":"/images/soil-scientist-hands.png","image_alt":"Scientist holding healthy living soil in both hands","paragraph_one":"For more than two decades, Bio Soil''s scientific leadership has focused on turning complex soil biology into practical guidance that growers, consultants, and communities can actually apply in the field.","paragraph_two":"Our work centers on the living relationships between plants, fungi, bacteria, protozoa, nematodes, and organic matter. When those relationships are restored, degraded land can begin functioning like healthy soil again.","paragraph_three":"Everything we build, from education to diagnostics to software, is designed to help people understand that biology clearly and use it to regenerate the soils that sustain their region.","question_heading":"Have more questions?","question_cta_label":"Connect With Us","question_cta_link":"/contact"}$json$::jsonb),
  ('about', 'founder_credentials', $json$[
    {"text":"B.A., Biology and Chemistry"},
    {"text":"M.S., Microbial Ecology"},
    {"text":"Ph.D., Soil Microbiology"}
  ]$json$::jsonb),
  ('science', 'food_web_levels', $json$[
    {"level":1,"name":"Primary Producers","members":"Plants, Algae","color":"#3a8c2f","description":"Fix energy from sunlight, feed the web with root exudates"},
    {"level":2,"name":"Primary Consumers","members":"Bacteria, Fungi, Root Feeders","color":"#5a7c2f","description":"Break down organic matter, immobilise nutrients"},
    {"level":3,"name":"Secondary Consumers","members":"Protozoa, Nematodes, Microarthropods","color":"#8aaa3a","description":"Eat bacteria and fungi, release nutrients in plant-available forms"},
    {"level":4,"name":"Tertiary Consumers","members":"Predatory Nematodes, Mites, Spiders","color":"#b9933d","description":"Regulate lower trophic levels, prevent population imbalances"},
    {"level":5,"name":"Higher-Order Predators","members":"Earthworms, Centipedes, Beetles","color":"#d4933d","description":"Redistribute organic matter, aerate and structure soil"},
    {"level":6,"name":"Apex Organisms","members":"Mammals, Birds, Reptiles","color":"#b97849","description":"Long-range redistribution of nutrients and biology"}
  ]$json$::jsonb),
  ('science', 'concepts', $json$[
    {"id":"soil-food-web","icon":"🕸️","title":"The Soil Food Web","subtitle":"Nature's Soil Operating System","body":"The soil food web is the interconnected community of organisms living in soil — bacteria, fungi, protozoa, nematodes, arthropods, earthworms, and more. Each plays a specific role in nutrient cycling, soil structure, and plant health. When this web is intact, plants thrive without chemical inputs.","detail":"A single tablespoon of healthy soil contains 1 billion bacteria, 120,000 fungi, and 25,000 protozoa — each essential."},
    {"id":"nutrient-cycling","icon":"♻️","title":"Nutrient Cycling","subtitle":"Plants control their own nutrition","body":"Plants exude sugars through their roots to attract bacteria and fungi. These microbes dissolve and immobilise nutrients. Protozoa and nematodes eat the bacteria and fungi, releasing nutrients directly in the root zone — in the exact form plants need, at the right time. No leaching. No waste.","detail":"Restored nutrient cycling has been linked to yield increases of up to 150% in the first growing season."},
    {"id":"carbon-sequestration","icon":"🌍","title":"Carbon Sequestration","subtitle":"Soil as the climate solution","body":"Plants absorb CO₂ during photosynthesis and invest approximately 40% as root exudates to feed soil microorganisms. These organisms build stable organic compounds — humus and glomalin — that lock carbon into the soil for decades. Scientists estimate that restoring the world's soils could halt and reverse climate change within 15–20 years.","detail":"Biological agriculture can sequester 2–5 tonnes of carbon per hectare per year — far exceeding industrial tree planting."},
    {"id":"suppress-pests-disease","icon":"🛡️","title":"Pest & Disease Suppression","subtitle":"Built-in natural protection","body":"A complete soil food web naturally suppresses pathogens and pests. Fungal networks produce antibiotic compounds. Bacterial films coat root surfaces, blocking pathogen attachment. Predatory nematodes control harmful pest populations. The result: crops grown in biologically active soil have far lower disease and pest pressure — without pesticides.","detail":"Farmers report up to 100% reduction in pesticide use after restoring soil biology."},
    {"id":"weed-suppression","icon":"🌾","title":"Weed Suppression","subtitle":"Biology outcompetes weeds","body":"Weeds are indicators of disturbed or depleted soil. They colonise biological vacuums left by degraded growing conditions. When soil biology is restored, desirable plant communities competitive advantage increases dramatically. Biology — not herbicide — becomes the primary weed management system.","detail":"Cover crop diversity + biological soil management can reduce weed pressure by 60–80%."},
    {"id":"structure-formation","icon":"⛰️","title":"Soil Structure Formation","subtitle":"Building soil from within","body":"Bacteria produce sticky polysaccharides that bind soil particles into aggregates. Fungal hyphae create a physical mesh that reinforces aggregate stability. Earthworms produce castings that dramatically improve water infiltration and aeration. This structured soil resists erosion, holds moisture, and supports deep root penetration.","detail":"Biologically active soil holds 3× more water than compacted or chemically treated soil of the same texture."}
  ]$json$::jsonb),
  ('science', 'stats', $json$[
    {"n":"1B+","label":"Bacteria per teaspoon of soil"},
    {"n":"120,000","label":"Fungal strands per teaspoon"},
    {"n":"40%","label":"Of plant photosynthate invested in soil"},
    {"n":"15–20yr","label":"Timeline to halt climate change via soil"}
  ]$json$::jsonb),
  ('blog', 'categories', $json$["All","Science","Case Studies","Updates","Events","Community"]$json$::jsonb)
on conflict (page_slug, section_key) do update
set content_json = excluded.content_json, updated_at = now();

insert into blog_posts (
  slug,
  category,
  title,
  excerpt,
  body_markdown,
  author,
  published_at,
  is_featured,
  read_time_minutes
)
values
  (
    'mycorrhizal-fungi-nutrient-cycling',
    'Science',
    'How Mycorrhizal Fungi Networks Drive Nutrient Cycling',
    'Underground fungal highways transport nutrients between plants and microorganisms in ways that still astonish soil scientists today.',
    $md$# How Mycorrhizal Fungi Networks Drive Nutrient Cycling

Underground fungal highways transport nutrients between plants and microorganisms in ways that still astonish soil scientists today.

Mycorrhizal fungi form symbiotic relationships with over 90% of land plants. In exchange for carbon-rich sugars from the plant, the fungi extend the plant's effective root system by orders of magnitude, accessing water and nutrients that roots alone could never reach.

## The Wood Wide Web

Recent research has revealed that mycorrhizal networks can connect multiple plants across large distances — creating what some scientists have termed the "Wood Wide Web." Through this network, established trees can support seedlings, nutrients can be transferred between species, and even warning signals about pest attacks can be communicated.

## Nutrient Cycling Mechanism

The fungi physically mine nutrients from soil minerals and organic matter using specialised enzymes. These nutrients are then transported through hyphal networks directly to plant roots — bypassing the need for chemical fertilisers entirely when the system is healthy.

## Key Takeaway

Restoring mycorrhizal networks is one of the most powerful and cost-effective interventions available to regenerative farmers. Avoid tillage, reduce chemical inputs, and establish diverse plant communities to support fungal networks.$md$,
    'Dr. Sarah Greenfield',
    '2026-04-03T00:00:00+00:00',
    true,
    6
  ),
  (
    'pakistani-farm-soil-restored',
    'Case Studies',
    'Pakistani Farm Soil Restored in One Season with Bio Approach',
    'Wild Soils UK and TrashIt demonstrate how the soil food web approach transformed degraded farmland in Pakistan, achieving a 120% yield increase.',
    $md$# Pakistani Farm Soil Restored in One Season

Wild Soils UK and TrashIt demonstrate how the soil food web approach transformed degraded farmland in Pakistan, achieving a 120% yield increase.

## The Challenge

The farm had been under intensive conventional cultivation for 15 years. Soil tests revealed:
- pH: 8.2 (too alkaline)
- Organic matter: 0.8% (severely depleted)
- Microbial activity: near-zero
- Heavy compaction layer at 15cm depth

## The Intervention

Over a single growing season, the team implemented:
1. BioComplete soil amendments
2. Cover crop interplanting
3. Elimination of all synthetic inputs
4. Minimal tillage protocol

## Results After One Season

- Yield increase: 120%
- pH normalised to 6.8
- Organic matter increased to 2.1%
- Significant earthworm return observed
- Pesticide costs: zero

This case demonstrates that dramatic improvements can happen within a single growing season when the biological approach is applied correctly.$md$,
    'Marcus Chen',
    '2026-03-28T00:00:00+00:00',
    true,
    8
  ),
  (
    'silksoil-microbiome-scoring',
    'Updates',
    'SilkSoil: New Microbiome Scoring Module Released',
    'Our latest calculator update adds fungal-to-bacterial ratio scoring and a predictive yield improvement estimate based on 5 years of field data.',
    $md$# SilkSoil: New Microbiome Scoring Module

We're excited to announce a significant update to SilkSoil, our free soil health calculator.

## What's New

### Fungal:Bacterial Ratio Analysis
The new module analyses your estimated F:B ratio and scores it against optimal ranges for different crop types.

### Predictive Yield Estimate
Based on 5 years of field data from 2,400+ farms, the calculator can now estimate potential yield improvement after biological restoration.

### Personalised Roadmap
Every score now comes with a personalised 3-step restoration roadmap tailored to your specific soil profile.

## How to Access

Simply log in to your Bio Soil account and navigate to SilkSoil. The new features are available to all members at no additional cost.$md$,
    'Bio Soil Team',
    '2026-03-20T00:00:00+00:00',
    true,
    4
  ),
  (
    'carbon-sequestration-biological-soil',
    'Science',
    'Carbon Sequestration Through Biological Soil Restoration',
    'New research confirms that restoring the soil food web can sequester carbon at rates that could meaningfully reverse atmospheric CO₂ levels.',
    $md$# Carbon Sequestration Through Biological Soil Restoration

New research confirms that restoring the soil food web can sequester carbon at rates that could meaningfully reverse atmospheric CO₂ levels.

## The Science of Soil Carbon

When the soil food web is intact, plants invest approximately 40% of their photosynthate — the sugars produced from sunlight — into the soil as root exudates. These exudates feed bacteria and fungi, which in turn build complex organic compounds that lock carbon into the soil for decades or even centuries.

## Key Carbon Compounds

- **Humic acids**: Stable carbon compounds that persist in soil for thousands of years
- **Glomalin**: A glycoprotein produced by mycorrhizal fungi that accounts for 15–20% of soil organic carbon
- **Microbial biomass**: Living microorganisms that represent active carbon storage

## Sequestration Rates

Research from our partner labs shows that restored soil food web systems can sequester 2–5 tonnes of carbon per hectare per year — far exceeding the rates achieved by tree planting initiatives.$md$,
    'Dr. Amara Diallo',
    '2026-03-10T00:00:00+00:00',
    false,
    9
  ),
  (
    'soil-food-web-webinar-series',
    'Events',
    'Free Webinar Series: A Living Legacy — The Science of the Soil Food Web',
    'Join us for a 6-part free webinar series exploring the foundational science behind the soil food web approach, from bacteria to food chains.',
    $md$# Free Webinar Series: A Living Legacy

Join us for a 6-part free webinar series exploring the foundational science behind the soil food web approach.

## Series Schedule

1. **Session 1**: The Invisible World — Understanding Soil Bacteria
2. **Session 2**: Fungal Networks — The Wood Wide Web
3. **Session 3**: Protozoa & Nematodes — Nutrient Cycling Engines
4. **Session 4**: Larger Organisms — Earthworms, Arthropods & More
5. **Session 5**: How Plants Control Their Nutrition
6. **Session 6**: Practical Restoration — From Diagnosis to Action

## How to Register

All sessions are free and open to the public. Register via the Events page on our website.$md$,
    'Bio Soil Team',
    '2026-02-28T00:00:00+00:00',
    false,
    3
  ),
  (
    '500-new-consultants-q1-2026',
    'Community',
    'Bio Soil Welcomes 500 New Certified Consultants in Q1 2026',
    'Our community of certified soil consultants grew by 500 members this quarter, now spanning 48 countries on 6 continents.',
    $md$# Bio Soil Welcomes 500 New Certified Consultants

We're thrilled to announce that our global community of certified soil consultants grew by 500 members in Q1 2026.

## Community Milestones

- **Total consultants**: 2,400+
- **Countries represented**: 48
- **Continents**: 6
- **Farms advised in Q1**: 3,200+

## What Certification Means

Our certification programme covers the complete soil food web science, practical diagnosis methods, and use of our SilkSoil platform. Certified consultants are equipped to guide farmers through the full restoration journey.

## Join the Community

Interested in becoming a certified consultant? Our next cohort opens in June 2026.$md$,
    'Bio Soil Team',
    '2026-02-15T00:00:00+00:00',
    false,
    3
  )
on conflict (slug) do update
set
  category = excluded.category,
  title = excluded.title,
  excerpt = excluded.excerpt,
  body_markdown = excluded.body_markdown,
  author = excluded.author,
  published_at = excluded.published_at,
  is_featured = excluded.is_featured,
  read_time_minutes = excluded.read_time_minutes,
  updated_at = now();

insert into calculator_formulas (name, is_active, formula_json, changelog)
select
  'Soil Health Score v1',
  true,
  $json${"version":"1.0","name":"Soil Health Score v1","description":"Weighted composite score from key soil health indicators.","weights":{"ph":{"weight":0.15,"optimal_min":6.0,"optimal_max":7.0,"description":"Soil pH — optimal range 6.0–7.0"},"organic_matter":{"weight":0.20,"optimal_min":3.0,"optimal_max":8.0,"description":"Organic matter % — above 3% is healthy"},"microbial_activity":{"weight":0.25,"optimal_min":60,"optimal_max":100,"description":"Microbial activity index (0–100)"},"fungal_bacterial_ratio":{"weight":0.20,"optimal_min":1.0,"optimal_max":5.0,"description":"Fungal:Bacterial ratio — 1:1 to 5:1 is healthy"},"moisture":{"weight":0.10,"optimal_min":20,"optimal_max":60,"description":"Soil moisture % — 20–60% is ideal"},"temperature":{"weight":0.10,"optimal_min":10,"optimal_max":30,"description":"Soil temperature °C — 10–30°C is active range"}},"score_bands":[{"min":0,"max":39,"label":"Poor","color":"#dc2626","description":"Severely degraded. Immediate biological restoration needed."},{"min":40,"max":59,"label":"Fair","color":"#d97706","description":"Moderately degraded. Targeted interventions recommended."},{"min":60,"max":74,"label":"Good","color":"#ca8a04","description":"Developing biology. Continue restoration programme."},{"min":75,"max":89,"label":"Excellent","color":"#16a34a","description":"Biologically active. Maintain current approach."},{"min":90,"max":100,"label":"Exceptional","color":"#059669","description":"Peak soil food web health. Model farm."}]}$json$::jsonb,
  'Initial formula based on Bio Soil research data.'
where not exists (
  select 1 from calculator_formulas where name = 'Soil Health Score v1'
);

commit;

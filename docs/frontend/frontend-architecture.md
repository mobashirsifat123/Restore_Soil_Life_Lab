# Frontend Architecture

## Goal

Define the frontend structure for a premium scientific SaaS product built with:

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- TanStack Query
- generated TypeScript API client
- one app containing both marketing and authenticated platform surfaces

This architecture should feel like a flagship scientific product, not a generic dashboard template.

## Product Experience Direction

The frontend should communicate:

- scientific credibility
- calm precision
- premium trust
- editorial quality on the marketing surface
- operational clarity on the platform surface

That means:

- expressive typography and careful spacing
- restrained but intentional color system
- data presentation that feels rigorous and legible
- strong separation between storytelling and workflow UI
- fast, clean route transitions with minimal cognitive noise

## Route Architecture

Use App Router route groups to separate public brand pages from authenticated product pages.

## Root Route Structure

```text
src/app/
├── (marketing)/
├── (platform)/
├── login/
├── layout.tsx
├── globals.css
├── not-found.tsx
└── api/
    └── auth/
```

## Marketing Routes

Use `src/app/(marketing)` for public, SEO-first pages.

Initial map:

- `/`
- `/science`
- `/case-studies`
- `/blog`
- `/contact`

Near-term expansion:

- `/about`
- `/approach`
- `/research`
- `/clients`
- `/lead-capture/*`

Rules:

- prefer Server Components by default
- fetch content server-side where possible
- minimize client-side JS
- use metadata exports for SEO
- keep analytics and conversion instrumentation isolated from platform logic

## Platform Routes

Use `src/app/(platform)` for authenticated product workflows.

Initial map:

- `/dashboard`
- `/projects/new`
- `/projects/[projectId]`
- `/projects/[projectId]/samples/new`
- `/projects/[projectId]/scenarios/new`
- `/runs/[runId]`

Near-term expansion:

- `/projects`
- `/projects/[projectId]/samples/[sampleId]`
- `/projects/[projectId]/scenarios/[scenarioId]`
- `/reports/[reportId]`
- `/settings`
- `/admin/*`

Rules:

- platform layout enforces auth boundary
- route-level pages stay thin and delegate UI to feature modules
- all API interaction goes through the generated client plus local query wrappers

## Auth Boundary Placement

### Public Boundary

`(marketing)` routes must remain unauthenticated by default.

### Protected Boundary

`(platform)` layout should:

- load session on the server when possible
- redirect unauthenticated users to `/login`
- hydrate initial session data for client components

### Login Route

`/login` should remain outside route groups so it is explicit and sharable.

### Auth Conventions

- auth resolution belongs in `src/lib/auth`
- route protection belongs in platform layouts, not scattered across leaf pages
- feature modules may still handle permission-based display states

## Feature And Module Architecture

Organize frontend business logic by domain feature, not by technical layer alone.

## `src/features`

Recommended modules:

- `auth`
- `marketing`
- `dashboard`
- `projects`
- `samples`
- `scenarios`
- `runs`
- `results`
- `reports`
- `admin`

Each feature may contain:

- `components/`
- `queries/`
- `mutations/`
- `schemas/`
- `lib/` when feature-specific utilities are needed

Example:

```text
src/features/projects/
├── components/
├── mutations/
├── queries/
└── schemas/
```

### Feature Responsibilities

#### `marketing`

- hero, editorial sections, science storytelling blocks, testimonial/case-study modules

#### `dashboard`

- project summaries, recent runs, quick actions

#### `projects`

- project forms, project header, project summary panels

#### `samples`

- soil sample forms and sample data display

#### `scenarios`

- scenario setup, inline food web editor lite, parameter set editor lite

#### `runs`

- run submission actions, run status, lifecycle polling

#### `results`

- provenance, summary metrics, output panels, artifact links

## Shared UI Architecture

## `src/components`

Use this for non-domain-specific UI building blocks.

Recommended groups:

- `layout`
- `navigation`
- `primitives`
- `feedback`
- `data-display`
- `surfaces`

### `primitives`

Shared low-level UI:

- button
- input
- textarea
- select
- badge
- dialog
- tabs
- skeleton

### `feedback`

- inline error
- empty state
- loading panel
- toast wrapper
- status callout

### `data-display`

- stat row
- key-value list
- table shell
- metric card
- timeline

### `surfaces`

- panel
- card
- section shell
- glass or elevated scientific display containers

## State Management Approach

Use a layered state model.

### Server State

Use TanStack Query for:

- lists from the API
- detail resources from the API
- mutations
- polling run status
- cache invalidation after create/update flows

Rules:

- one query module per feature
- query keys are centralized by feature
- optimistic updates only when behavior is simple and low-risk

### Form State

Keep form state local to the feature form component.

Recommended approach:

- controlled local state for simple forms
- move to a form library only when nested scenario forms become heavy

### URL State

Use URL params for:

- resource identity
- list filters
- sorting
- pagination cursors

Do not keep essential workflow state only in memory if it affects reload behavior.

### App-Wide Client State

Keep global client state minimal.

Allowed examples:

- session context
- active organization context
- UI preferences

Do not use a global client store for API data that belongs in TanStack Query.

## Data Fetching Conventions

## Server Components

Prefer Server Components for:

- marketing pages
- platform shell data that benefits initial render
- route metadata

## Client Components

Use client components for:

- interactive forms
- mutations
- polling
- rich result panels
- local UI transitions

## Generated API Client

Use the generated TypeScript client from `packages/api-client` as the single typed API source.

Rules:

- no raw `fetch` calls in feature code for API resources once codegen exists
- wrap generated methods in feature query/mutation helpers
- do not deep import generated internals

Recommended local API structure:

```text
src/lib/api/
├── client.ts
├── query-client.ts
└── server-client.ts
```

### Query Convention

Each feature should expose:

- query keys
- query options factories
- mutation hooks or wrappers

Example:

```text
src/features/runs/queries/
├── run-keys.ts
├── use-run-status-query.ts
└── use-run-results-query.ts
```

## Design System Direction

## Token Usage

Use `packages/design-tokens` as the source for:

- color scales
- spacing scale
- typography scale
- radii
- shadows
- motion timing

Expose them to the app through:

- Tailwind theme extension
- CSS custom properties in `globals.css`

## UI Package Usage

Use `packages/ui` for:

- stable primitives
- shared layout blocks
- reusable data-display components

Keep platform-specific compositions in `apps/web`.

## Visual Direction

Marketing:

- editorial, cinematic, atmospheric
- strong typography
- layered backgrounds and textures
- generous whitespace

Platform:

- precise and calm
- tighter density
- data-first surfaces
- premium scientific instrumentation feel

Do not make marketing and platform identical, but keep them part of one brand family.

## First Vertical Slice Page Structure

## Pages

### `/login`

Component composition:

- `LoginShell`
- `SessionBootstrapNotice`
- `LoginCard`

### `/projects/new`

Component composition:

- `PlatformPageHeader`
- `ProjectForm`
- `FormActionsBar`

### `/projects/[projectId]`

Component composition:

- `ProjectHeader`
- `ProjectSummaryPanel`
- `RecentSamplesPanel`
- `RecentScenariosPanel`
- `RecentRunsPanel`
- `QuickActionsPanel`

### `/projects/[projectId]/samples/new`

Component composition:

- `PlatformPageHeader`
- `SoilSampleForm`
- `JsonFieldEditor` or `KeyValueEditor`

### `/projects/[projectId]/scenarios/new`

Component composition:

- `PlatformPageHeader`
- `ScenarioForm`
- `FoodWebEditorLite`
- `ParameterSetEditorLite`
- `ScenarioConfigPanel`

### `/runs/[runId]`

Component composition:

- `RunPageHeader`
- `RunStatusBadge`
- `RunTimeline`
- `RunProvenancePanel`
- `RunSummaryPanel`
- `ModuleResultsGrid`
- `ArtifactList`

## Loading, Error, And Empty State Strategy

## Loading States

Use:

- page-level skeletons for route transitions
- form button pending states for mutations
- section skeletons for sub-panels
- status pulse for live run processing

Do not block the whole page for a small mutation when local pending UI is enough.

## Error States

Separate:

- form validation errors
- recoverable network errors
- authorization errors
- terminal job failures

Patterns:

- inline field errors for form issues
- callout panel for section-level failures
- dedicated failure panel on run page for terminal failed state

## Empty States

Use editorial empty states for premium feel.

Examples:

- no projects yet
- no samples in a project
- no scenarios yet
- no runs yet

Each empty state should:

- explain the next action
- provide a primary CTA
- avoid looking like a generic blank dashboard

## Testing Strategy

## Unit Tests

Test:

- feature hooks
- query key generation
- form serialization helpers
- result formatting utilities

## Component Tests

Test:

- forms
- run status displays
- result panels
- empty and error state rendering

## Integration Tests

Test:

- page-level flows with mocked generated client
- auth boundary redirects
- mutation success and error behavior

## End-To-End Tests

Critical slice:

1. session bootstrap
2. create project
3. add soil sample
4. create scenario
5. submit run
6. poll until complete
7. verify results page

Marketing smoke tests:

- home page renders
- metadata and title are present
- main CTA works

## Starter `apps/web` Folder Structure

```text
apps/web/
├── public/
└── src/
    ├── app/
    │   ├── (marketing)/
    │   │   ├── blog/
    │   │   ├── case-studies/
    │   │   ├── contact/
    │   │   ├── science/
    │   │   ├── layout.tsx
    │   │   └── page.tsx
    │   ├── (platform)/
    │   │   ├── dashboard/
    │   │   ├── projects/
    │   │   │   ├── new/
    │   │   │   └── [projectId]/
    │   │   │       ├── page.tsx
    │   │   │       ├── samples/
    │   │   │       │   └── new/
    │   │   │       └── scenarios/
    │   │   │           └── new/
    │   │   ├── runs/
    │   │   │   └── [runId]/
    │   │   └── layout.tsx
    │   ├── login/
    │   ├── api/
    │   │   └── auth/
    │   ├── globals.css
    │   ├── layout.tsx
    │   └── not-found.tsx
    ├── components/
    │   ├── data-display/
    │   ├── feedback/
    │   ├── layout/
    │   ├── navigation/
    │   ├── primitives/
    │   └── surfaces/
    ├── content/
    │   └── marketing/
    ├── features/
    │   ├── admin/
    │   ├── auth/
    │   │   ├── components/
    │   │   ├── hooks/
    │   │   └── lib/
    │   ├── dashboard/
    │   │   ├── components/
    │   │   └── queries/
    │   ├── marketing/
    │   │   ├── components/
    │   │   └── sections/
    │   ├── projects/
    │   │   ├── components/
    │   │   ├── mutations/
    │   │   ├── queries/
    │   │   └── schemas/
    │   ├── results/
    │   │   ├── components/
    │   │   └── queries/
    │   ├── runs/
    │   │   ├── components/
    │   │   ├── mutations/
    │   │   ├── queries/
    │   │   └── schemas/
    │   ├── samples/
    │   │   ├── components/
    │   │   ├── mutations/
    │   │   ├── queries/
    │   │   └── schemas/
    │   └── scenarios/
    │       ├── components/
    │       ├── mutations/
    │       ├── queries/
    │       └── schemas/
    ├── hooks/
    ├── lib/
    │   ├── analytics/
    │   ├── api/
    │   ├── auth/
    │   ├── config/
    │   ├── observability/
    │   └── utils/
    ├── providers/
    ├── styles/
    ├── tests/
    │   ├── e2e/
    │   ├── fixtures/
    │   └── integration/
    └── types/
```

## Conventions

1. Route files compose feature modules; they should not own heavy business logic.
2. Marketing and platform layouts must stay separate even if they share primitives.
3. API data belongs in TanStack Query, not ad hoc local state.
4. Feature modules own API wrappers, mutation logic, and domain UI.
5. Shared components stay domain-agnostic.
6. Server Components first for marketing; client components where interactivity or polling is required.
7. Use generated API types everywhere instead of hand-maintained duplicates.
8. Do not let platform styling collapse into generic SaaS defaults.

## Recommended Next Build Steps

1. scaffold root app layouts and `AppProviders`
2. wire the generated API client and QueryClient
3. build the platform auth boundary
4. implement `ProjectForm`, `SoilSampleForm`, and `ScenarioForm`
5. implement the run detail page with polling and result panels
6. build the marketing home page shell using the same token system

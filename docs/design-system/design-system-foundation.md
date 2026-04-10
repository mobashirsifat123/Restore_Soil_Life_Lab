# Design System Foundation

## Goal

Create the design-system foundation for a premium scientific platform that serves both:

- public editorial marketing pages
- authenticated analytical workflows

The system should communicate trust, rigor, and clarity without looking sterile or generic.

## Design Principles

### 1. Scientific Confidence

The interface should feel evidence-based, stable, and precise.

Design implications:

- disciplined spacing
- strong typographic hierarchy
- numerical alignment
- restrained accent usage
- low-noise layouts

### 2. Editorial Depth

Marketing pages should feel like a premium research publication, not a startup landing page template.

Design implications:

- serif display voice for long-form storytelling
- layered sections and atmospheric backgrounds
- careful pacing between dense and open sections

### 3. Instrument-Like Product UX

The platform side should feel like a modern scientific instrument panel.

Design implications:

- calm surfaces
- explicit status communication
- data-forward layouts
- cards that read like analysis modules rather than generic widgets

### 4. One Brand, Two Modes

Marketing and platform should be visually related but not identical.

Marketing mode:

- richer imagery
- stronger contrast between headline and body
- more atmospheric surfaces

Platform mode:

- tighter density
- clearer data grouping
- more neutral canvas

### 5. High Signal Over Decoration

Visual richness is welcome, but it must reinforce comprehension.

Avoid:

- decorative gradients that obscure content
- noisy shadows
- gratuitous animation
- gimmicky glassmorphism

## Visual Language For Scientific Credibility

The platform should evoke:

- geological materials
- lab instrumentation
- field research notes
- premium editorial publishing

Core visual cues:

- deep mineral inks instead of pure black
- warm paper neutrals instead of flat white
- measured copper and moss accents instead of neon highlights
- serif editorial headlines paired with disciplined sans-serif UI text
- monospaced numerics for run IDs, hashes, timings, and metrics
- thin dividing lines and subtle grid structures

## Token Recommendations

## Color System

Build from a small, distinctive palette:

- `ink`: primary deep text and structural tone
- `mineral`: cool neutral for UI surfaces and data framing
- `sage`: scientific/biological accent
- `sand`: warm editorial neutral
- `copper`: premium emphasis and action accent
- `signal`: functional status tones

Color rules:

- most UI should live in ink, mineral, and sand
- sage is a secondary accent
- copper is sparing and intentional
- signal colors should be muted, not neon

Recommended semantic roles:

- canvas
- panel
- elevated panel
- subtle border
- strong border
- text primary
- text muted
- accent primary
- accent secondary
- success
- warning
- danger
- info

## Spacing System

Use a 4px base scale, but bias layouts toward 8/12/16/24/32 rhythm.

Recommended tokens:

- `0`, `1`, `2`, `3`, `4`, `5`, `6`, `8`, `10`, `12`, `16`, `20`, `24`, `32`

Use:

- compact density for tables and analytical workflows
- looser spacing for marketing and long-form reading

## Typography System

Use three voices:

- editorial serif for marketing and key hero moments
- disciplined sans for UI and application copy
- mono for metrics, hashes, and technical metadata

Recommended families:

- editorial: `Newsreader`
- ui sans: `Instrument Sans`
- mono: `IBM Plex Mono`

Type roles:

- display
- hero
- h1
- h2
- h3
- title
- body
- body-small
- label
- caption
- numeric

## Radius

Keep radius refined, not playful.

Recommended tokens:

- `sm: 6px`
- `md: 10px`
- `lg: 14px`
- `xl: 18px`
- `pill: 999px`

Rule:

Prefer `md` and `lg`. Avoid very round components for analytical UI.

## Elevation

Use subtle, cool-toned shadows and border layering.

Recommended levels:

- `flat`
- `raised`
- `floating`
- `dialog`

Rule:

Elevation should imply information hierarchy, not “card spam.”

## Motion

Motion should feel calm and purposeful.

Recommended durations:

- `fast: 140ms`
- `base: 220ms`
- `slow: 320ms`

Recommended easing:

- `standard`
- `emphasized`
- `decelerated`

Use motion for:

- page reveal
- panel transition
- async status change
- modal entry

Do not use springy or playful motion in core analytical workflows.

## What Belongs In `packages/design-tokens`

Put only reusable, non-React design primitives here:

- primitive color scales
- semantic color roles
- typography scales and font stacks
- spacing tokens
- radius tokens
- elevation tokens
- motion tokens
- Tailwind theme extension objects
- CSS variable maps

This package should not contain:

- React components
- app-specific layout code
- business-specific styling logic

## What Belongs In `packages/ui`

Put reusable React UI building blocks here:

- primitives
- surfaces
- feedback components
- data-display primitives
- layout shells
- navigation primitives

This package should not contain:

- API calls
- TanStack Query hooks
- route logic
- feature/business domain logic
- product-specific orchestration

## Component Categories To Build First

## Primitives

- `Button`
- `Input`
- `Textarea`
- `Select`
- `Checkbox`
- `Radio`
- `Badge`
- `Tabs`
- `Dialog`
- `Tooltip`
- `Skeleton`

## Surfaces

- `Panel`
- `Card`
- `SectionShell`
- `MetricSurface`
- `InsetSurface`

## Feedback

- `InlineError`
- `StatusCallout`
- `EmptyState`
- `LoadingPanel`
- `ToastViewport`

## Data Display

- `KeyValueList`
- `MetricCard`
- `StatusBadge`
- `Timeline`
- `TableShell`
- `ResultCard`
- `ArtifactListRow`

## Layout And Navigation

- `AppShell`
- `TopNav`
- `SidebarNav`
- `PageHeader`
- `SectionHeader`
- `ContentContainer`

## MVP Component List

Build in this order:

1. `Button`
2. `Input`
3. `Textarea`
4. `Select`
5. `Panel`
6. `Card`
7. `PageHeader`
8. `StatusBadge`
9. `LoadingPanel`
10. `InlineError`
11. `EmptyState`
12. `MetricCard`
13. `KeyValueList`
14. `TableShell`
15. `ResultCard`
16. `Timeline`

## Page Layout Patterns

## Marketing Home

Structure:

- atmospheric hero
- science credibility band
- product capability grid
- case study teaser
- lead capture band

Pattern rules:

- alternate dense editorial sections with breathing-room sections
- keep CTA count low
- use typography and layout before decorative UI chrome

## Editorial Content Page

Structure:

- narrow reading column
- side metadata rail optional
- pull quotes and callouts
- embedded visual modules

Use for:

- science pages
- case studies
- blog

## Platform Workspace Page

Structure:

- page header
- action row
- primary content column
- secondary context rail optional

Use for:

- dashboard
- project detail
- run detail

## Create/Edit Form Page

Structure:

- header
- multi-section form
- persistent action bar

Form sections should feel like:

- scientific record entry
- not like a generic admin form

## Results Page

Structure:

- run status and provenance header
- summary metrics row
- module result grid
- artifacts section
- diagnostics section if needed

## Table, Chart, Form, And Result-Card Patterns

## Tables

Tables should be:

- numerically aligned
- scannable
- low-contrast but sharp
- compact without becoming cramped

Rules:

- use monospaced numerics for measurements and durations
- keep row separators subtle
- emphasize selected or anomalous rows with tone, not bright color
- avoid striped rows unless density truly requires it

## Charts

Charts should feel scientific, not decorative.

Rules:

- clear axes and units
- restrained palette
- annotation-friendly
- consistent legend behavior
- avoid gratuitous gradients, 3D, or glossy treatments

Preferred chart frame:

- chart inside `Panel`
- header with title, subtitle, and controls
- footer with notes or provenance when needed

## Forms

Forms should communicate trust and precision.

Rules:

- group fields into named sections
- explain why inputs matter
- place validation close to the field
- allow structured text or JSON for scientific inputs in MVP
- keep labels explicit and unambiguous

## Result Cards

Result cards should look like analysis modules.

Structure:

- module title
- short descriptor
- key numeric outcome
- supporting metrics
- optional provenance footer

Use cases:

- flux summary
- mineralization summary
- stability metrics
- decomposition constant
- run provenance

## Starter Token Structure

Recommended package structure:

```text
packages/design-tokens/
└── src/
    ├── colors.ts
    ├── spacing.ts
    ├── typography.ts
    ├── radius.ts
    ├── elevation.ts
    ├── motion.ts
    ├── semantic.ts
    ├── tailwind-theme.ts
    └── index.ts
```

Recommended UI package structure:

```text
packages/ui/
└── src/
    ├── primitives/
    ├── feedback/
    ├── data-display/
    ├── layout/
    ├── navigation/
    ├── surfaces/
    ├── component-roadmap.ts
    └── index.ts
```

## Styling Conventions

1. Use token-backed Tailwind theme values instead of ad hoc hex colors.
2. Prefer semantic token usage over raw palette values in app components.
3. Use serif display type selectively, not everywhere.
4. Use mono only for numeric or technical contexts.
5. Favor borders and tone shifts before heavy shadows.
6. Use whitespace as a primary luxury signal.
7. Reserve accent colors for action, state, and emphasis.

## Premium UI Rules

1. Every page should have a clear focal hierarchy within the first screen.
2. Every analytical surface should make the data easier to read than a raw table.
3. Every loading state should feel intentional, not like a blank wait.
4. Every empty state should teach the next action.
5. Every results view should expose provenance and status, not just numbers.

## Don’t Do This

Avoid these anti-patterns:

- generic blue-purple SaaS gradients
- over-rounded cards and pills everywhere
- dashboard pages made entirely of identical KPI tiles
- loud shadows and heavy blur
- neon status colors
- bouncy micro-interactions
- dense forms without sectioning
- tables with poor numeric alignment
- charts without units or legends
- burying scientific provenance beneath decorative UI

## Recommended Next Steps

1. wire `packages/design-tokens` into Tailwind theme extension
2. build `packages/ui` primitives and surfaces in MVP priority order
3. create marketing and platform layout shells that share tokens but not page composition
4. implement result-card and table patterns before ornamental marketing sections

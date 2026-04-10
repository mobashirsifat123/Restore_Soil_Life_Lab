# UI Package

`@bio/ui` contains reusable React components built on top of the design tokens.

It should contain:

- low-level primitives
- reusable surfaces
- feedback components
- data-display primitives
- layout and navigation building blocks

It should not contain:

- API clients
- TanStack Query hooks
- route logic
- feature-specific business logic

Build order should follow `src/component-roadmap.ts`.

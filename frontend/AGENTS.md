# KuyLab frontend

React, TypeScript, Vite and MUI. The project follows the module structure of the
user's Deenly frontend; its interface remains KuyLab's Ivory-inspired design.

```text
src/
  app/                 layouts, providers, routes, theme, styles
  shared/              api, i18n, lib, offline, routing, ui
  modules/<feature>/
    application/       providers, queries, mutations, controllers
    domain/            entities, contracts, pure policies
    data-access/       dto, mappers, repository, platform adapters
    ui/                pages/<PageName>, shared
    index.ts
```

- Flow: UI -> application hooks -> domain contract -> injected repository ->
  shared API client. UI and application code do not call HTTP or import adapters.
- Keep domain entities and policies independent of React, browser globals and
  transport code. DTO normalization belongs in data-access mappers.
- Import other modules through their public entry, application or domain barrel.
  Only app routes may lazy-load a `ui/pages/<PageName>/index.ts` entry. Do not
  deep-import another module's page implementation or repository.
- Keep barrels small. Pages orchestrate routing and feature components. Shared
  code is domain-agnostic; feature-specific UI stays within its module.
- Use query and mutation files for related application hooks. Introduce query
  cache keys only when the feature actually uses a query cache.
- Preserve curated content, existing lesson stage IDs, saved positions and
  five-minute activity accounting. Content editing is managed outside the UI.
- Playback runs continuously to the end. Do not reintroduce automatic looping,
  selected repeat ranges, repeat delays or a repeat keyboard shortcut.
- Keep UZ/RU/EN complete, both themes readable, local fonts and sample credits
  intact, and loading/error states available for every asynchronous route.
- Run commands from this directory: `npm run check:architecture`,
  `npm run typecheck`, `npm test`, `npm run lint`, and `npm run build`.
- The lint command checks architecture and formatting; it is not an ESLint scan.


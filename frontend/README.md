# KuyLab frontend

The personal piano studio uses React, TypeScript, Vite and MUI. Deenly's feature
module structure is the architecture reference. Ivory provides the visual
reference; no Deenly template components or licensed Minimal assets are copied.

## Development

USB MIDI input is shared across the signed-in studio, including composition and
lesson players, the free piano, and visible keyboard challenges. Use **Connect
piano** in the header or **Settings > MIDI** in a player. Access is requested only
after a click, without SysEx; only the selected input is opened. MIDI output is
never sent to the instrument. Unplugging, changing inputs, hiding the tab or
signing out clears held notes and pedal sound.

The default sound source is the instrument itself. **KuyLab Grand** uses the
browser sample bank with input velocity and CC64 sustain. Disable Local Control
on the instrument when choosing browser sound to prevent doubled audio. Sound
source, master volume and reverb use the same account preferences as all players.
MIDI input does not pause composition playback. In keyboard challenges, single
notes and chords accumulate until cleared; key release and repeated pitches do
not erase the selection. Checking and progress updates still require **Check**.

Test the adapter/controller without hardware with `npm test`. Physical acceptance
on Yamaha YDP-145 / Windows / USB covers permission, selected input, repeated
notes with pedal held, unplug/replug, and audible latency. Web MIDI requires HTTPS
(localhost is allowed); Chrome/Edge on Windows is the target setup.

Run the Django API on `127.0.0.1:8000`. In this directory:

```powershell
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to Django. A production preview
uses `npm run build` followed by `npm run preview` on port 4173.

## Structure

```text
src/
  app/
    layouts/studio/                header, sidebar and application shell
    providers/                     application composition
    routes/                        lazy page routing and error boundary
    theme/                         MUI theme
    styles/                        global styles and bundled fonts
  shared/
    api/                           HTTP transport
    i18n/                          UZ, RU and EN
    lib/                           generic storage helpers
    offline/                       cached catalog and score support
    routing/                       route parsing and navigation
    ui/                            reusable domain-independent UI
  modules/<feature>/
    application/                   providers, query/mutation hooks, controllers
    domain/
      entities/                    application types
      contracts/                   repository and platform ports
      *.logic.ts                   pure rules and transformations
    data-access/
      dto/                         API response and payload shapes
      mappers/                     transport normalization
      repository/                  API and local-storage implementations
      adapters/                    audio/MIDI adapters in the practice module
    ui/
      pages/<PageName>/             page component and route entry
      shared/                      reusable UI within that feature
    index.ts                       module public API
```

UI calls application hooks. Hooks depend on domain contracts. The module or app
composition injects data-access repositories, which call `shared/api`. DTOs and
API field normalization remain in data-access. Parsed MIDI uses the canonical
score model; musical timing rules remain pure domain functions.

The architecture checker resolves TypeScript imports, including aliases and lazy
imports. Cross-feature imports use public barrels. Only app routes can import a
page's `index.ts`; feature modules cannot reach its implementation. Domain code
cannot depend on React or browser services, and UI/application cannot call HTTP.

The catalog is curated and read-only. Each Still lesson has three independent
MIDI stages. Main playback remains separate from lesson explanations. Player
preferences and playback positions persist independently; playback stops at the
end and the timeline is used for seeking.

On narrow screens the keyboard initially shows a readable portion of all 88
keys. Wheel input or a horizontal drag pans the keys and falling notes together;
two-finger pinch changes the visible range. The Display settings slider selects
12–88 visible keys and persists across players for the current account. Canvas
resolution stays bounded by the viewport rather than the zoomed keyboard width.
Mobile transport uses a compact speed popover and a secondary actions menu;
settings open as a bottom sheet.

The prerendered landing page uses local musical SVG patterns, a pausable preview
animation and progressive section reveals. Public content stays visible without
JavaScript or IntersectionObserver, and reduced-motion preferences disable
decorative movement. No React runtime is needed for public pages.

Offline content caching remains available after content has loaded. The UI does
not display an offline-ready badge. The production service worker and local piano
sample bank remain part of the build.

## Verification

```powershell
npm run check:architecture
npm run typecheck
npm test
npm run lint
npm run build
```

`lint` checks module boundaries and Prettier formatting. `lint:architecture` is
retained as an alias for existing workflows. Tests use Node's TypeScript stripping
support and cover transport timing, preferences, offline behavior, repository
mapping, lesson stage selection, navigation and activity accounting.

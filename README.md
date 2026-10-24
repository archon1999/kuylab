# KuyLab

A composition-first piano learning studio built with Django, React, TypeScript and
MUI. Learn with a falling-note MIDI player, separately authored composition
lessons, general exercises and music theory. Interface languages: Uzbek, Russian
and English; light and dark themes.

Each account has its own favorites, playback positions, learning progress,
preferences and activity statistics. The musical catalog is curated in code;
users do not upload or edit shared content through the website.

## Structure

- `backend/apps`: learning, scores, studio and activity domains.
- `backend/config/settings`: local SQLite, test SQLite/PostgreSQL, production PostgreSQL.
- `frontend/src/app`: routes, layouts, providers and theme.
- `frontend/src/modules`: domain, application, data-access and UI layers.
- `frontend/src/shared`: transport, localization, UI and playback helpers.
- `frontend/public-site`: prerendered UZ/RU/EN public pages and educational guides.
- `ops`: production deployment, backup and Nginx configuration.

## Local development

Python 3.12, Poetry 2.3.2 and Node 24 LTS are used by CI. SQLite is the local default.

```sh
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py seed_studio
poetry run python manage.py runserver 127.0.0.1:8000
```

In a second terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173 for the public site, then `/studio` to create an account.
No default production password or
administrator is shipped. `seed_studio` preserves existing learner state; the
explicit destructive replacement flag is not part of normal setup or deployment.

## Verification

```sh
cd backend
poetry run python manage.py test tests --settings=config.settings.test --noinput
```

```sh
cd frontend
npm run typecheck
npm test
npm run lint
npm run build
```

CI repeats backend tests against PostgreSQL, checks migrations and production
security settings, builds both Docker images, and runs CodeQL. Successful main
commits deploy through a dedicated restricted SSH identity.

## Production

See [deployment and recovery](docs/deployment.md) for Docker, PostgreSQL, Nginx,
DNS/TLS, backup and rollback procedures. Secrets, databases, media and learner
records stay outside Git. Production is configured for `kuylab.uz`.

## Content and attribution

Public pages are generated at build time, including canonical/hreflang links,
Open Graph images, visible educational content and matching JSON-LD. `/robots.txt`
and `/sitemap.xml` list the public site; authenticated studio routes send `noindex`.
Existing composition/player links and legacy query-string bookmarks remain valid.
The service worker keeps public HTML separate from `/studio.html` so visiting a
public guide cannot replace the offline studio shell. No analytics tracker runs
on the public site. `llms.txt` is a content directory, not an indexing guarantee.

When changing public content, edit all three languages in
`frontend/public-site/content.mjs`, update its actual review date, and rebuild.
Google Search Console uses DNS ownership verification; retain its root TXT record.
Submit `https://kuylab.uz/sitemap.xml` and inspect public URLs after deployment.
Check PageSpeed on mobile and desktop; lab scores are separate from field data.

The current curriculum uses the supplied Winter Sonata — Still MIDI, with separate
teaching adaptations; general exercises are original examples. Source bytes and
provenance are documented in [the studio notes](backend/apps/studio/README.md).
Composition files and historical reference fixtures do not carry a blanket
open-source redistribution license. Review their provenance before republishing
musical content. Public repository visibility does not change third-party rights.

Piano samples, fonts, MUI and audio worklet notices are in
[third-party notices](frontend/THIRD_PARTY_NOTICES.md) and the app's `/licenses.html`.

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

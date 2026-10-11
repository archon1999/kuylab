# KuyLab backend

Django runs from this directory. The repository follows the Deenly layout:

```text
apps/
  studio/          curated catalog, authored MIDI, lesson content and services
  activity/        library state, visits, serializers and services
  scores/          MIDI parsing, stored scores and read endpoints
  learning/        learner profile and retained historical domain models
config/
  settings/
    base.py        shared configuration
    local.py       loopback development
    test.py        isolated test configuration
tests/             tests grouped by domain
db.sqlite3         existing learner data (ignored by Git)
media/             original and authored score files (ignored by Git)
```

Views adapt HTTP requests; the active studio and activity business operations
live in `services.py`. Activity validation lives in `serializers.py`. Existing
app labels and database table names stay `studio`, `activity`, `scores`, and
`learning`, so moving Python packages does not recreate learner data.

## Development

Python 3.12 or 3.13 and Poetry 2:

```powershell
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver 127.0.0.1:8000
```

The frontend starts separately with `npm run dev` in `frontend/`. Its Vite proxy
uses port 8000. `config.settings.local` is the default. This is a personal local
studio; musical content is read-only through HTTP. Environment variables can
override `SQLITE_PATH`, `MEDIA_ROOT`, `DJANGO_SECRET_KEY`, and `DJANGO_DEBUG`.

Only a new, empty database needs `poetry run python manage.py seed_studio`.
Seeding is an authoring operation; do not run it as part of ordinary startup.
The original MIDI is at `apps/studio/assets/still.mid`.

## Verification

```powershell
poetry check
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run python manage.py test tests --settings=config.settings.test --noinput
poetry run python ../ops/verify_workspace.py
```

Historical authoring API tests explicitly opt out of the curated middleware
inside their test classes. Studio tests keep the current read-only mode enabled
and verify that retired routes cannot write. Local configuration never disables
that protection.

Backups and diagnostics live in root `runtime/` and are excluded from Git.
The migration snapshot and media manifest are under `runtime/backups/`.

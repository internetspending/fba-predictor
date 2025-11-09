### Summary

* Prefer `weight_kg`; support legacy `weight` with **one** structured deprecation warning only when consumed
* FeeBreakdown serialization now uses `asdict()` → JSON-safe primitives
* ETL scan orchestration verified in Docker; idempotent re-run confirmed

### Changes

* `apps/api/app/workers/pipeline.py`

  * `_parse_decimal` guard for `InvalidOperation`
  * `warn_deprecated_weight()` structured logger
  * `build_dimensions()` helper: prefers `weight_kg`, falls back to legacy `weight`
  * `serialize_fee_breakdown()` dataclass → plain `dict` for JSON
* Tests

  * `tests/test_dimensions_compat.py` (preferred `weight_kg`, legacy fallback + warning, mixed fields)
  * `tests/test_fee_breakdown_serialization.py` (round-trip JSON using `asdict()`)
* Docs

  * `docs/milestones/M5_CHECKLIST.md` (checked)
  * `docs/milestones/M5_VERIFICATION.md` (commands + expected logs)
  * `docs/KNOWN_DEPRECATIONS.md` (documented `weight` → `weight_kg`) and README link

### How to Test

```bash
# rebuild + up
docker compose -f deploy/docker/compose.yml down --remove-orphans
docker compose -f deploy/docker/compose.yml build
docker compose -f deploy/docker/compose.yml up -d

# migrations
docker compose -f deploy/docker/compose.yml exec api alembic upgrade head

# ETL run + idempotent re-run
docker compose -f deploy/docker/compose.yml exec api python - <<'PY'
import asyncio, logging
from apps.api.app.persistence.db import get_session_local
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import run_scan
logging.basicConfig(level=logging.INFO)
async def main():
    session_factory = get_session_local()
    async with session_factory() as session:
        scan = Scan(); session.add(scan); await session.commit(); await session.refresh(scan)
        counts = await run_scan(scan.id); print("ETL counts:", counts.model_dump())
        counts2 = await run_scan(scan.id); print("Re-run counts:", counts2.model_dump())
asyncio.run(main())
PY

# Deprecation warning (legacy weight consumed)
docker compose -f deploy/docker/compose.yml exec api python - <<'PY'
import logging
from apps.api.app.workers.pipeline import build_dimensions
logging.basicConfig(level=logging.WARNING)
build_dimensions({"length_cm":"10","width_cm":"5","height_cm":"2","weight":"0.5"})
PY

# Local tests (new suites)
pytest tests/test_dimensions_compat.py tests/test_fee_breakdown_serialization.py -q
```

### Expected Logs

* Deprecation (once):
  `{"event":"deprecated_weight_field","action":"use_weight_kg","source":"Dimensions","level":"warning"}`
* ETL: schedule → extract → complete; second run shows zero deltas

### Known Non-blocking CI

* Pre-existing async fixture / `httpx.AsyncClient` test issues; tracked in the repo (link the tracking issue in a review comment). Not introduced by this PR.

### Rollback

* Revert PR; no destructive migrations added

### Background Tasks

* All background scan tests/orchestration runs completed; none need to remain open. Safe to close legacy background test issues after merge.

### Checklist

* [x] Dimensions: prefer `weight_kg`; legacy fallback emits one warning when consumed
* [x] FeeBreakdown uses `asdict()` and round-trips JSON
* [x] Docker + Alembic verified
* [x] ETL logs verified; idempotent re-run confirmed
* [x] New regression tests added and passing locally
* [x] Non-blocking CI failures acknowledged + linked in review thread
* [x] Verification notes included (`docs/milestones/M5_VERIFICATION.md`)

# Milestone 5 Verification

**Migrations**
```
docker compose -f deploy/docker/compose.yml exec api alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

**ETL run**
```
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
        scan_id = scan.id
        logging.info("Created scan %s", scan_id)
    counts = await run_scan(scan_id)
    logging.info("Run counts %s", counts.model_dump())
    counts2 = await run_scan(scan_id)
    logging.info("Re-run counts %s", counts2.model_dump())
asyncio.run(main())
PY
INFO:verification:Created scan c2517db5-7ffe-4b6e-a07a-1cb5c6915c85
INFO:apps.api.app.workers.pipeline:SCAN c2517db5-7ffe-4b6e-a07a-1cb5c6915c85 ETL extracted=2 transformed=2 loaded=2 skipped=0 errors=0 scan_duration_ms=1
INFO:verification:Run counts {'extracted': 2, 'transformed': 2, 'loaded': 2, 'skipped': 0, 'errors': 0}
INFO:apps.api.app.workers.pipeline:Skip: scan c2517db5-7ffe-4b6e-a07a-1cb5c6915c85 already done
INFO:verification:Re-run counts {'extracted': 0, 'transformed': 0, 'loaded': 0, 'skipped': 0, 'errors': 0}
```

**Deprecation log**
```
docker compose -f deploy/docker/compose.yml exec api python - <<'PY'
import logging
from apps.api.app.workers.pipeline import build_dimensions
logging.basicConfig(level=logging.WARNING)
build_dimensions({"length_cm":"10","width_cm":"5","height_cm":"2","weight":"0.5"})
PY
WARNING:apps.api.app.workers.pipeline:{"event":"deprecated_weight_field","action":"use_weight_kg","source":"Dimensions","level":"warning"}
```

**Tests**
```
pytest tests/test_dimensions_compat.py tests/test_fee_breakdown_serialization.py -q
============================== 7 passed in 0.01s ===============================
```

**How to reproduce**
- `docker compose -f deploy/docker/compose.yml up -d`
- Run the ETL block above, then the deprecation log snippet
- `pytest tests/test_dimensions_compat.py tests/test_fee_breakdown_serialization.py -q`

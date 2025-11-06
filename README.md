# FBA Predictor

SaaS tool to forecast product ROI and automate Amazon FBA profitability analysis using FastAPI and PostgreSQL.

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/internetspending/fba-predictor.git
   cd fba-predictor
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Keepa API key
   ```

3. **Start the development stack:**
   ```bash
   docker compose -f deploy/docker/compose.yml up --build
   ```

4. **Verify the setup:**
   ```bash
   curl http://localhost:8000/v1/health
   # Expected: {"status":"ok"}
   ```

## Development Workflow

### Running the Stack

```bash
# Start all services
docker compose -f deploy/docker/compose.yml up

# Start in background
docker compose -f deploy/docker/compose.yml up -d

# View logs
docker compose -f deploy/docker/compose.yml logs -f

# Stop services
docker compose -f deploy/docker/compose.yml down
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose -f deploy/docker/compose.yml exec db psql -U fba_user -d fba_predictor

# Connect to Redis
docker compose -f deploy/docker/compose.yml exec redis redis-cli
```

### Code Quality

```bash
# Install pre-commit hooks
pre-commit install

# Run linting and formatting
ruff check .
ruff format .

# Run type checking
mypy apps/api/app

# Run tests
pytest
```

## Architecture

- **API**: FastAPI application with hot reload
- **Database**: PostgreSQL 16 with health checks
- **Cache**: Redis 7 for session and data caching
- **Development**: Docker Compose for local development

## API Endpoints

- `GET /v1/health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `KEEPA_API_KEY` - Keepa API key for Amazon data
- `APP_ENV` - Application environment (development/production)
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level (info/debug/error)

## Project Structure

```
fba-predictor/
├── apps/
│   └── api/
│       └── app/
│           ├── api/          # API endpoints
│           ├── core/         # Configuration and logging
│           ├── domain/       # Business logic
│           ├── integrations/ # External services
│           ├── models/       # Data schemas
│           ├── persistence/  # Database layer
│           └── workers/      # Background tasks
├── deploy/
│   └── docker/              # Docker configuration
└── requirements.txt         # Python dependencies
```

## Milestone 3 (Integrations) — Local dev

### Quick Start for M3

- Mock Keepa in tests; no real network calls in CI
- Optional: run Redis locally (`docker compose -f deploy/docker/compose.yml up redis`)
- Run tests: `pytest -m "m2 or m3" -q`

### M3 Features

- **Keepa Integration**: Client with retry/backoff, caching, and normalization
- **SellerAmp Parsers**: CSV and JSON storefront export parsing
- **Snapshot Storage**: Raw Keepa payloads persisted to database

### Testing M3

All M3 tests are marked with `@pytest.mark.m3` and mock external services:

```bash
# Run only M3 tests
pytest -m m3

# Run M2 + M3 tests
pytest -m "m2 or m3"
```

## Milestone 4 (Fees & Rules Engine) — Local dev

### Quick Start for M4

- All currency math uses `Decimal`
- Run tests: `pytest -m "m2 or m3 or m4" -q`

### M4 Features

- **Fee Calculation**: Referral, FBA, and optional placement fees
- **Size Tier Estimation**: Standard vs. oversize logic
- **ROI/Net Profit**: Comprehensive breakdown calculation
- **Rules Engine**: Predicates for ROI, profit, BSR, sellers, brand allow/block, hazmat
- **Explainer**: Human-readable reasons for rule pass/fail

### Testing M4

All M4 tests are marked with `@pytest.mark.m4` and use `Decimal` for assertions:

```bash
# Run only M4 tests
pytest -m m4

# Run M2 + M3 + M4 tests
pytest -m "m2 or m3 or m4"
```

## Milestone 5 (Scan Pipeline) — Local dev

### Quick Start for M5

- ETL pipeline processes SellerAmp data with fee calculation and rule evaluation
- Background tasks run scans asynchronously
- Status tracking: `pending → running → done/failed`
- Run tests: `pytest -m "m2 or m3 or m4 or m5" -q`

### M5 Features

- **ETL Pipeline**: Extract, Transform, Load workflow for batch scans
- **Status Tracking**: Database-backed scan status with timestamps
- **Background Processing**: FastAPI BackgroundTasks for async execution
- **Rate Limiting**: Configurable concurrency via `SCAN_MAX_CONCURRENCY` env var
- **Retry Logic**: Exponential backoff on transient errors
- **ETL Logging**: Summary log line with extracted/transformed/loaded/skipped/errors counts

### Running Scans

1. **Create a scan:**
   ```bash
   curl -X POST http://localhost:8000/v1/dev/create-scan
   # Returns: {"scan_id": "uuid", "status": "pending"}
   ```

2. **Trigger scan processing:**
   ```bash
   curl -X POST http://localhost:8000/v1/dev/run-scan/{scan_id}
   # Returns: {"status": "enqueued", "scan_id": "uuid"}
   ```

3. **Check scan status:**
   ```bash
   curl http://localhost:8000/v1/dev/scan/{scan_id}
   # Returns scan status, timestamps, and error (if any)
   ```

4. **Watch logs for ETL summary:**
   ```bash
   docker compose -f deploy/docker/compose.yml logs -f api
   # Look for: "SCAN {scan_id} ETL extracted=... transformed=... loaded=... skipped=... errors=..."
   ```

### Environment Variables

- `SCAN_MAX_CONCURRENCY` - Maximum concurrent item processing (default: 10, minimum: 1)
  - If missing or ≤0, defaults to 10
  - Only mounts `/v1/dev/*` endpoints in non-production environments

### Input Data Format

**Dimensions (for fee calculation):**
- Preferred: `dimensions.weight_kg` (weight in kilograms)
- Legacy supported: `dimensions.weight` (assumed kilograms, deprecated)
- Note: If both `weight_kg` and `weight` are present, `weight_kg` takes precedence

### Policies

- **Idempotency**: Re-running a completed scan (status `done` or `failed`) is a no-op. The pipeline checks scan status before processing and returns zero counts if the scan is not `pending`.
- **Partial Success**: The pipeline continues processing even if individual items fail. Failed items are counted in `errors`, but successful items are still saved. Partial results are persisted.
- **Retry Logic**: Only transient errors (network timeouts, connection errors, I/O errors) are retried with exponential backoff. Non-transient errors (validation, data errors) fail immediately without retry.

### Testing M5

All M5 tests are marked with `@pytest.mark.m5`:

```bash
# Run only M5 tests
pytest -m m5

# Run M2 + M3 + M4 + M5 tests
pytest -m "m2 or m3 or m4 or m5"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

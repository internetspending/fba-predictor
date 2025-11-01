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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

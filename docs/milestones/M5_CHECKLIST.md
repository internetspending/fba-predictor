# Milestone 5 Finalization Checklist

- [x] Dimensions: accept `weight_kg` and legacy `weight` inputs; normalize downstream.
- [x] Emit deprecation warning when legacy `weight` is seen (single, structured log line).
- [x] FeeBreakdown serialization: use `asdict()`; ensure JSON-safe types.
- [x] Scan orchestration: dry-run and full run succeed in Docker (no regressions).
- [x] ETL logs: verify scheduling + extraction messages appear as expected.
- [x] Add tests for: (a) legacy weight path + warning, (b) `weight_kg` path, (c) FeeBreakdown serialization.
- [x] Note known flaky CI issues as non-blocking (link to the existing tracking issue).
- [ ] PR description includes “What changed / How to test / Known issues / Rollback plan”.

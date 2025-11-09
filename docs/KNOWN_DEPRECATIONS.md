# Known Deprecations

## weight → weight_kg

- **Deprecated**: `dimensions.weight`
- **Use instead**: `dimensions.weight_kg`
- **Behavior**: when only `weight` is present, the pipeline consumes it and emits a structured warning once per payload:
  `{"event":"deprecated_weight_field","action":"use_weight_kg","source":"Dimensions","level":"warning"}`
- **Timeline**: warning in Milestone 5; removal planned in a future milestone once downstream data sources migrate.

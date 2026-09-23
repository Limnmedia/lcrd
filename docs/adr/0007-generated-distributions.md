# 0007 — Generated distributions

## Context

Consumers should not depend on the repository's internal directories or
migration implementation.

## Decision

`data/` is canonical authored knowledge. `tools/` validates and builds
distributions. `dist/lcrd.json` is relational and provenance-rich,
`dist/lcrd.min.json` is compact lookup data, and `dist/lcrd.csv` is a lossy
flat convenience export. Consumers use `dist/`, not `data/` or `Research/`.

## Why

This creates a clear release boundary and lets internal storage evolve without
breaking an external consumer.

## Consequences

Generated files must not be hand-edited. A canonical change requires a
validation/build cycle and a review of the generated diff.

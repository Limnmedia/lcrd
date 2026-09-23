# LCRD — LIMN Camera Reference Database

LCRD is a machine-readable, provenance-aware reference database for cameras,
imaging devices, physical camera modules, sensors, lenses, and observed camera
metadata. It is designed for software that needs to understand what imaging
hardware produced an image, what physical geometry that hardware uses, and
where that information came from.

LIMNTPS is one consumer, not LCRD's defining scope. The repository is
currently an **unreleased research snapshot** prepared for public review.

## What is included

The `Research/` directory contains:

- `lcrd_camera_reference_v0_1_FREEZE.csv` — the frozen v0.1 reference set,
  containing 656 records across dedicated cameras and mobile camera modules.
- Sensor-dimension research passes covering DragonFrame-supported cameras and
  selected mobile-device families.
- A cutoff/audit pass used to document coverage and follow-up work.
- `LCRD_V0_1_FREEZE_NOTES.md` and `LCRD_V0_1_FREEZE_MANIFEST.json`, which
  describe the freeze scope and provide integrity metadata.
- `LIMNTPS_LCRD_EXIF_CODEX_HANDOFF.md`, the integration handoff for the
  LIMNTPS consumer.

The canonical public data is under `data/`. JSON Schema contracts are under
`schema/`; generated consumer files are under `dist/`. The original research
CSVs remain under `Research/` as an auditable migration source and are not the
consumer-facing database format.

## Data principles

LCRD separates:

- canonical camera or device identity;
- observed or imported metadata;
- physical sensor geometry;
- geometry evidence and provenance;
- identity-match confidence; and
- the actual pixel raster used by an imported image.

The physical sensor dimensions in LCRD must not be confused with the native
or maximum pixel raster of a camera. A downstream TPS workflow should combine
the resolved physical geometry with the dimensions of the specific imported
image.

Evidence tier `E` records are structural or unresolved and must not provide
automatic calculation geometry. Tiers `A`, `B`, and `C` retain their
individual provenance even when a downstream consumer permits automatic use.

## Validate and build

The only runtime requirement is Python 3.10 or newer:

```text
python tools/lcrd.py migrate
python tools/lcrd.py validate
python tools/lcrd.py build
```

`migrate` is used when the preserved research inputs change. `validate` checks
stable IDs, relationships, observations, sources, and sensor dimensions.
`build` produces `dist/lcrd.json`, `dist/lcrd.min.json`, and `dist/lcrd.csv`.
Generated JSON uses `lcrdVersion` `0.1.0` and `schemaVersion` `1.0.0`.

See [`docs/CONSUMING_LCRD.md`](docs/CONSUMING_LCRD.md) for general consumer
examples and [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) for the entity model.

## CSV conventions

CSV files use UTF-8, one header row, and one record per line. Numeric geometry
fields are expressed in millimeters. `record_id` is the stable row identifier
within a dataset version. The freeze schema is documented by its header and
by the field descriptions in the freeze notes.

## Status and licensing

The `Research/` directory is ready for public review, but the repository still
needs a project-level license decision before it should be presented as a
reusable public data product. No license is asserted by this repository yet;
see [`SECURITY.md`](SECURITY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) for
project guidance while that decision is pending.

## Related project

LIMNTPS is the first intended consumer of the frozen reference data. The
integration handoff is included for context, but this repository does not
contain LIMNTPS application code or change its calculation model.

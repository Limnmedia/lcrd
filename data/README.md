# Canonical data

This directory is the authored source of LCRD's public database. Edit records
here when making a canonical data change; do not edit `dist/` directly.

Collections are split by entity type: cameras, devices, physical camera
modules, sensors, lenses, observations, and sources. An observation preserves
what a source or research pass recorded. A reference entity is the normalized
identity that consumers use. See [`../docs/DATA_MODEL.md`](../docs/DATA_MODEL.md)
and [`../docs/PROVENANCE.md`](../docs/PROVENANCE.md) before changing a record.

After editing, run the validation and build commands in the repository
README, inspect the generated diff, and include the source/provenance reason
for the change.

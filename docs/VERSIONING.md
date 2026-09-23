# Versioning

LCRD has two version dimensions:

- `lcrdVersion` identifies a data release (`0.1.0` for this initialization);
- `schemaVersion` identifies the public structural contract (`1.0.0` for the
  initial contract).

Adding or correcting observations normally changes the dataset version, not
the schema version. A schema version changes when consumers must adapt to a
structural contract change. The project is pre-1.0 and may make incompatible
changes with explicit release notes.

Generated distributions include both values, `generatedAt`, and
`sourceCommit`. Set `LCRD_GENERATED_AT` and `LCRD_SOURCE_COMMIT` when producing
a reproducible release artifact.

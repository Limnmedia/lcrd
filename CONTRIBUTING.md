# Contributing to LCRD

LCRD contributions should be atomic. A contributor may add one observation,
one source, one alias, a corrected dimension, or a new entity without filling
in unrelated fields.

## Contribution licensing

By contributing material that you have the right to contribute, you submit it
under the applicable LCRD license: database and data contributions under CC BY
4.0, software and tooling contributions under Apache-2.0, and documentation
contributions under CC BY 4.0. Contributors retain whatever rights they retain
under those licenses; this project does not require a copyright transfer, CLA,
or DCO.

Do not submit copyrighted manufacturer images, proprietary documents, sample
media, or other material that you do not have the right to redistribute.
Facts and properly attributed observations are the intended contribution model.

## Required provenance

Every factual addition needs a source or an explicit statement that it is a
direct measurement or observation. Preserve the raw value, the source URL or
file reference when available, the method, and the confidence. Estimates must
remain labeled as estimates; do not upgrade them to verified data during a
cleanup.

Observed EXIF values must be copied exactly as observed. A normalized value or
alias belongs beside the observation, not in place of it.

## IDs and data changes

Read [`docs/IDENTIFIERS.md`](docs/IDENTIFIERS.md) before assigning an ID.
Stable IDs are never reused for a different physical entity. Generated files
under `dist/` are not hand-edited.

When changing the canonical data:

```text
python tools/lcrd.py validate
python tools/lcrd.py build
```

Include the validation result and explain any changed provenance or coverage.

## Acceptable sources

Prefer manufacturer specifications, primary technical documentation, direct
measurements, and source files whose metadata can be inspected. Secondary
sources are acceptable when clearly labeled. Do not commit copyrighted sample
photographs, RAW files, or videos merely to support an EXIF observation.

## Pull requests

Describe what changed, why the source supports it, whether the value is
observed or derived, and how validation was run. Corrections are welcome even
when they reduce certainty.

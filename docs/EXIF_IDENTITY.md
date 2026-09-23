# EXIF identity observations

Raw metadata is an observation layer, not a rewrite of canonical identity.
Relevant fields may include EXIF Make, EXIF Model, UniqueCameraModel,
CameraModelName, LensMake, LensModel, Software, and manufacturer-specific
identifiers.

When a source file is available, preserve the exact observed value and retain
the source file reference, URL, hash, and access date where permitted. A
manufacturer model identifier or gallery label is not automatically an
observed EXIF value.

Consumers may match in stages:

```text
raw exact → normalized exact → manufacturer identifier → explicit alias → candidate
```

LCRD distributes observations and identifiers; it does not become a fuzzy
matching service or rewrite the raw observation.

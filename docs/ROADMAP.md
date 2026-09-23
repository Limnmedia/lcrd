# LCRD post-release roadmap

## Initialization is complete

LCRD is no longer a database that needs to be “completed.” The initialization
phase is complete. LCRD v0.1.0 is maintained reference infrastructure with
canonical data, stable IDs, provenance/evidence semantics, public schemas,
generated distributions, validation/build tooling, tests, licensing, a public
consumer contract, and human-reviewability documentation.

Future work should be incremental and evidence-driven: new evidence,
corrections, new imaging hardware, real consumer requirements, provenance
improvements, and empirical metadata observations. Do not expand the dataset
speculatively merely because more data or architecture could be added.

The governing principle remains:

> Preserve observations. Derive interpretations.

LCRD owns reference facts, identity, physical geometry, observations, sources,
provenance, evidence, aliases, manufacturer identifiers, and empirical
metadata observations. Consumer-specific calculations and workflows remain in
consuming applications. TPS concepts belong in LIMNTPS, not LCRD.

## Next focused data sprint — Empirical EXIF Corpus Pass 001

This is planned work, not work started by this document. The first empirical
corpus should collect metadata extracted from actual camera-generated files,
including where present:

```text
Make, Model, UniqueCameraModel, CameraModelName,
LensMake, LensModel, Software, ImageWidth, ImageHeight
```

Each observation should retain its source URL/type, sample filename, sample
SHA-256, metadata extractor and version, and observation date. Do not store
copyrighted photographs or RAW/JPEG samples merely to preserve metadata;
extract the required fields and preserve provenance instead.

Favor variation over maximum camera count. An initial target of approximately
40 representative files should span ecosystems such as Canon, Nikon, Sony,
Fujifilm, Panasonic, OM System/Olympus, Blackmagic, RED, Apple/iPhone, Google
Pixel, and Samsung Galaxy. The goal is to learn how real metadata behaves,
not to collect every camera immediately.

Keep these identities distinct:

```text
manufacturer identifier ≠ known alias ≠ observed EXIF value
```

For example, a manufacturer relationship between Sony α7 IV and `ILCE-7M4`
does not prove that an image file contains `Model=ILCE-7M4`. That claim
requires an actual extracted camera-generated file. Do not fabricate EXIF
observations from names, identifiers, or marketing material.

## Ongoing maintenance

Existing C-tier geometry is not automatically technical debt or a release
blocker. A good, explicitly labeled estimate is preferable to fabricated
certainty. Evidence may improve opportunistically:

```text
C — good reference / labeled estimate
        ↓
B — strong derived evidence
        ↓
A — verified/direct evidence
```

Do not launch another broad sensor-dimension sweep merely to increase A-tier
counts. Normal incremental contributions include new cameras, phones, modules,
corrected dimensions, improved sensor identity, aliases, better sources,
provenance corrections, empirical EXIF observations, and reported identity
resolution failures.

Consumer reports should drive public-contract improvements. Ask:

> Would camera-reference software generally need this information?

If yes, consider adding it to LCRD. If it exists only for one application's
workflow, keep it in that application.

## LCRD and LIMNTPS boundary

LCRD provides:

```text
camera/device identity
physical camera modules
sensor identity and physical geometry
observations and sources
provenance and evidence
manufacturer identifiers and aliases
empirical metadata observations
```

LIMNTPS provides:

```text
TPS A/B/C points
Sacred Triangle / STCARD workflow
focus-distance workflow
HOT SET and Stage Line-Up state
TPS focal calculation and readiness
camera recovery and TPS package workflow/UI state
```

The relationship remains:

```text
LIMNTPS / TPS → consumes LCRD as an external reference dependency
```

The immediate LIMNMEDIA development focus returns to LIMNTPS/TPS. LCRD is not
an unfinished prerequisite.

## Deferred domains and intentional limits

Lenses are a legitimate future LCRD domain, but not the next population
project. The current `0 lenses` state is acceptable. Empirical `LensMake` and
`LensModel` observations may eventually provide an evidence-driven starting
point; do not attempt to populate the world's lens catalog now.

Mobile module identity remains ongoing research. Preserve:

```text
device → physical camera module → sensor
```

Do not collapse a multi-camera phone into one sensor or silently assume the
main camera when metadata cannot resolve the physical module. Preserve the
ambiguity for the consumer to handle.

Explicitly not required now:

- exhaustive camera coverage or phone history;
- an exhaustive lens catalog;
- upgrading every record to A-tier;
- a cloud API or live hardware discovery;
- TPS workflow logic in LCRD;
- a large EXIF corpus before LIMNTPS development continues.

## Versioning direction

Version numbers describe compatibility and public-contract evolution, not
database size. New cameras, observations, sources, aliases, or corrected
evidence do not automatically require a new architecture release and may fit
compatible `v0.1.x` updates. A future `v0.2.0` should be motivated by a
meaningful change to the public schema, relationships, contract, or
consumer-facing semantics. Do not create `v0.2.0` for routine maintenance.

Conceptually:

```text
LCRD v0.1
   │
   ├── Empirical EXIF Corpus Pass 001
   ├── LIMNTPS field feedback
   ├── evidence/source strengthening
   ├── corrections
   ├── new cameras/devices/modules
   └── evidence-driven lens observations
              │
              ↓
      compatible v0.1.x updates

Public-contract evolution
              │
              ↓
           v0.2.0
```

This is a direction, not a release calendar.

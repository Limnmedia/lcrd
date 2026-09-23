# LIMNTPS --- LCRD v0.1 + EXIF Camera Identity Integration Handoff

## Purpose

Integrate the frozen LCRD v0.1 camera-reference data into LIMNTPS and
use imported-image metadata to automatically resolve the most likely
camera and physical sensor geometry.

This is now an implementation task, not an open-ended camera-data
research task.

The data architecture and matching approach are approved and should be
treated as the current product direction.

------------------------------------------------------------------------

## Product Goal

For the normal user workflow:

1.  Import an image.
2.  LIMNTPS reads available EXIF/file metadata.
3.  LIMNTPS identifies the camera automatically when confidence is
    sufficient.
4.  LIMNTPS obtains physical sensor dimensions from LCRD.
5.  The imported image's actual pixel dimensions become the effective
    working raster for that capture.
6.  TPS continues without requiring the user to research sensor
    dimensions.

The desired normal UX is approximately:

> Camera recognized: Sony α7 IV\
> Sensor: 35.9 × 23.9 mm

The user should not normally need to understand EXIF model identifiers,
LCRD evidence tiers, optical formats, or database internals.

If identity is genuinely ambiguous, ask for the minimum necessary
confirmation.

------------------------------------------------------------------------

# 1. Governing Data Principle

LCRD follows:

> **Preserve observations. Derive interpretations.**

Do not rewrite canonical camera names to imitate EXIF strings.

Keep these concepts separate:

-   canonical camera/device identity
-   observed EXIF identity strings
-   manufacturer identifiers
-   aliases
-   sensor geometry
-   sensor-geometry provenance
-   identity-match confidence
-   imported-image raster
-   TPS-derived focal information

An EXIF identity match and the confidence in sensor geometry are
different things.

Example:

``` text
identity:
    canonical: Sony α7 IV
    rawExifMake: SONY
    rawExifModel: ILCE-7M4
    matchMethod: manufacturerIdentifier
    matchConfidence: high

sensorGeometry:
    widthMm: 35.9
    heightMm: 23.9
    evidenceTier: A
```

Do not collapse those into one confidence value.

------------------------------------------------------------------------

# 2. Frozen LCRD v0.1 Dataset

Use the frozen v0.1 dataset supplied with this handoff:

-   `lcrd_camera_reference_v0_1_FREEZE.csv`
-   `LCRD_V0_1_FREEZE_NOTES.md`
-   `LCRD_V0_1_FREEZE_MANIFEST.json`

The freeze contains 656 records.

Current evidence distribution:

-   A: 23
-   B: 30
-   C: 602
-   E: 1 structural/non-calculating record

There are 650 calculable records and no release-blocking QA records in
the freeze.

The remaining source-strengthening backlog is database maintenance and
does not block LIMNTPS integration.

## Evidence semantics

### A --- Verified

Strong direct evidence for physical geometry.

May be used automatically.

### B --- Strong derived

Physical geometry derived from strong observations, such as active
raster × documented pixel pitch.

May be used automatically.

### C --- Good working reference / estimate

A defensible geometry suitable for TPS use, but not necessarily directly
manufacturer-published physical dimensions.

May be used automatically.

Its estimated/reference provenance must remain preserved.

### E --- Structural/unresolved

Must not provide automatic geometry.

Example: generic RED DSMC2 is a platform parent. A sensor-specific DSMC2
child must be selected.

------------------------------------------------------------------------

# 3. Critical TPS Geometry Rule

LCRD provides the **physical sensor geometry in millimeters**.

The imported image provides the **effective pixel raster for that
particular capture**.

Do not assume the camera's advertised/native maximum sensor raster is
the raster used by the imported image.

For TPS use:

``` text
physical sensor/active-area dimensions in mm
+
actual imported image width × height in pixels
```

The imported image dimensions may differ from the native sensor raster
because of:

-   crop modes
-   aspect-ratio modes
-   output resolution
-   JPEG/RAW configuration
-   camera processing
-   phone camera modes

The imported file is workflow authority for the captured raster.

TPS calculates its working focal length from TPS observations. EXIF
focal length can be retained as an observation and sanity check, but
must not replace the TPS focal calculation.

------------------------------------------------------------------------

# 4. EXIF Identity Architecture Is Locked

Do not massage LCRD's canonical camera names until they resemble EXIF.

Instead use a dedicated identity resolver.

Conceptual architecture:

``` text
ImportedImage
      ↓
ImportedImageMetadata
      ↓
CameraIdentityResolver
      ↓
CameraIdentityMatch
      ↓
LcrdRepository
      ↓
ResolvedSensorGeometry
      ↓
TPS
```

Keep this service isolated from TPS mathematics and from UI widgets.

------------------------------------------------------------------------

# 5. EXIF Observation Model

LCRD may eventually contain observations conceptually similar to:

``` yaml
canonical:
  manufacturer: Sony
  model: α7 IV

identifiers:
  - ILCE-7M4

observed_exif:
  make:
    - SONY
  model:
    - ILCE-7M4
```

Do not claim something is an `observed_exif` value unless it was
actually extracted from a camera-generated/source file.

A manufacturer model identifier is useful identity evidence but is not
automatically an observed EXIF value.

A manufacturer sample-gallery label is also not automatically an
observed EXIF value.

Preserve those distinctions.

------------------------------------------------------------------------

# 6. Camera Identity Resolution Pipeline

Implement deterministic matching before fuzzy matching.

## Stage 1 --- Raw exact observation

If raw EXIF Make/Model matches a known observed identity, resolve
automatically.

Example:

``` text
Make: SONY
Model: ILCE-7M4
```

If LCRD has that observation associated with Sony α7 IV, this is
effectively deterministic.

## Stage 2 --- Manufacturer identifier

Match documented manufacturer model identifiers.

Example:

``` text
canonical: Sony α7 IV
identifier: ILCE-7M4
```

This is strong enough for automatic resolution when manufacturer context
agrees.

## Stage 3 --- Normalized exact match

Normalize strings for comparison without modifying the raw metadata.

Reasonable normalization includes:

-   trim leading/trailing whitespace
-   collapse repeated whitespace
-   case-fold
-   Unicode normalization
-   normalize obvious punctuation/separators
-   normalize `α` / `Alpha` where useful
-   remove a duplicated manufacturer prefix from Model when Make already
    establishes manufacturer

Example:

``` text
Make: Canon
Model: Canon EOS R5
```

may normalize against:

``` text
manufacturer: Canon
model: EOS R5
```

Do not aggressively remove meaningful tokens.

Preserve distinctions such as:

-   R5 vs R5 C
-   Mark II vs Mark III
-   II / III / IV / V
-   Pro
-   Plus
-   Ultra
-   Max
-   regional/hardware suffixes when meaningful

A false-positive camera identity is worse than asking for confirmation.

## Stage 4 --- Explicit alias match

Resolve documented aliases automatically.

Examples include regional naming:

``` text
EOS 100D
Rebel SL1
Kiss X7
```

when LCRD establishes that they refer to the same physical camera.

## Stage 5 --- Strong manufacturer-constrained model guess

If there is no deterministic observation/alias match, constrain
candidates by manufacturer first.

Then compare meaningful model tokens.

For example:

``` text
Make: NIKON CORPORATION
Model: NIKON Z 8
```

should be compared primarily against Nikon records, not the entire LCRD
catalog.

If there is exactly one strong, non-conflicting model candidate, LIMNTPS
may treat it as a high-confidence model guess.

The system should be comfortable making a reasonable guess when the
evidence is strong.

Do not require confirmation merely because punctuation or branding
differs.

## Stage 6 --- Fuzzy candidate

Generic fuzzy string similarity is discovery assistance, not automatic
optical authority.

If similarity produces multiple plausible cameras, return candidates
rather than silently selecting sensor geometry.

## Stage 7 --- User confirmation

When there is meaningful ambiguity, present a simple confirmation:

> This looks like a Canon EOS R6 Mark II.

Allow:

-   Confirm
-   Choose another camera

Use the friendly canonical LCRD name in normal UI.

Raw EXIF strings belong in details/debug/advanced information.

## Stage 8 --- Manual selection

If EXIF is absent, stripped, or unusable, allow camera search/selection.

Preserve the user's confirmed mapping with the TPS/setup data so the
same problem does not need to be solved repeatedly.

------------------------------------------------------------------------

# 7. Suggested Match Result Type

Do not return only a camera record.

Create an explicit identity-resolution result, conceptually:

``` text
CameraIdentityMatch
    record
    method
    confidence

    rawMake
    rawModel

    normalizedMake
    normalizedModel

    candidates
    requiresConfirmation
```

Suggested methods:

``` text
exactExif
manufacturerIdentifier
normalizedExif
knownAlias
manufacturerConstrainedGuess
userConfirmed
manualSelection
fuzzyCandidate
unresolved
```

Suggested confidence semantics can be implementation-specific, but
automatic resolution should be limited to sufficiently strong methods.

Avoid arbitrary percentage confidence unless there is a meaningful
calibrated reason to use one.

Named states are preferable.

------------------------------------------------------------------------

# 8. Manufacturer Matching Should Be Constrained

Normalize manufacturer identity separately from camera model.

Examples that may need to resolve to the same manufacturer include
variations such as:

``` text
NIKON CORPORATION
Nikon

FUJIFILM
Fujifilm

SONY
Sony

Canon
CANON
```

Use explicit manufacturer normalization/aliases rather than general
fuzzy matching wherever possible.

Once manufacturer is established, search within that manufacturer's
camera records.

This dramatically reduces accidental matches.

------------------------------------------------------------------------

# 9. Mobile Devices

Phones require special handling because:

``` text
device
→ hardware/regional variant
→ physical camera module
→ sensor geometry
```

One phone must not be represented as having one fake universal sensor.

EXIF may identify:

> iPhone 16 Pro

without uniquely identifying whether the image came from:

-   main/wide
-   ultrawide
-   telephoto

Use additional reliable metadata where available, including:

-   lens model
-   focal length
-   focal-length-in-35mm-format
-   manufacturer-specific metadata
-   image characteristics only when deterministic enough

Do not silently choose a physical camera module solely because the
device is known.

If device identity is high-confidence but module identity is ambiguous,
request the minimum necessary confirmation or use another reliable
discriminator.

Keep device-match confidence separate from module-match confidence if
necessary.

------------------------------------------------------------------------

# 10. Provenance UX

Normal users should not be forced to understand evidence tiers.

For A/B/C geometry, normal UX can simply say:

> Camera recognized

C-tier geometry can still be used automatically.

Internally and in exported TPS data, retain:

-   LCRD record ID
-   physical sensor dimensions used
-   geometry evidence tier
-   provenance/method
-   source/reference where appropriate
-   identity-match method
-   raw imported EXIF identity
-   imported image dimensions

An advanced/details view may expose this information.

If geometry is genuinely unavailable, ask for manual physical sensor
dimensions rather than manufacturing certainty.

------------------------------------------------------------------------

# 11. EXIF Research Is No Longer a Release Prerequisite

A separate EXIF identity corpus effort has been started.

Supporting research artifacts include:

-   `LCRD_EXIF_CORPUS_SCHEMA_v0_1.json`
-   `LCRD_EXIF_CORPUS_CODEX_TASK.md`
-   `lcrd_exif_40_camera_extraction_target_v0_1.csv`
-   `lcrd_exif_identity_research_pass_002.csv`
-   `LCRD_EXIF_RESEARCH_PASS_002_NOTES.md`

Do not wait for all 40 camera samples before implementing the resolver.

The architecture must support incremental EXIF observations.

As beta files expose real EXIF variants, those observations can be added
to LCRD.

Implementation and real imported files are now more valuable than
speculative alias research.

------------------------------------------------------------------------

# 12. Feedback Loop to LCRD

Instrument the resolver so development/testing can report:

-   unresolved Make/Model combinations
-   ambiguous matches
-   successful normalized matches
-   aliases that appear repeatedly
-   mobile device/module ambiguities
-   LCRD records missing useful identity metadata

Provide a developer/debug export of unresolved identity observations if
practical.

Do not add telemetry or transmit user image metadata.

LIMNTPS remains offline-first and no-telemetry.

Any corpus contribution should be an explicit developer/user action
outside the normal automatic workflow.

------------------------------------------------------------------------

# 13. Tests

Add tests covering at least:

### Basic identity

-   exact Make + Model
-   case differences
-   whitespace differences
-   manufacturer prefix duplicated in Model
-   punctuation differences
-   Unicode α vs Alpha

### Manufacturer identifiers

-   Sony ILCE identifiers
-   friendly Sony α names
-   Nikon branding variations

### Aliases

-   Canon regional aliases
-   documented marketing/model-number aliases

### Dangerous near matches

Ensure these do not collapse incorrectly:

``` text
EOS R5
EOS R5 C
```

and equivalent generation/model distinctions.

### Missing metadata

-   Make only
-   Model only
-   no EXIF
-   EXIF stripped by editing/export software

### Ambiguity

-   multiple strong candidates
-   weak fuzzy candidate
-   user-confirmed candidate
-   manual camera selection

### Mobile

-   device identified, module identified
-   device identified, module ambiguous
-   multiple physical sensors
-   main vs ultrawide vs telephoto

### Geometry

-   A-tier geometry
-   B-tier derived geometry
-   C-tier estimated geometry
-   structural/non-calculating record
-   imported raster equal to native resolution
-   imported raster different from native resolution

### Persistence

Ensure TPS package round-trip preserves:

-   resolved LCRD ID
-   sensor geometry
-   provenance
-   identity-match method
-   imported raster
-   user confirmation where applicable

------------------------------------------------------------------------

# 14. Do Not Do These Things

Do not:

-   rewrite canonical LCRD names to match EXIF
-   assume marketing name equals EXIF Model
-   claim manufacturer identifiers are observed EXIF unless actually
    observed
-   silently promote estimated geometry to verified geometry
-   use generic fuzzy matching as optical authority
-   silently merge R5 with R5 C or equivalent near-name models
-   assume native sensor pixel dimensions equal imported image
    dimensions
-   collapse multi-camera phones into one sensor
-   require user confirmation for harmless capitalization/punctuation
    differences
-   redesign unrelated LIMNTPS UI
-   expand this into live camera discovery
-   add accounts, telemetry, network requirements, or cloud dependencies

------------------------------------------------------------------------

# 15. Implementation Sequence

Before changing code:

1.  Inspect the existing LIMNTPS architecture.
2.  Locate:
    -   EXIF parsing
    -   imported-image metadata
    -   sensor catalog
    -   sensor selection
    -   TPS geometry calculation
    -   TPS serialization/package round-trip
3.  Summarize the existing architecture.
4.  Identify the smallest clean integration boundary.

Then implement:

1.  LCRD repository/import layer.
2.  Camera identity types.
3.  Manufacturer normalization.
4.  Camera identity resolver.
5.  Sensor-geometry resolution.
6.  Minimal confirmation/manual-selection UI integration.
7.  TPS provenance persistence.
8.  Tests.
9.  Documentation for replacing LCRD v0.1 with a future LCRD release.
10. Developer report of unresolved/ambiguous LCRD identity mappings.

Do not stop merely because some LCRD records lack perfect EXIF aliases.

The resolver is intentionally designed to work with incomplete identity
observations.

------------------------------------------------------------------------

# 16. Definition of Done

This integration is successful when a typical imported image from a
known dedicated camera can flow approximately like this:

``` text
Import image
→ read EXIF
→ SONY / ILCE-7M4
→ resolve Sony α7 IV
→ load 35.9 × 23.9 mm sensor geometry
→ use actual imported image pixel dimensions
→ continue TPS
```

without asking the user to research their sensor.

When the system cannot confidently establish identity, it should degrade
gracefully:

``` text
Import image
→ metadata suggests two plausible cameras
→ show friendly confirmation
→ user chooses
→ continue TPS
```

and finally:

``` text
Import image
→ no usable metadata
→ camera search/manual selection
→ continue TPS
```

The primary objective is not perfect EXIF taxonomy.

The objective is to remove sensor-dimension research from the normal
LIMNTPS user workflow while preserving enough provenance that the result
remains technically defensible.

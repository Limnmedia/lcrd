# LCRD v0.1 freeze notes

## Scope

This freeze is the local v0.1 camera-reference snapshot prepared for review
and downstream integration. It contains 656 records:

- 247 dedicated-camera records;
- 409 mobile-camera-module records;
- 23 evidence-tier `A` records;
- 30 evidence-tier `B` records;
- 602 evidence-tier `C` records; and
- 1 evidence-tier `E` structural record.

The single structural record is `red_dsmc2`. It represents a platform parent,
not a calculable sensor variant, and has `tps_use=no`. A sensor-specific
variant must be selected before it can provide physical geometry.

## Release interpretation

The freeze contains 650 records marked `ship` and 6 records marked
`retain_nonblocking`. The retained records are legacy iPhone models outside
the current iOS coverage target. Their retention is documented for audit and
does not promote them to a stronger evidence tier.

The dataset is not a claim that every row has a direct manufacturer source.
The majority of rows are good working references or estimates. Source URLs,
source titles, evidence tiers, provenance methods, usage notes, and QA flags
must remain attached to the data when it is consumed downstream.

## Geometry rule

`sensor_width_mm`, `sensor_height_mm`, and `sensor_diagonal_mm` describe
physical geometry. They are not image-pixel dimensions. A consuming workflow
must use the imported image's actual raster dimensions for that capture.

The generic RED DSMC2 platform-parent row is intentionally non-calculating.
The sensor-specific child must be resolved instead of silently assuming one
universal DSMC2 sensor.

## Freeze integrity

The companion manifest records the SHA-256 digest and record count for every
research artifact present at the time this freeze was prepared. If a data
file changes, update its manifest entry and create a new versioned freeze;
do not silently rewrite this snapshot.

## Known follow-up work

- Preserve the repository's approved licensing boundaries when adding future
  data, documentation, and tooling contributions.
- Audit and strengthen missing source URLs identified by `qa_flags` and
  `qa_pass4_flags`.
- Keep EXIF observations distinct from manufacturer identifiers and aliases.
- Review mobile-device module ambiguity before automatic camera-module
  resolution.
- Add a versioned schema/data dictionary if the CSV becomes a stable public
  interchange format.

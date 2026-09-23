# Stable identifiers

Stable IDs are public contract values. Consumers must not key records by
display names.

The current forms are:

```text
camera:<manufacturer-slug>:<model-slug>
device:<manufacturer-slug>:<model-slug>
camera_module:<manufacturer-slug>:<device-slug>:<role-slug>
sensor:<source-record-slug>
lens:<manufacturer-slug>:<model-slug>
observation:<source-record-slug>
source:<title-slug>:<stable-hash>
```

Slugs are lower-case ASCII words separated by hyphens. The display name may
change, and aliases may be added, but an existing ID must not be reused for a
different entity. If a published entity is replaced, mark it deprecated and
link `replaced_by` rather than silently repurposing its ID.

`aliases` are known names for the same canonical entity. A
`manufacturer_identifiers` value is a documented manufacturer model
identifier; neither field is an observed EXIF value. Raw EXIF values belong to
observations and must remain unchanged.

Sensor IDs are source-record identifiers when the actual sensor chip identity
is unknown. LCRD does not invent a chip identity from a physical dimension.

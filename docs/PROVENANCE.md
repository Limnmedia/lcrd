# Provenance and evidence

Provenance is first-class. A source record identifies the title, publisher,
URL, type, and notes. An observation links a subject to a source and preserves
the original value and method.

The current evidence convenience tiers mean:

- `A` — verified direct evidence;
- `B` — strong derived evidence;
- `C` — good working reference or estimate;
- `D` — best available guess below the normal automatic-use threshold; and
- `E` — unresolved or structural/non-calculating.

The tier never replaces the underlying method. Examples include `published`,
`active_raster_x_pixel_pitch`, `optical_format_conversion`, and
`family_sensor_class_estimate`. Optical formats such as `1/1.56"` are not
literal physical diagonals; any converted dimensions remain estimates.

Downstream consumers may choose their own automatic-use policy, but they must
not silently promote estimated or derived geometry to manufacturer-published
facts.

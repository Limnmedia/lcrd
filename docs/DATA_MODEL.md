# LCRD data model

LCRD follows the chain:

```text
source → observation → reference entity → derived/convenience view → distribution
```

Canonical collections are stored as JSON under `data/`:

- `cameras` — dedicated cameras and their stable identity;
- `devices` — phones and other devices that contain one or more modules;
- `camera_modules` — physical camera paths within a device;
- `sensors` — physical geometry and its status;
- `lenses` — reserved for independently identified lenses;
- `observations` — source-backed facts, including preserved legacy rows; and
- `sources` — de-duplicated source metadata.

The frozen migration keeps the complete original CSV row under each observation
in `legacy`. This prevents information loss while the public model evolves.
`values` contains the normalized, useful subset for consumers.

Sensor geometry is linked to the camera or module that uses it. A mobile
device is not assigned one universal sensor: each physical module has its own
sensor relationship. When a named physical sensor model is explicitly shared
by multiple records, one sensor entity may list multiple `owner_ids`; anonymous
sensors remain separate rather than being merged by dimensions alone.

`dist/lcrd.json` is relational and provenance-rich. `dist/lcrd.min.json` is a
smaller lookup view. `dist/lcrd.csv` is a convenience flattening of
observations and cannot express all relationships without repeating data.

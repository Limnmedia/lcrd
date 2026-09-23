# Traceability examples

The repeatable audit procedure is:

```text
entity → sensor or camera module → observation → source
```

Start with the entity ID in `data/`. Follow its `sensor_id`, or follow a
device's `camera_module_ids` and then each module's `sensor_id`. Use the
sensor's `source_observation_id`/`source_observation_ids` to find observations,
then follow each observation's `source_id` into `data/sources/sources.json`.
The observation preserves the original research row in `legacy` and the
normalized facts in `values`.

Representative checks:

| Case | Entity path | What it demonstrates |
| --- | --- | --- |
| Sony α7 IV | `camera:sony:alpha-a7-iv` → `sensor:sony-alpha-a7-iv` → `observation:sony-alpha-a7-iv` | Published 35.9 × 23.9 mm, tier A |
| Canon EOS R5 / R5 C | `camera:canon:eos-r5` or `camera:canon:eos-r5-c` → matching sensor and observation | Similar geometry does not erase distinct camera identities |
| Intel RealSense D455 RGB | `camera:intel-realsense:depth-camera-d455` → `sensor:model:omnivision-ov9782` → `observation:intel-realsense-depth-camera-d455` | RGB-module geometry derived from active raster × pixel pitch, tier B |
| iPhone 16 Pro | `device:apple:iphone-16-pro` → `camera_module:apple:iphone-16-pro:rear-main` (or another role) → sensor → observation | One device has independent physical modules |
| RED DSMC2 parent | `camera:red:dsmc2` → `sensor:red-dsmc2` → `observation:red-dsmc2` | Platform identity is retained without fabricated geometry; tier E |

The same procedure applies to a named shared sensor: inspect all `owner_ids`
before deciding whether a repeated geometry is a shared physical model or an
anonymous source-associated record. `dist/lcrd.json` preserves the full
relationship and source detail; `dist/lcrd.min.json` preserves the lookup
relationships and geometry status/method/evidence tier but not full sources.

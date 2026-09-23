# Consuming LCRD

Build the distributions locally with:

```text
python tools/lcrd.py build
```

Applications that need rich provenance should use `dist/lcrd.json`. Small
applications can use `dist/lcrd.min.json`, which contains cameras, devices,
camera modules, and sensors. The CSV is intended for inspection and
spreadsheet workflows.

Example lookup in Python:

```python
import json

with open("dist/lcrd.min.json", encoding="utf-8") as stream:
    lcrd = json.load(stream)

camera = next(c for c in lcrd["cameras"] if c["id"] == "camera:canon:eos-r5")
sensor = next(s for s in lcrd["sensors"] if s["id"] == camera["sensor_id"])
print(sensor["width_mm"], sensor["height_mm"])
```

For provenance, load `dist/lcrd.json`, find the observation by `subject_id`,
then follow its `source_id` into `sources`. The observation's `legacy` object
contains the original research fields, while `values` contains the normalized
subset.

For multi-camera devices, resolve the device's `camera_module_ids`, then follow
each module's `sensor_id`. Do not assign one sensor to the whole device.

Estimated geometry is identified by `geometry_method`, `geometry_status`, and
the linked observation's evidence/provenance fields. EXIF observations remain
raw values in the observation layer; consumers may normalize them for lookup
without changing the stored value.

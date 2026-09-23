#!/usr/bin/env python3
"""Build and validate the LCRD public data products.

The repository intentionally uses only the Python standard library so that
contributors can validate and build LCRD on a clean machine.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "Research"
DATA = ROOT / "data"
DIST = ROOT / "dist"
SCHEMA = ROOT / "schema"
DATASET_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"

# These are explicit source-record aliases, not a general fuzzy matcher. Each
# pass row is a direct model-level observation of the already frozen camera.
RESEARCH_ENTITY_ALIASES = {
    "sony_ilce_7m4": "sony_alpha_a7_iv",
    "sony_ilce_7rm5": "sony_alpha_a7r_v",
    "sony_ilce_7rm4": "sony_alpha_a7r_iv",
    "sony_ilce_6700": "sony_alpha_a6700",
    "panasonic_lumix_s5_ii": "panasonic_lumix_dc_s5m2",
    "fujifilm_gfx100_ii": "fujifilm_gfx_100_ii",
    "fujifilm_gfx100": "fujifilm_gfx_100",
    "om_system_om_1": "olympus_om_system_om_1",
    "om_system_om_1_mark_ii": "olympus_om_system_om_1_mark_ii",
}


def slug(value: str | None) -> str:
    value = (value or "unknown").strip().lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "unknown"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def text(row: dict[str, str], key: str) -> str | None:
    value = row.get(key, "")
    return value.strip() or None


def number(row: dict[str, str], key: str) -> float | None:
    value = text(row, key)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def source_id(title: str | None, url: str | None) -> str:
    basis = f"{title or 'unresolved'}|{url or ''}"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"source:{slug(title)}:{digest}"


def observation_digest(row: dict[str, str], subject_id: str, source_id_value: str | None) -> str:
    payload = json.dumps(
        {"row": row, "subject_id": subject_id, "source_id": source_id_value},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def load_source_records() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    sources: dict[str, dict[str, Any]] = {}
    source_keys: dict[str, str] = {}
    for path in sorted(RESEARCH.glob("*.csv")):
        for row in read_csv(path):
            title = text(row, "source_title") or text(row, "source_note")
            url = text(row, "source_url")
            if title is None and url is None:
                continue
            key = f"{title or ''}|{url or ''}"
            sid = source_keys.setdefault(key, source_id(title, url))
            sources[sid] = {
                "id": sid,
                "title": title or "Unresolved source",
                "publisher": text(row, "manufacturer"),
                "url": url,
                "source_type": "research_reference",
                "accessed": None,
                "notes": "Source metadata preserved from the research pass.",
            }
    return sources, source_keys


def entity_ids(row: dict[str, str], fallback: str) -> tuple[str, str | None, str]:
    manufacturer = text(row, "manufacturer") or "Unknown"
    model = text(row, "device_model") or text(row, "model") or text(row, "device") or fallback
    role = text(row, "module_role")
    if text(row, "record_class") == "mobile_camera_module" or text(row, "device"):
        device_id = f"device:{slug(manufacturer)}:{slug(text(row, 'device') or model)}"
        module_id = f"camera_module:{slug(manufacturer)}:{slug(text(row, 'device') or model)}"
        if role:
            module_id += f":{slug(role)}"
        return device_id, module_id, model
    return f"camera:{slug(manufacturer)}:{slug(model)}", None, model


def migrate() -> None:
    freeze_path = RESEARCH / "lcrd_camera_reference_v0_1_FREEZE.csv"
    freeze = read_csv(freeze_path)
    sources, source_keys = load_source_records()
    cameras: dict[str, dict[str, Any]] = {}
    devices: dict[str, dict[str, Any]] = {}
    modules: dict[str, dict[str, Any]] = {}
    sensors: dict[str, dict[str, Any]] = {}
    observations: list[dict[str, Any]] = []
    seen_entities: dict[str, str] = {}

    def add_sensor(record_id: str, row: dict[str, str], owner: str) -> str:
        sensor_name = text(row, "sensor_model")
        sid = f"sensor:model:{slug(sensor_name)}" if sensor_name else f"sensor:{slug(record_id)}"
        if sid not in sensors:
            sensors[sid] = {
                "id": sid,
                "name": sensor_name,
                "owner_id": owner,
                "owner_ids": [owner],
                "width_mm": number(row, "sensor_width_mm"),
                "height_mm": number(row, "sensor_height_mm"),
                "diagonal_mm": number(row, "sensor_diagonal_mm"),
                "geometry_status": text(row, "lcrd_status") or text(row, "dimension_status") or "unresolved",
                "geometry_method": text(row, "provenance_method") or text(row, "dimension_method"),
                "evidence_tier": text(row, "evidence_tier"),
                "source_observation_id": f"observation:{slug(record_id)}",
                "source_observation_ids": [f"observation:{slug(record_id)}"],
            }
        else:
            if owner not in sensors[sid]["owner_ids"]:
                sensors[sid]["owner_ids"].append(owner)
            observation_id = f"observation:{slug(record_id)}"
            if observation_id not in sensors[sid]["source_observation_ids"]:
                sensors[sid]["source_observation_ids"].append(observation_id)
        return sid

    for index, row in enumerate(freeze, start=1):
        record_id = text(row, "record_id") or f"freeze-{index}"
        owner_id, module_id, model = entity_ids(row, record_id)
        manufacturer = text(row, "manufacturer") or "Unknown"
        role = text(row, "module_role")
        sensor_id = add_sensor(record_id, row, module_id or owner_id)
        if module_id:
            device_id = owner_id
            if device_id not in devices:
                devices[device_id] = {
                    "id": device_id,
                    "manufacturer": manufacturer,
                    "name": text(row, "device_model") or model,
                    "device_model": text(row, "device_model") or model,
                    "camera_module_ids": [],
                    "status": "active_reference",
                }
            if module_id not in modules:
                modules[module_id] = {
                    "id": module_id,
                    "device_id": device_id,
                    "manufacturer": manufacturer,
                    "name": f"{model} {role or 'camera module'}",
                    "module_role": role,
                    "sensor_id": sensor_id,
                    "status": text(row, "lcrd_status") or "reference",
                }
                devices[device_id]["camera_module_ids"].append(module_id)
            subject_id = module_id
        else:
            if owner_id not in cameras:
                cameras[owner_id] = {
                    "id": owner_id,
                    "manufacturer": manufacturer,
                    "name": model,
                    "device_model": model,
                    "variant": text(row, "device_variant"),
                    "module_role": text(row, "module_role"),
                    "aliases": [],
                    "manufacturer_identifiers": [],
                    "sensor_id": sensor_id,
                    "status": text(row, "lcrd_status") or "reference",
                }
            subject_id = owner_id
        seen_entities[record_id] = subject_id
        title = text(row, "source_title")
        url = text(row, "source_url")
        sid = source_keys.get(f"{title or ''}|{url or ''}")
        observation = {
            "id": f"observation:{slug(record_id)}",
            "subject_id": subject_id,
            "source_id": sid,
            "kind": "camera_reference_freeze",
            "observed_at": None,
            "values": {
                "manufacturer": manufacturer,
                "model": model,
                "module_role": role,
                "sensor_width_mm": number(row, "sensor_width_mm"),
                "sensor_height_mm": number(row, "sensor_height_mm"),
                "sensor_diagonal_mm": number(row, "sensor_diagonal_mm"),
                "evidence_tier": text(row, "evidence_tier"),
                "provenance_method": text(row, "provenance_method"),
                "confidence": text(row, "original_confidence"),
            },
            "legacy_record_id": record_id,
            "legacy": row,
        }
        observations.append(observation)

    # Preserve supplemental research passes as explicit observations. Rows
    # that match the freeze are linked to that entity; unmatched rows receive
    # stable research-only subjects without overwriting canonical identities.
    for path in sorted(RESEARCH.glob("*.csv")):
        if path.name == freeze_path.name:
            continue
        for index, row in enumerate(read_csv(path), start=1):
            rid = text(row, "id") or text(row, "record_id") or f"{path.stem}-{index}"
            lookup_id = RESEARCH_ENTITY_ALIASES.get(rid, rid)
            subject_id = seen_entities.get(lookup_id)
            if subject_id is None:
                subject_id, module_id, model = entity_ids(row, rid)
                manufacturer = text(row, "manufacturer") or "Unknown"
                if module_id:
                    devices.setdefault(
                        subject_id,
                        {
                            "id": subject_id,
                            "manufacturer": manufacturer,
                            "name": text(row, "device") or model,
                            "device_model": text(row, "device") or model,
                            "camera_module_ids": [],
                            "status": "research_reference",
                        },
                    )
                    sid = f"sensor:{slug(path.stem)}:{index}"
                    sensors.setdefault(
                        sid,
                        {
                            "id": sid,
                            "name": text(row, "sensor_name"),
                            "owner_id": module_id,
                            "owner_ids": [module_id],
                            "width_mm": number(row, "sensor_width_mm"),
                            "height_mm": number(row, "sensor_height_mm"),
                            "geometry_status": text(row, "confidence") or "unresolved",
                            "geometry_method": text(row, "dimension_method"),
                            "evidence_tier": None,
                            "source_observation_id": None,
                            "source_observation_ids": [],
                        },
                    )
                    modules.setdefault(
                        module_id,
                        {
                            "id": module_id,
                            "device_id": subject_id,
                            "manufacturer": manufacturer,
                            "name": f"{model} {text(row, 'module_role') or 'camera module'}",
                            "module_role": text(row, "module_role"),
                            "sensor_id": sid,
                            "status": "research_reference",
                        },
                    )
                    if module_id not in devices[subject_id]["camera_module_ids"]:
                        devices[subject_id]["camera_module_ids"].append(module_id)
                else:
                    cameras.setdefault(
                        subject_id,
                        {
                            "id": subject_id,
                            "manufacturer": manufacturer,
                            "name": model,
                            "device_model": model,
                            "variant": None,
                            "module_role": text(row, "module_role"),
                            "aliases": [],
                            "manufacturer_identifiers": [],
                            "sensor_id": None,
                            "status": "research_reference",
                        },
                    )
            if subject_id in cameras:
                aliases = text(row, "aliases")
                if aliases:
                    cameras[subject_id]["aliases"] = sorted(
                        set(cameras[subject_id].get("aliases", []))
                        | {item.strip() for item in aliases.split("|") if item.strip()}
                    )
                model_value = text(row, "model")
                if model_value and "/" in model_value:
                    identifiers = {
                        item.strip()
                        for item in model_value.split("/")[1:]
                        if item.strip() and any(character.isdigit() for character in item)
                    }
                    cameras[subject_id]["manufacturer_identifiers"] = sorted(
                        set(cameras[subject_id].get("manufacturer_identifiers", [])) | identifiers
                    )
            title = text(row, "source_title") or text(row, "source_note")
            url = text(row, "source_url")
            sid = source_keys.get(f"{title or ''}|{url or ''}")
            observation_id = observation_digest(row, subject_id, sid)
            observations.append(
                {
                    "id": f"observation:research:{observation_id}",
                    "subject_id": subject_id,
                    "source_id": sid,
                    "kind": "research_pass",
                    "observed_at": None,
                    "values": {"confidence": text(row, "confidence"), "method": text(row, "dimension_method") or text(row, "provenance_method")},
                    "legacy_record_id": rid,
                    "research_file": path.name,
                    "legacy": row,
                }
            )

    write_json(DATA / "cameras" / "cameras.json", {"records": sorted(cameras.values(), key=lambda x: x["id"])})
    write_json(DATA / "devices" / "devices.json", {"records": sorted(devices.values(), key=lambda x: x["id"])})
    write_json(DATA / "camera_modules" / "camera_modules.json", {"records": sorted(modules.values(), key=lambda x: x["id"])})
    write_json(DATA / "sensors" / "sensors.json", {"records": sorted(sensors.values(), key=lambda x: x["id"])})
    write_json(DATA / "lenses" / "lenses.json", {"records": []})
    write_json(DATA / "observations" / "observations.json", {"records": sorted(observations, key=lambda x: x["id"])})
    write_json(DATA / "sources" / "sources.json", {"records": sorted(sources.values(), key=lambda x: x["id"])})
    print(f"migrated {len(cameras)} cameras, {len(devices)} devices, {len(modules)} modules, {len(sensors)} sensors, {len(observations)} observations, {len(sources)} sources")


def load_records(directory: str, filename: str) -> list[dict[str, Any]]:
    path = DATA / directory / filename
    return json.loads(path.read_text(encoding="utf-8"))["records"]


def validate() -> int:
    errors: list[str] = []
    collections = {
        "cameras": load_records("cameras", "cameras.json"),
        "devices": load_records("devices", "devices.json"),
        "camera_modules": load_records("camera_modules", "camera_modules.json"),
        "sensors": load_records("sensors", "sensors.json"),
        "lenses": load_records("lenses", "lenses.json"),
        "observations": load_records("observations", "observations.json"),
        "sources": load_records("sources", "sources.json"),
    }
    schema_map = {
        "cameras": "camera.schema.json",
        "devices": "device.schema.json",
        "camera_modules": "camera_module.schema.json",
        "sensors": "sensor.schema.json",
        "lenses": "lens.schema.json",
        "observations": "observation.schema.json",
        "sources": "source.schema.json",
    }
    for collection, schema_name in schema_map.items():
        schema = json.loads((SCHEMA / schema_name).read_text(encoding="utf-8"))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{schema_name}: unsupported or missing JSON Schema dialect")
        for record in collections[collection]:
            for field in schema.get("required", []):
                if field not in record:
                    errors.append(f"{record.get('id', '<unknown>')}: missing schema field {field}")
            try:
                import jsonschema

                validator = jsonschema.Draft202012Validator(schema)
                errors.extend(
                    f"{record.get('id', '<unknown>')}: schema: {error.message}"
                    for error in validator.iter_errors(record)
                )
            except ImportError:
                # The standard-library fallback above still checks all public
                # required fields and repository relationships. CI installs
                # jsonschema for full Draft 2020-12 validation.
                pass
    all_ids: dict[str, str] = {}
    for name, records in collections.items():
        for record in records:
            rid = record.get("id")
            if not isinstance(rid, str) or not rid:
                errors.append(f"{name}: record has no stable id")
            elif rid in all_ids:
                errors.append(f"duplicate id {rid} in {name} and {all_ids[rid]}")
            else:
                all_ids[rid] = name
    for record in collections["sensors"]:
        for field in ("width_mm", "height_mm"):
            value = record.get(field)
            if value is not None and (not isinstance(value, (int, float)) or value <= 0):
                errors.append(f"{record['id']}: invalid {field}")
        owner = record.get("owner_id")
        if owner and owner not in all_ids:
            errors.append(f"{record['id']}: missing owner {owner}")
        for owner_id in record.get("owner_ids", []):
            if owner_id not in all_ids:
                errors.append(f"{record['id']}: missing owner {owner_id}")
    for record in collections["camera_modules"]:
        for field in ("device_id", "sensor_id"):
            value = record.get(field)
            if value and value not in all_ids:
                errors.append(f"{record['id']}: missing {field} {value}")
    for record in collections["devices"]:
        for module_id in record.get("camera_module_ids", []):
            if module_id not in all_ids:
                errors.append(f"{record['id']}: missing module {module_id}")
    for record in collections["observations"]:
        if record.get("subject_id") not in all_ids:
            errors.append(f"{record['id']}: orphan subject {record.get('subject_id')}")
        source_id = record.get("source_id")
        if source_id and source_id not in all_ids:
            errors.append(f"{record['id']}: missing source {source_id}")
    if errors:
        print("validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("validation passed")
    for name, records in collections.items():
        print(f"{name}: {len(records)}")
    return 0


def build() -> int:
    if validate() != 0:
        return 1
    collections = {}
    for directory, filename, key in [
        ("cameras", "cameras.json", "cameras"),
        ("devices", "devices.json", "devices"),
        ("camera_modules", "camera_modules.json", "cameraModules"),
        ("sensors", "sensors.json", "sensors"),
        ("lenses", "lenses.json", "lenses"),
        ("observations", "observations.json", "observations"),
        ("sources", "sources.json", "sources"),
    ]:
        collections[key] = load_records(directory, filename)
    generated_at = os.environ.get("LCRD_GENERATED_AT", "1970-01-01T00:00:00Z")
    source_commit = os.environ.get("LCRD_SOURCE_COMMIT", "unknown")
    rich = {"lcrdVersion": DATASET_VERSION, "schemaVersion": SCHEMA_VERSION, "generatedAt": generated_at, "sourceCommit": source_commit, **collections}
    DIST.mkdir(parents=True, exist_ok=True)
    write_json(DIST / "lcrd.json", rich)
    minimal = {
        "lcrdVersion": DATASET_VERSION,
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "sourceCommit": source_commit,
        "cameras": collections["cameras"],
        "devices": collections["devices"],
        "cameraModules": collections["cameraModules"],
        "sensors": collections["sensors"],
    }
    write_json(DIST / "lcrd.min.json", minimal)
    rows: list[dict[str, Any]] = []
    for observation in collections["observations"]:
        row = {"observation_id": observation["id"], "subject_id": observation["subject_id"], "source_id": observation.get("source_id"), "kind": observation["kind"]}
        row.update(observation.get("legacy", {}))
        rows.append(row)
    columns = sorted({key for row in rows for key in row})
    with (DIST / "lcrd.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    for path in sorted(DIST.iterdir()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{path.name}: {path.stat().st_size} bytes sha256={digest}")
    return 0


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if command == "migrate":
        migrate()
        return 0
    if command == "validate":
        return validate()
    if command == "build":
        return build()
    print("usage: python tools/lcrd.py [migrate|validate|build]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

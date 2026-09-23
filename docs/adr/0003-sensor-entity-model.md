# 0003 — Sensor entity model

## Context

A camera or module may have known physical geometry without a defensible
sensor-chip identity. Identical dimensions alone do not prove shared hardware.

## Decision

Use a distinct sensor entity for an anonymous/source-associated record unless
exact physical sensor-model identity is defensible. Share a named sensor only
when the evidence supports the same physical model. Preserve geometry and
uncertainty on either kind of record.

## Why

This avoids accidental sensor merging while still allowing real shared models
to be represented once with multiple owners.

## Consequences

The sensor count is larger than the count of named chips. Anonymous sensors
are intentional, not automatically duplicate knowledge.

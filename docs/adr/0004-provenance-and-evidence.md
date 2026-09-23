# 0004 — Provenance and evidence

## Context

An evidence tier is useful for filtering, but it cannot explain how a value
was obtained or where it came from.

## Decision

Store source, observation, method, confidence, geometry status, and evidence
tier separately. Tiers are convenience classifications: A verified, B strong
derived, C good reference/explicit estimate, D weak fallback, and E
unresolved/structural.

## Why

`published`, `active_raster_x_pixel_pitch`, `optical_format_conversion`, and
family estimates have materially different meanings even when a consumer uses
all of them.

## Consequences

Consumers may adopt their own automatic-use policy, but must not relabel a
derived or estimated value as manufacturer-published.

# 0002 — Stable identifiers

## Context

Display names, aliases, and source filenames change. Consumers need keys that
remain usable across dataset releases.

## Decision

Every public entity and observation has a readable stable ID. IDs are not
display names, are not row numbers, and must not depend on temporary research
filenames. Existing IDs are never casually renamed or reused for another
entity; corrections use deprecation/replacement deliberately.

## Why

Stable references make distributions, applications, and citations resilient
to spelling or display-name improvements.

## Consequences

Some current anonymous sensor IDs look less elegant than a later naming
scheme. They remain valid public identifiers and must be preserved.

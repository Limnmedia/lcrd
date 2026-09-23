# 0006 — EXIF identity resolution

## Context

Canonical names, manufacturer identifiers, aliases, and observed metadata are
different kinds of identity evidence. The current research does not include a
complete raw EXIF corpus.

## Decision

Keep raw observed metadata unchanged when it exists. Consumers may resolve in
the order raw exact observation, manufacturer identifier, normalized exact,
explicit alias, candidate match, user confirmation, and manual selection.
Manufacturer identifiers and aliases are not called EXIF observations unless
they were extracted from an actual file.

## Why

This preserves auditability and prevents a weak fuzzy match from silently
authorizing physical sensor geometry.

## Consequences

Some metadata resolves to candidates or remains unresolved until a user
confirms it. Building an empirical EXIF corpus is a separate data effort.

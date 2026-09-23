# Generated distributions

Files in this directory are generated consumer artifacts. Do not edit them by
hand. Rebuild them with:

```text
python tools/lcrd.py build
```

Use `lcrd.json` for relational data and full observations/sources,
`lcrd.min.json` for compact offline identity and sensor lookup, and
`lcrd.csv` for flat inspection. A source change may update one or more of
these files; review the generated diff and confirm that it is deterministic.
See [`../docs/CONSUMING_LCRD.md`](../docs/CONSUMING_LCRD.md).

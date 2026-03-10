# Metrics Notes

## Metric types
- Use `Counter` for monotonically increasing totals.
- Use `Gauge` for point-in-time values.

## Naming rules
- Metric names must start with a letter.
- Use only letters, digits, and underscores.
- Do not end names with reserved suffixes: `_sum`, `_bucket`, `_count`, `_total`.

## Labels
- Label keys must start with a letter.
- Use only letters, digits, and underscores.
- Do not use reserved labels: `le`, `quantile`.
- Keep label cardinality small to avoid large metric series.

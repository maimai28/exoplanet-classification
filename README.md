# Exoplanet Classification: small vs. large (R = 2 R⊕)

Binary classification of exoplanet size class, `small` (R < 2 R⊕) or `large`
(R ≥ 2 R⊕), from the orbital period and the host-star parameters, on the 623
planets of `data/raw/exoplanets_clean.csv`. Label definition: T4b in
`docs/decisiones.md`.

## Reproduce

```bash
uv sync --locked
uv run jupyter nbconvert --to notebook --execute classification.ipynb --output /tmp/run.ipynb
```

The second command runs `classification.ipynb` end to end and rewrites its
outputs in `data/processed/` (files and schemas: "Contrato de interfaz" in
`docs/plan.md`). Tests: `uv run pytest -q`.

## Question and label

<!-- T8 (Mai) -->

## Data and lineage

<!-- T8 (Mai) -->

## Leakage verdicts

<!-- T8 (Mai) -->

## Method

<!-- T8 (Mai) -->

## Results

Run `main` (623 rows), mean ± std (ddof = 1) over the 25 evaluations, from
`data/processed/metrics.json`. Positive class: `small`.

<!-- metrics:start -->
| Model | `accuracy` | `average_precision_small` | `balanced_accuracy` | `f1_small` | `precision_small` | `recall_small` | `roc_auc` |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.757 ± 0.034 | 0.515 ± 0.154 | 0.727 ± 0.068 | 0.435 ± 0.065 | 0.322 ± 0.045 | 0.684 ± 0.160 | 0.797 ± 0.073 |
| Random Forest | 0.847 ± 0.028 | 0.433 ± 0.107 | 0.637 ± 0.063 | 0.379 ± 0.122 | 0.435 ± 0.146 | 0.347 ± 0.128 | 0.789 ± 0.059 |
| SVM (RBF) | 0.826 ± 0.028 | 0.426 ± 0.090 | 0.715 ± 0.052 | 0.471 ± 0.073 | 0.410 ± 0.069 | 0.563 ± 0.106 | 0.769 ± 0.061 |
| Baseline (prior) | 0.862 ± 0.003 | 0.138 ± 0.003 | 0.500 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 |
<!-- metrics:end -->

<!-- T8 (Mai): interpretation. T9: tables from comparisons.json and metrics_sensitivity.json. -->

## Discussion

<!-- T8 (Mai) -->

## Authorship

<!-- T9 -->

## Files

- `classification.ipynb` — the whole analysis; writes every output of the
  contract.
- `data/raw/` — input data (immutable) and `SHA256SUMS`.
- `data/processed/` — lineage, mass provenance and the notebook outputs.
- `docs/` — brief, plan, decisions and log (in Spanish).
- `tests/` — pytest suite for the success criteria of `docs/brief.md`.
- `pyproject.toml`, `uv.lock` — dependencies; `uv.lock` is the source of
  truth (`requirements.txt` is not).

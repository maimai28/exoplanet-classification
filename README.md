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

This repository audits an earlier classification project. The original label turned out to be a threshold on planet radius, so the task was reframed: **can a planet's size class (below or above 2 R⊕) be predicted from its orbital period and host-star properties alone?** In short: partly. All models clearly beat chance (average precision 0.43–0.52 vs 0.14), none is significantly better than the others, and the signal is concentrated in part of the sample. Every decision is documented in `docs/decisiones.md`.

## Data and lineage

<!-- T8 (Mai) -->

- 623 planets × 7 columns (`mass`, `radius`, `orbital_period`, `star_mass`, `star_radius`, `star_teff`, `planet_type`). Exact origin unknown: the values match an older release of the NASA Exoplanet Archive *PSCompPars* table (row-level matching in `data/processed/lineage.csv`). The file is stored unmodified in `data/raw/` with its SHA-256.
- `radius` is in Jupiter radii. The original label `planet_type` is reproduced exactly (623/623) by the rule R ≥ 2 R⊕ (0.1784 R_J). The original class names ("terrestrial" / "gas_giant") are physically misleading: the boundary sits at the upper edge of the radius valley and separates *size*, not composition. Classes are renamed `small` (R < 2 R⊕, 86 rows) and `large` (537 rows).
- Planets in the same system are grouped (connected components by host name or identical stellar parameters: 504 groups, largest = 7) so that no system is split between training and test.

## Leakage verdicts

<!-- T8 (Mai) -->

- `radius` is excluded: the label is a threshold on it.
- `mass` is excluded from the main model. Comparing each mass with the Chen & Kipping (2017) mass–radius relation used by the Archive: 4 masses are derived from radius, 236 are measured, and 383 cannot be verified because they come from an older catalog version. A mass that may have been computed from radius cannot be used to predict radius.
- Main model features: `orbital_period`, `star_mass`, `star_radius`, `star_teff`. `star_radius` enters the measured planet radius (R = (Rp/R*)·R*) but does not fix it on its own; its effect is tested by ablation.
- Sensitivity run: the same models with `mass` added, restricted to the 236 measured rows.

## Method

<!-- T8 (Mai) -->

- Models: Logistic Regression, Random Forest and SVM (RBF) with the original notebook's hyperparameters (including `class_weight="balanced"`), no tuning; plus a prior baseline.
- Evaluation: StratifiedGroupKFold, k = 5 × 5 seeds = 25 evaluations, grouped by system.
- Main metric: average precision for `small` (baseline = prevalence = 0.138). Also reported: balanced accuracy, ROC-AUC, accuracy and precision/recall/F1 for `small` at each model's default decision threshold.
- Model comparison: Nadeau–Bengio corrected resampled t-test on average precision (df = 24).
- The sensitivity run has only 17 `small` planets and is reported as exploratory, without significance tests.

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

All three models beat the prior baseline by a wide margin on the main metric: average precision for `small` is 0.52 ± 0.15 (Logistic Regression), 0.43 ± 0.11 (Random Forest) and 0.43 ± 0.09 (SVM), against 0.138 for the baseline (p < 0.001 in all three corrected t-tests). ROC-AUC is 0.77–0.80. The differences *between* models are not significant (p = 0.20–0.91): the fold-to-fold spread is as large as the gaps, so the data do not support ranking them.

At the default threshold the models trade precision for recall differently: Logistic Regression recovers 68 % of small planets with 32 % precision; Random Forest is more conservative (35 % recall, 44 % precision). Accuracy (0.76–0.85) is *below* the 0.86 obtained by always predicting `large`, which is why it is not used to judge the models.

The signal is not uniform across the sample. Slicing the same out-of-fold predictions by mass provenance, Logistic Regression reaches ROC-AUC 0.81 on the 383 unverifiable rows but only 0.68 on the 236 measured rows. On the measured subset alone (exploratory, 17 small planets), models retrained without mass reach ROC-AUC 0.55–0.63; adding mass raises it substantially (SVM: 0.55 → 0.83), as expected from the physical mass–radius relation.

## Discussion

<!-- T8 (Mai) -->

- **What the result means.** A planet's orbital period and its host star carry real information about whether the planet lies above or below ~2 R⊕ — enough to lift average precision 3–4× above chance, but far from a reliable classifier. This is consistent with known trends (short-period giant planets in transit surveys, small planets being more common around cool, low-mass stars), but this analysis does not test any mechanism.
- **Why the signal is uneven.** The gap between measured and unverifiable rows is most likely a sample effect, not leakage: the main model does not use mass. Measured masses come mostly from radial-velocity follow-up, which favors bright stars and massive planets; the unverifiable rows come from an older catalog release with different detection biases. The models learn properties of *this catalog*; the numbers should not be read as properties of the planet population.
- **Limitations.** Unknown exact origin of the data and an outdated catalog version; only 86 small planets; no hyperparameter tuning; the label encodes size, not composition; the mass sensitivity run is exploratory.
- **What changed from the original project.** The original notebook already excluded `radius`, but it kept `mass` (4 of its values are derived from radius and 383 cannot be verified), evaluated each model on a single stratified 80/20 split (about 17 small planets in the test set) without grouping planets by system, and named the classes "terrestrial" and "gas giant". Its best result, F1 = 0.72 for the minority class (Random Forest), depended on `mass`; without it and with grouped, repeated cross-validation, F1 for `small` is 0.38–0.47.

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

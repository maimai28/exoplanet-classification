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

<!-- comparisons:start -->
Nadeau–Bengio corrected resampled t-test on `average_precision_small`, from `data/processed/comparisons.json` (df = 24, ρ = `test_train_ratio` = 0.250); two-sided p-values as written in the file.

Run `main`:

| Pair (A vs B) | `mean_diff` (A − B) | `t` | `df` | `p_value` |
|---|---|---|---|---|
| Logistic Regression vs Random Forest | 0.082 | 1.144 | 24 | 0.263822 |
| Logistic Regression vs SVM (RBF) | 0.089 | 1.314 | 24 | 0.201358 |
| Logistic Regression vs Baseline (prior) | 0.377 | 4.542 | 24 | 0.000133 |
| Random Forest vs SVM (RBF) | 0.007 | 0.120 | 24 | 0.905695 |
| Random Forest vs Baseline (prior) | 0.295 | 5.134 | 24 | 0.000030 |
| SVM (RBF) vs Baseline (prior) | 0.288 | 5.924 | 24 | 0.000004 |
<!-- comparisons:end -->

<!-- sensitivity:start -->
Sensitivity runs on the 236 rows with `mass_provenance == measured` (17 `small`), mean ± std (ddof = 1) over the 25 evaluations, from `data/processed/metrics_sensitivity.json`. Exploratory (`n_small` < 25): no significance test.

Without mass (`sens_without_mass`, features `main`):

| Model | `accuracy` | `average_precision_small` | `balanced_accuracy` | `f1_small` | `precision_small` | `recall_small` | `roc_auc` |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.691 ± 0.045 | 0.192 ± 0.144 | 0.594 ± 0.180 | 0.169 ± 0.123 | 0.104 ± 0.074 | 0.480 ± 0.376 | 0.629 ± 0.144 |
| Random Forest | 0.899 ± 0.026 | 0.213 ± 0.162 | 0.538 ± 0.102 | 0.118 ± 0.204 | 0.131 ± 0.230 | 0.117 ± 0.204 | 0.588 ± 0.184 |
| SVM (RBF) | 0.661 ± 0.093 | 0.134 ± 0.103 | 0.520 ± 0.134 | 0.111 ± 0.101 | 0.067 ± 0.063 | 0.353 ± 0.334 | 0.549 ± 0.117 |
| Baseline (prior) | 0.928 ± 0.010 | 0.072 ± 0.010 | 0.500 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 |

With mass (`sens_with_mass`, features `sensitivity_mass`):

| Model | `accuracy` | `average_precision_small` | `balanced_accuracy` | `f1_small` | `precision_small` | `recall_small` | `roc_auc` |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.781 ± 0.050 | 0.369 ± 0.166 | 0.829 ± 0.087 | 0.368 ± 0.070 | 0.235 ± 0.048 | 0.883 ± 0.185 | 0.870 ± 0.074 |
| Random Forest | 0.947 ± 0.035 | 0.689 ± 0.252 | 0.824 ± 0.169 | 0.619 ± 0.282 | 0.614 ± 0.299 | 0.680 ± 0.339 | 0.960 ± 0.039 |
| SVM (RBF) | 0.740 ± 0.065 | 0.340 ± 0.123 | 0.770 ± 0.098 | 0.311 ± 0.079 | 0.198 ± 0.062 | 0.803 ± 0.207 | 0.830 ± 0.083 |
| Baseline (prior) | 0.928 ± 0.010 | 0.072 ± 0.010 | 0.500 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 |
<!-- sensitivity:end -->

## Discussion

<!-- T8 (Mai) -->

- **What the result means.** A planet's orbital period and its host star carry real information about whether the planet lies above or below ~2 R⊕ — enough to lift average precision 3–4× above chance, but far from a reliable classifier. This is consistent with known trends (short-period giant planets in transit surveys, small planets being more common around cool, low-mass stars), but this analysis does not test any mechanism.
- **Why the signal is uneven.** The gap between measured and unverifiable rows is most likely a sample effect, not leakage: the main model does not use mass. Measured masses come mostly from radial-velocity follow-up, which favors bright stars and massive planets; the unverifiable rows come from an older catalog release with different detection biases. The models learn properties of *this catalog*; the numbers should not be read as properties of the planet population.
- **Limitations.** Unknown exact origin of the data and an outdated catalog version; only 86 small planets; no hyperparameter tuning; the label encodes size, not composition; the mass sensitivity run is exploratory.
- **What changed from the original project.** The original notebook already excluded `radius`, but it kept `mass` (4 of its values are derived from radius and 383 cannot be verified), evaluated each model on a single stratified 80/20 split (about 17 small planets in the test set) without grouping planets by system, and named the classes "terrestrial" and "gas giant". Its best result, F1 = 0.72 for the minority class (Random Forest), depended on `mass`; without it and with grouped, repeated cross-validation, F1 for `small` is 0.38–0.47.

## Authorship

<!-- T9 -->

Model and date of each agent task: the model recorded in the Claude Code session transcripts of the task (for T1, the `Co-Authored-By` trailer of its commit) and the local date of the task commit.

| Part | Authorship | Evidence |
|---|---|---|
| Decisions (T0, T4, T4b, T5) and acceptance of the results | Mai | `docs/bitacora.md`, `docs/decisiones.md` |
| Commits b316a47 and 1f2e02f (original project: notebook, README, `exoplanets_clean.csv`) | Mai, con asistencia de Claude Sonnet 5 (trailer Co-Authored-By), 2026-09-19 | `git show -s b316a47 1f2e02f` |
| Data: `data/raw/exoplanets_clean.csv` | Bytes from commit b316a47 (row above); exact origin unknown | `data/raw/SHA256SUMS` |
| Data: move to `data/raw/` and `SHA256SUMS` (T2) | agente: Claude Code, rol Implementador, claude-opus-5-5, 2026-10-13 | 94fb11b |
| Data: `data/raw/pscomppars_provenance_2026-10-13.csv` (T3) | agente: Claude Code, rol Especialista, claude-opus-5-5, 2026-10-13 | 19605bb |
| Data: `data/processed/lineage.csv` (T1; `hostname` from T3) | agente: Claude Code, rol Especialista, claude-opus-5-5, 2026-10-02 (T1) and 2026-10-13 (T3) | 8c93eb2, 19605bb |
| Data: `data/processed/mass_provenance.csv` (T3b and its re-run) | agente: Claude Code, rol Especialista, claude-opus-5-5, 2026-10-13 and 2026-10-15 | 43a9b14, 1617f94 |
| Notebook §1, §3, §7, §12, §13 (code from the original notebook, adapted to T4, T4b and T5) | Original: commits b316a47 and 1f2e02f; adaptation: agente: Claude Code, rol Implementador, claude-opus-5-5, 2026-10-18 | 93fc459 |
| Notebook §2, §4–§6, §8–§11, §14 (written or rewritten in T7) | agente: Claude Code, rol Implementador, claude-opus-5-5, 2026-10-18 | 93fc459 |
| Notebook §10, cell `readme-tables` (T9) | agente: Claude Code, rol Implementador, claude-opus-5-5, 2026-10-21 | 922540b |
| `tests/` and `reports/pruebas_v1.md` (T6) | agente: Claude Code, rol Tester, claude-opus-5-5, 2026-10-18 | dd284e2, tag `pruebas-1` |
| README: opening paragraph, Reproduce, section layout, main results table, Files (T7) | agente: Claude Code, rol Implementador, claude-opus-5-5, 2026-10-18 | 93fc459 |
| README: Question and label, Data and lineage, Leakage verdicts, Method, interpretation of the results, Discussion (T8) | Mai (texto editado y aprobado por Mai a partir de un borrador de Claude, 2026-10-21) | f2cc43a |
| README: comparison and sensitivity tables, Authorship layout (T9; assignments by Mai) | agente: Claude Code, rol Implementador, claude-opus-5-5, 2026-10-21 | 922540b, `docs/decisiones.md` (T9) |
| `reports/ataque_v1.md` (T10) | pendiente | — |
| `reports/veredicto_v1.md` (T11) | pendiente | — |

- **AI assistance**, under a documented role-based workflow: Claude Code (Anthropic) for planning, tests, implementation and verification; Gemini (Antigravity CLI) as red team; ChatGPT for brief critique. Agent outputs were reviewed and accepted by Mai (GitHub @maimai28); all decisions are recorded in `docs/decisiones.md`.
- **Data:** NASA Exoplanet Archive, *PSCompPars* (older release). Mass–radius relation: Chen & Kipping (2017).

## Files

- `classification.ipynb` — the whole analysis; writes every output of the
  contract.
- `data/raw/` — input data (immutable) and `SHA256SUMS`.
- `data/processed/` — lineage, mass provenance and the notebook outputs.
- `docs/` — brief, plan, decisions and log (in Spanish).
- `tests/` — pytest suite for the success criteria of `docs/brief.md`.
- `pyproject.toml`, `uv.lock` — dependencies; `uv.lock` is the source of
  truth (`requirements.txt` is not).

# Exoplanet Classification: Terrestrial vs. Gas Giant

Binary classification of exoplanets into `terrestrial` or `gas_giant` from
five bulk and stellar host parameters, using `exoplanets_clean.csv` (623
planets, no missing values).

## Data

| Column | Description | Used as feature? |
|---|---|---|
| `mass` | Planet mass (Jupiter masses) | yes |
| `radius` | Planet radius (Jupiter radii) | **no — see below** |
| `orbital_period` | Orbital period (days) | yes |
| `star_mass` | Host star mass (solar masses) | yes |
| `star_radius` | Host star radius (solar radii) | yes |
| `star_teff` | Host star effective temperature (K) | yes |
| `planet_type` | Target: `terrestrial` or `gas_giant` | target |

### Why `radius` is excluded (data leakage)

`radius` almost perfectly separates the two classes on its own: the
largest terrestrial planet in the data has `radius = 0.178000` (Jupiter
radii), the smallest gas giant has `radius = 0.178428` — a gap of
**0.000428**. That boundary sits right at the ~1.5–2 R⊕ "radius valley"
astronomers use to distinguish rocky planets from gas-rich ones, which is
strong evidence that `planet_type` in this cleaned dataset was itself
*generated* from a `radius` threshold rather than being an independent,
observationally-derived label.

That makes `radius` a **leaked feature**: a model trained on it isn't
learning a relationship between planetary/stellar parameters and
composition, it's recovering the threshold rule used to build the label —
something an unseen, non-thresholded catalog wouldn't hand it for free. So
`radius` is dropped from `FEATURES`, and the notebook includes a cell that
reproduces the gap above before training on the remaining five columns:
`mass`, `orbital_period`, `star_mass`, `star_radius`, `star_teff`.

## Class imbalance

The target is dominated by gas giants — **537 gas giants (86.2%) vs. 86
terrestrial planets (13.8%)**. This is a known detection-bias artifact:
large planets on short orbits produce a bigger transit signal and a bigger
radial-velocity wobble, so ground- and space-based surveys find them far
more easily than small terrestrial planets. The imbalance reflects survey
sensitivity, not the true occurrence rate of planet types.

Two choices in the notebook address this directly:

1. **Stratified 80/20 split** — `train_test_split(..., stratify=y)` keeps
   the ~86/14 ratio identical in train and test, so the test set stays
   representative instead of randomly skewing further.
2. **`class_weight='balanced'`** on Logistic Regression and SVM (and on
   Random Forest, where it's equally supported) — reweights each class
   inversely to its frequency during training, so the ~6.2:1 majority
   doesn't dominate the loss.

With imbalance this size, **accuracy alone is a misleading metric**: a
classifier that always predicts `gas_giant` scores ~86% accuracy while
finding zero terrestrial planets. The notebook reports precision, recall,
and F1 **for the `terrestrial` class specifically**, since detecting the
minority class is the actually interesting task.

## Methodology

1. Load and inspect `exoplanets_clean.csv` (shape, dtypes, missing-value
   check, class counts).
2. Check and exclude `radius` as a leaked feature (see above), leaving
   `mass`, `orbital_period`, `star_mass`, `star_radius`, `star_teff`.
3. Stratified 80/20 train/test split (498 / 125 rows), `random_state=42`.
4. Three classifiers, each with `class_weight='balanced'`:
   - **Logistic Regression** — `StandardScaler` + `LogisticRegression`, in a
     `Pipeline` (scale-sensitive).
   - **Random Forest** — `RandomForestClassifier(n_estimators=300)`, trained
     on raw features (scale-invariant).
   - **SVM (RBF kernel)** — `StandardScaler` + `SVC`, in a `Pipeline`
     (scale-sensitive).
   Scaling is fit on the training split only, inside each `Pipeline`, so no
   test-set information leaks into the transform.
5. Evaluate on the held-out test set: accuracy, and precision/recall/F1 for
   the `terrestrial` class, plus a full `classification_report` and
   confusion matrix per model.
6. Compare all three models in a table and a grouped bar chart.

## Results

Without `radius`, scores drop substantially across all three models — this
is the expected, honest result once the leaked feature is gone:

| Model | Accuracy | Precision (terrestrial) | Recall (terrestrial) | F1 (terrestrial) |
|---|---|---|---|---|
| Logistic Regression | 0.720 | 0.275 | 0.647 | 0.386 |
| Random Forest | 0.912 | 0.636 | 0.824 | 0.718 |
| SVM (RBF) | 0.784 | 0.292 | 0.412 | 0.341 |

(For reference, training with `radius` included — the leaky version —
gave Random Forest a literal 1.000 on every metric, and pushed Logistic
Regression/SVM to 0.896/0.864 accuracy. Those numbers were an artifact of
`radius` encoding the label-generation threshold, not a real signal; they
are not reproducible on data that doesn't share that construction.)

**Random Forest is still the best model, but no longer trivially perfect** —
0.912 accuracy, 0.718 F1 on the minority class. Without the single
near-deterministic feature to split on, it has to combine `mass`,
`orbital_period`, and the three stellar parameters, and it does that
better than the other two: mass and orbital period alone carry real
information about planet type (short-period, low-mass rocky planets vs.
longer-period, higher-mass giants), just not a clean single-feature
threshold.

**Logistic Regression and SVM both struggle more here** (F1 = 0.386 and
0.341) than Random Forest. `class_weight='balanced'` still shifts their
decision boundaries toward recall — both catch more terrestrial planets
than they'd get by chance (0.647 and 0.412 recall) — but at much lower
precision (0.275, 0.292) than before, because without `radius` the classes
are no longer close to linearly separable, and a linear/RBF boundary in
the remaining five features overlaps the two classes considerably more
than a tree's axis-aligned splits do.

**Takeaway:** the pre-fix numbers were measuring how easily a model could
recover a threshold rule, not how well it classifies exoplanets from
physically independent parameters. The post-fix numbers are the honest
baseline for this feature set — Random Forest is the model to build on,
and there's real headroom left (0.636 precision on the minority class
means over a third of its "terrestrial" predictions are false positives),
which a leakage-free result should show.

## Setup

```bash
uv sync
uv run jupyter lab classification.ipynb
```

Or with plain `pip`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab classification.ipynb
```

## Files

- `classification.ipynb` — full analysis: EDA, leakage check, split, three
  models, metrics, confusion matrices, comparison.
- `exoplanets_clean.csv` — source data.
- `requirements.txt` — dependencies (unpinned, Python 3.14-compatible).
- `pyproject.toml` — `uv` project file.

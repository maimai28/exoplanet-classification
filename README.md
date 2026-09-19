# Exoplanet Classification: Terrestrial vs. Gas Giant

Binary classification of exoplanets into `terrestrial` or `gas_giant` from
six bulk and stellar host parameters, using `exoplanets_clean.csv` (623
planets, no missing values).

## Data

| Column | Description |
|---|---|
| `mass` | Planet mass (Jupiter masses) |
| `radius` | Planet radius (Jupiter radii) |
| `orbital_period` | Orbital period (days) |
| `star_mass` | Host star mass (solar masses) |
| `star_radius` | Host star radius (solar radii) |
| `star_teff` | Host star effective temperature (K) |
| `planet_type` | Target: `terrestrial` or `gas_giant` |

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
2. Stratified 80/20 train/test split (498 / 125 rows), `random_state=42`.
3. Three classifiers, each with `class_weight='balanced'`:
   - **Logistic Regression** — `StandardScaler` + `LogisticRegression`, in a
     `Pipeline` (scale-sensitive).
   - **Random Forest** — `RandomForestClassifier(n_estimators=300)`, trained
     on raw features (scale-invariant).
   - **SVM (RBF kernel)** — `StandardScaler` + `SVC`, in a `Pipeline`
     (scale-sensitive).
   Scaling is fit on the training split only, inside each `Pipeline`, so no
   test-set information leaks into the transform.
4. Evaluate on the held-out test set: accuracy, and precision/recall/F1 for
   the `terrestrial` class, plus a full `classification_report` and
   confusion matrix per model.
5. Compare all three models in a table and a grouped bar chart.

## Results

| Model | Accuracy | Precision (terrestrial) | Recall (terrestrial) | F1 (terrestrial) |
|---|---|---|---|---|
| Logistic Regression | 0.896 | 0.567 | 1.000 | 0.723 |
| Random Forest | 1.000 | 1.000 | 1.000 | 1.000 |
| SVM (RBF) | 0.864 | 0.500 | 1.000 | 0.667 |

**Random Forest's perfect score is a property of this dataset, not a
generalization claim.** `radius` alone almost perfectly separates the two
classes: the largest terrestrial planet in the data has `radius = 0.178`
(Jupiter radii), the smallest gas giant has `radius = 0.1784` — a gap of
less than 0.001. That boundary sits right at the observed ~1.5–2 R⊕
"radius valley" astronomers use to distinguish rocky planets from
gas-rich ones, which strongly suggests `planet_type` in this cleaned
dataset was itself generated from a radius (and/or mass) threshold. A
tree-based model finds and exploits that single-feature split trivially,
so 1.000 here reflects a near-deterministic label rule, not evidence that
Random Forest would generalize this well on a raw, un-thresholded
observational catalog.

Logistic Regression and SVM don't reach 1.000 because their decision
boundaries (linear, and RBF in scaled multi-feature space) don't isolate
that single threshold as cleanly — and `class_weight='balanced'` pushes
both of them to **100% recall on `terrestrial` at the cost of precision**
(0.567 and 0.500): they over-predict the minority class near the boundary,
catching every real terrestrial planet but also flagging some borderline
gas giants as terrestrial. This is the expected trade-off from balanced
class weights, not a bug.

**Takeaway:** on this dataset, `radius` is close to a sufficient statistic
for `planet_type`. Random Forest's F1 = 1.000 should be read as "the
classes are nearly linearly separable in this feature," not as a
benchmark result — the more informative comparison is Logistic Regression
vs. SVM, where both trade precision for recall in the same direction once
`class_weight='balanced'` is applied.

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

- `classification.ipynb` — full analysis: EDA, split, three models, metrics,
  confusion matrices, comparison.
- `exoplanets_clean.csv` — source data.
- `requirements.txt` — dependencies (unpinned, Python 3.14-compatible).
- `pyproject.toml` — `uv` project file.

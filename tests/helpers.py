"""Shared paths, contract constants and loaders for the T6 tests.

Source of truth: docs/brief.md (success criteria) and the "Contrato de interfaz"
of docs/plan.md. Every loader asserts that its file exists, so a missing
contract output fails the test with a message naming the file and its owner.

Convention: `row_id` is the 0-based row position in data/raw/exoplanets_clean.csv
(as in lineage.csv and mass_provenance.csv, written by T1 and T3b).
"""

import ast
import json
from collections import defaultdict
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
RAW_CSV = RAW_DIR / "exoplanets_clean.csv"
PROCESSED = ROOT / "data" / "processed"
NOTEBOOK = ROOT / "classification.ipynb"
README = ROOT / "README.md"

RUN_COMMAND = (
    "uv run jupyter nbconvert --to notebook --execute classification.ipynb "
    "--output /tmp/run.ipynb"
)

N_ROWS = 623
N_MEASURED = 236
REPEATS = tuple(range(5))
FOLDS = tuple(range(5))

# Model keys in the contract order (used for comparison pairs "A vs B").
MODELS = ("Logistic Regression", "Random Forest", "SVM (RBF)", "Baseline (prior)")
BASELINE = "Baseline (prior)"
SVM = "SVM (RBF)"
METRICS = (
    "accuracy",
    "average_precision_small",
    "balanced_accuracy",
    "f1_small",
    "precision_small",
    "recall_small",
    "roc_auc",
)
RUNS = ("main", "sens_without_mass", "sens_with_mass")
SENS_RUNS = ("sens_without_mass", "sens_with_mass")
PROVENANCE_CATEGORIES = ("measured", "derived", "unverifiable")
FEATURE_COLUMNS = (
    "orbital_period",
    "star_mass",
    "star_radius",
    "star_teff",
    "mass",
    "radius",
)

# Outputs that the contract assigns to T7 (brief, criterion 1).
T7_OUTPUTS = (
    "labels.csv",
    "features.json",
    "folds.csv",
    "folds_sensitivity.csv",
    "predictions.csv",
    "metrics_by_fold.csv",
    "metrics.json",
    "metrics_sensitivity.json",
    "metrics_by_mass_provenance.json",
    "comparisons.json",
    "grouping_report.json",
)

# Files on disk carry 6 decimals; a value recomputed from rounded inputs may
# land on the other side of a rounding boundary, hence one unit of slack.
ROUND_TOL = 1e-6 + 1e-9


def require(path: Path, owner: str) -> Path:
    assert path.is_file(), f"{path.relative_to(ROOT)} does not exist (owner: {owner})"
    return path


def read_csv_str(path: Path, owner: str) -> pd.DataFrame:
    """Read a CSV keeping every cell as its literal text ('' for empty)."""
    require(path, owner)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def read_json(path: Path, owner: str):
    require(path, owner)
    return json.loads(path.read_text(encoding="utf-8"))


def processed(name: str) -> Path:
    return PROCESSED / name


def close6(expected, actual) -> bool:
    """Equality at 6 decimals; None (JSON null) only matches None."""
    if expected is None or actual is None:
        return expected is None and actual is None
    if isinstance(actual, float) and np.isnan(actual):
        return isinstance(expected, float) and np.isnan(expected)
    return abs(float(expected) - float(actual)) <= ROUND_TOL


def is_sorted(df: pd.DataFrame, key: list[str]) -> bool:
    """Ascending order by `key`: ints numerically, strings lexicographically."""
    rows = list(df[key].itertuples(index=False, name=None))
    return rows == sorted(rows)


# --------------------------------------------------------------------------
# Inputs that already exist (T1, T2, T3b)
# --------------------------------------------------------------------------


@cache
def _raw() -> pd.DataFrame:
    df = read_csv_str(RAW_CSV, "T2")
    df.insert(0, "row_id", range(len(df)))
    return df


def raw() -> pd.DataFrame:
    return _raw().copy()


@cache
def _lineage() -> pd.DataFrame:
    df = read_csv_str(processed("lineage.csv"), "T1/T3")
    df["row_id"] = df["row_id"].astype(int)
    return df


def lineage() -> pd.DataFrame:
    return _lineage().copy()


@cache
def _mass_provenance() -> pd.DataFrame:
    df = read_csv_str(processed("mass_provenance.csv"), "T3b")
    df["row_id"] = df["row_id"].astype(int)
    return df


def mass_provenance() -> pd.DataFrame:
    return _mass_provenance().copy()


def measured_row_ids() -> list[int]:
    mp = mass_provenance()
    return sorted(mp.loc[mp["mass_provenance"] == "measured", "row_id"].tolist())


def provenance_by_row() -> dict[int, str]:
    mp = mass_provenance()
    return dict(zip(mp["row_id"], mp["mass_provenance"]))


@cache
def expected_group_ids() -> dict[int, str]:
    """Criterion 13: connected components over shared hostname or exact tuple."""
    r = raw()
    lin = lineage().set_index("row_id")
    assert sorted(lin.index) == list(range(N_ROWS)), "lineage.csv row_id != 0..622"
    parent = list(range(N_ROWS))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union_all(members: list[int]) -> None:
        for other in members[1:]:
            a, b = find(members[0]), find(other)
            if a != b:
                parent[max(a, b)] = min(a, b)

    by_hostname = defaultdict(list)
    by_tuple = defaultdict(list)
    for row_id, sm, sr, st in zip(
        r["row_id"], r["star_mass"], r["star_radius"], r["star_teff"]
    ):
        hostname = lin.at[row_id, "hostname"]
        if hostname:
            by_hostname[hostname].append(row_id)
        by_tuple[(sm, sr, st)].append(row_id)
    for members in [*by_hostname.values(), *by_tuple.values()]:
        union_all(members)

    root_min = defaultdict(lambda: N_ROWS)
    for i in range(N_ROWS):
        root_min[find(i)] = min(root_min[find(i)], i)
    return {i: f"g:{root_min[find(i)]}" for i in range(N_ROWS)}


# --------------------------------------------------------------------------
# T7 outputs
# --------------------------------------------------------------------------


@cache
def _labels() -> pd.DataFrame:
    df = read_csv_str(processed("labels.csv"), "T7")
    df["row_id"] = df["row_id"].astype(int)
    return df


def labels() -> pd.DataFrame:
    return _labels().copy()


def size_class_by_row() -> dict[int, str]:
    lab = labels()
    return dict(zip(lab["row_id"], lab["size_class"]))


@cache
def _folds(name: str) -> pd.DataFrame:
    df = read_csv_str(processed(name), "T7")
    for col in ("row_id", "repeat", "fold"):
        df[col] = df[col].astype(int)
    return df


def folds(name: str) -> pd.DataFrame:
    return _folds(name).copy()


@cache
def _predictions() -> pd.DataFrame:
    df = read_csv_str(processed("predictions.csv"), "T7")
    for col in ("repeat", "row_id", "fold"):
        df[col] = df[col].astype(int)
    df["score"] = df["score"].astype(float)
    return df


def predictions() -> pd.DataFrame:
    return _predictions().copy()


@cache
def _metrics_by_fold() -> pd.DataFrame:
    df = read_csv_str(processed("metrics_by_fold.csv"), "T7")
    for col in ("repeat", "fold", "n_train", "n_eval", "n_eval_small"):
        df[col] = df[col].astype(int)
    for col in METRICS:
        df[col] = pd.to_numeric(df[col].replace("", np.nan))
    return df


def metrics_by_fold() -> pd.DataFrame:
    return _metrics_by_fold().copy()


def compute_metrics(y_true, score, pred) -> dict:
    """The seven metrics of the contract, positive class `small`.

    AP and ROC-AUC are None (JSON null) when y_true lacks one of the classes;
    P/R/F1 use zero_division=0.
    """
    yt = (np.asarray(y_true) == "small").astype(int)
    yp = (np.asarray(pred) == "small").astype(int)
    s = np.asarray(score, dtype=float)
    both = 0 < yt.sum() < len(yt)
    return {
        "accuracy": accuracy_score(yt, yp),
        "average_precision_small": average_precision_score(yt, s) if both else None,
        "balanced_accuracy": balanced_accuracy_score(yt, yp),
        "f1_small": f1_score(yt, yp, zero_division=0),
        "precision_small": precision_score(yt, yp, zero_division=0),
        "recall_small": recall_score(yt, yp, zero_division=0),
        "roc_auc": roc_auc_score(yt, s) if both else None,
    }


def mean_std(values) -> dict:
    """{"mean", "std"} with ddof=1; None if any value is undefined."""
    if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in values):
        return {"mean": None, "std": None}
    arr = np.asarray(values, dtype=float)
    return {"mean": float(arr.mean()), "std": float(arr.std(ddof=1))}


def summary_from_fold_rows(rows: pd.DataFrame) -> dict:
    """Schema of metrics.json computed from metrics_by_fold.csv rows."""
    out = {}
    for model in MODELS:
        sub = rows[rows["model"] == model]
        out[model] = {m: mean_std(sub[m].tolist()) for m in METRICS}
    return out


def summary_mismatches(expected: dict, actual: dict, where: str) -> list[str]:
    bad = []
    for model, per_metric in expected.items():
        for metric, stats in per_metric.items():
            for stat, value in stats.items():
                got = actual[model][metric][stat]
                if not close6(value, got):
                    bad.append(f"{where}[{model}][{metric}][{stat}]: {got} != {value}")
    return bad


# --------------------------------------------------------------------------
# Notebook (static inspection)
# --------------------------------------------------------------------------


def notebook_code_cells() -> list[str]:
    nb = read_json(NOTEBOOK, "T7")
    cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = cell["source"]
            cells.append("".join(src) if isinstance(src, list) else src)
    return cells


def parse_cell(source: str) -> ast.Module:
    """Parse a code cell, blanking IPython magics and shell escapes."""
    lines = [
        "" if line.lstrip().startswith(("%", "!")) else line
        for line in source.splitlines()
    ]
    return ast.parse("\n".join(lines))

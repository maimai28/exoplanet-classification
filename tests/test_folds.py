"""Brief criteria 5 and 13; contract 'Particiones' (folds*.csv); T6 (c), (d), (j)."""

import re

import numpy as np
import pytest
from helpers import (
    FOLDS,
    N_MEASURED,
    N_ROWS,
    REPEATS,
    expected_group_ids,
    folds,
    is_sorted,
    measured_row_ids,
    processed,
    read_csv_str,
    size_class_by_row,
)
from sklearn.model_selection import StratifiedGroupKFold

FOLD_FILES = {
    "folds.csv": lambda: list(range(N_ROWS)),
    "folds_sensitivity.csv": measured_row_ids,
}
EXPECTED_LINES = {"folds.csv": N_ROWS * 5, "folds_sensitivity.csv": N_MEASURED * 5}

per_file = pytest.mark.parametrize("name", list(FOLD_FILES))


def partition(df, repeat: int) -> set[frozenset[int]]:
    sub = df[df["repeat"] == repeat]
    return {frozenset(g["row_id"]) for _, g in sub.groupby("fold")}


@per_file
def test_columns(name):
    """Contract: columns row_id, group_id, repeat, fold."""
    df = read_csv_str(processed(name), "T7")
    assert list(df.columns) == ["row_id", "group_id", "repeat", "fold"]


@per_file
def test_one_line_per_row_and_repeat(name):
    """Contract: one line per (row_id, repeat), ordered by row_id and repeat."""
    df = folds(name)
    assert len(df) == EXPECTED_LINES[name]
    assert not df.duplicated(["row_id", "repeat"]).any()
    assert is_sorted(df, ["row_id", "repeat"])
    population = FOLD_FILES[name]()
    for repeat in REPEATS:
        assert sorted(df.loc[df["repeat"] == repeat, "row_id"]) == population
    assert set(df["repeat"]) == set(REPEATS)
    assert set(df["fold"]) == set(FOLDS)


def test_sensitivity_rows_are_exactly_measured():
    """Criterion 4 / T6 (d): folds_sensitivity.csv covers exactly `measured`."""
    df = folds("folds_sensitivity.csv")
    assert sorted(set(df["row_id"])) == measured_row_ids()


@per_file
def test_group_id_format(name):
    """Criterion 13: group_id = 'g:<row_id mínimo de la componente>'."""
    df = folds(name)
    assert df["group_id"].map(lambda g: bool(re.fullmatch(r"g:\d+", g))).all()
    assert (df.groupby("row_id")["group_id"].nunique() == 1).all()


@per_file
def test_group_id_equals_connected_components(name):
    """Criterion 13: partition by group_id = components (neither coarser nor finer)."""
    df = folds(name).drop_duplicates("row_id")
    expected = expected_group_ids()
    wrong = [
        (r, g, expected[r])
        for r, g in zip(df["row_id"], df["group_id"])
        if g != expected[r]
    ]
    assert not wrong, f"(row_id, group_id, expected): {wrong[:10]}"


@per_file
def test_no_group_split_across_folds(name):
    """Criterion 5: no system in train and eval of the same partition."""
    df = folds(name)
    per_group = df.groupby(["repeat", "group_id"])["fold"].nunique()
    split = per_group[per_group > 1]
    assert split.empty, f"split groups: {split.index.tolist()[:10]}"


@per_file
def test_every_fold_has_a_small(name):
    """T6 (c): at least one `small` in each (repeat, fold)."""
    df = folds(name)
    size = size_class_by_row()
    df["small"] = df["row_id"].map(size) == "small"
    per_fold = df.groupby(["repeat", "fold"])["small"].sum()
    assert len(per_fold) == len(REPEATS) * len(FOLDS)
    assert (per_fold >= 1).all(), per_fold[per_fold < 1].index.tolist()


@per_file
def test_folds_reproduce_stratified_group_kfold(name):
    """Contract: StratifiedGroupKFold(5, shuffle=True, random_state=repeat),
    y = size_class, groups = group_id, rows ordered by row_id.

    Compared as partitions, so the numbering of folds is not constrained.
    """
    df = folds(name)
    size = size_class_by_row()
    for repeat in REPEATS:
        sub = df[df["repeat"] == repeat].sort_values("row_id")
        row_ids = sub["row_id"].to_numpy()
        y = sub["row_id"].map(size).to_numpy()
        groups = sub["group_id"].to_numpy()
        splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=repeat)
        expected = {
            frozenset(row_ids[test].tolist())
            for _, test in splitter.split(np.zeros((len(sub), 1)), y, groups)
        }
        assert partition(df, repeat) == expected, f"repeat {repeat}"

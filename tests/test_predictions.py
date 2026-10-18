"""Contract 'Predicciones fuera de fold' (predictions.csv); brief criteria 4 and 6."""

import numpy as np
from helpers import (
    BASELINE,
    MODELS,
    N_MEASURED,
    N_ROWS,
    REPEATS,
    ROUND_TOL,
    RUNS,
    SENS_RUNS,
    SVM,
    folds,
    is_sorted,
    measured_row_ids,
    predictions,
    processed,
    read_csv_str,
)

COLUMNS = ["run", "model", "repeat", "row_id", "fold", "score", "pred"]
KEY = ["run", "model", "repeat", "row_id"]


def test_columns():
    """Contract: run, model, repeat, row_id, fold, score, pred."""
    df = read_csv_str(processed("predictions.csv"), "T7")
    assert list(df.columns) == COLUMNS


def test_runs_models_and_row_count():
    """Contract: three runs, four models, five repeats, one line per key."""
    df = predictions()
    assert set(df["run"]) == set(RUNS)
    assert set(df["model"]) == set(MODELS)
    assert set(df["repeat"]) == set(REPEATS)
    expected = 4 * 5 * N_ROWS + 2 * 4 * 5 * N_MEASURED
    assert len(df) == expected
    assert not df.duplicated(KEY).any(), "a (run, model, repeat, row_id) repeats"


def test_sorted_by_key():
    """Contract: ordered by run, model, repeat, row_id (strings lexicographic)."""
    assert is_sorted(predictions(), KEY)


def test_main_run_covers_all_rows():
    """Contract: run main uses the 623 rows."""
    df = predictions()
    main = df[df["run"] == "main"]
    for (model, repeat), sub in main.groupby(["model", "repeat"]):
        assert sorted(sub["row_id"]) == list(range(N_ROWS)), (model, repeat)


def test_sensitivity_runs_use_exactly_measured_rows():
    """Criterion 4 / T6 (d): sens_* runs use exactly the `measured` rows."""
    df = predictions()
    measured = measured_row_ids()
    for run in SENS_RUNS:
        sub_run = df[df["run"] == run]
        for (model, repeat), sub in sub_run.groupby(["model", "repeat"]):
            assert sorted(sub["row_id"]) == measured, (run, model, repeat)


def test_fold_matches_fold_files():
    """Contract: main uses folds.csv; sens_* use folds_sensitivity.csv."""
    df = predictions()
    for runs, name in ((["main"], "folds.csv"), (SENS_RUNS, "folds_sensitivity.csv")):
        assigned = folds(name).set_index(["row_id", "repeat"])["fold"]
        sub = df[df["run"].isin(runs)]
        expected = assigned.reindex(list(zip(sub["row_id"], sub["repeat"]))).to_numpy()
        assert (sub["fold"].to_numpy() == expected).all(), name


def test_pred_domain():
    """Contract: pred ∈ {small, large}."""
    assert set(predictions()["pred"]) <= {"small", "large"}


def test_pred_is_default_threshold_of_score():
    """Contract 'Predicción': predict() = proba > 0.5; SVM: decision_function > 0.

    Scores within one rounding unit of the threshold are not judged.
    """
    df = predictions()
    threshold = np.where(df["model"] == SVM, 0.0, 0.5)
    margin = df["score"].to_numpy() - threshold
    decided = np.abs(margin) > ROUND_TOL
    expected = np.where(margin > 0, "small", "large")
    wrong = df[decided & (df["pred"].to_numpy() != expected)]
    assert wrong.empty, wrong.head(10).to_string()


def test_probability_scores_in_unit_interval():
    """Contract 'Score': predict_proba[:, small] for LR, RF and the baseline."""
    df = predictions()
    proba = df[df["model"] != SVM]["score"]
    assert ((proba >= 0) & (proba <= 1)).all()


def test_baseline_score_is_constant_within_a_fold():
    """Contract: Baseline (prior) = DummyClassifier(strategy='prior')."""
    df = predictions()
    base = df[df["model"] == BASELINE]
    per_fold = base.groupby(["run", "repeat", "fold"])["score"].nunique()
    assert (per_fold == 1).all()

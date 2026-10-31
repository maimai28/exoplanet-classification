"""Brief criteria 4 and 6; contract 'Métricas' files; T6 (e), (f), (h), (i).

Recomputations use the values as written on disk (6 decimals), because the
contract says each file is computed from the previous one.
"""

from helpers import (
    BASELINE,
    FOLDS,
    METRICS,
    MODELS,
    N_MEASURED,
    PROVENANCE_CATEGORIES,
    REPEATS,
    RUNS,
    close6,
    compute_metrics,
    mass_provenance,
    mean_std,
    measured_row_ids,
    metrics_by_fold,
    predictions,
    processed,
    read_csv_str,
    read_json,
    size_class_by_row,
    summary_from_fold_rows,
    summary_mismatches,
)

FOLD_COLUMNS = [
    "run",
    "model",
    "repeat",
    "fold",
    "n_train",
    "n_eval",
    "n_eval_small",
    *METRICS,
]
POPULATION = {
    "main": 623,
    "sens_without_mass": N_MEASURED,
    "sens_with_mass": N_MEASURED,
}


def test_metrics_by_fold_columns():
    """Contract 'Métricas por fold': listed columns."""
    df = read_csv_str(processed("metrics_by_fold.csv"), "T7")
    assert list(df.columns) == FOLD_COLUMNS


def test_metrics_by_fold_grid_and_order():
    """Contract: one row per (run, model, repeat, fold), ordered by that key."""
    df = metrics_by_fold()
    assert len(df) == len(RUNS) * len(MODELS) * 25
    keys = set(zip(df["run"], df["model"], df["repeat"], df["fold"]))
    expected = {
        (r, m, i, f) for r in RUNS for m in MODELS for i in REPEATS for f in FOLDS
    }
    assert keys == expected
    rows = list(zip(df["run"], df["model"], df["repeat"], df["fold"]))
    assert rows == sorted(rows)


def test_metrics_by_fold_recomputed_from_predictions():
    """Contract / T6 (e): counts and seven metrics recomputed from predictions.csv."""
    size = size_class_by_row()
    preds = predictions()
    preds["y"] = preds["row_id"].map(size)
    grouped = dict(list(preds.groupby(["run", "model", "repeat", "fold"])))
    bad = []
    for row in metrics_by_fold().itertuples(index=False):
        key = (row.run, row.model, row.repeat, row.fold)
        sub = grouped.get(key)
        if sub is None:
            bad.append(f"{key}: no predictions")
            continue
        n_eval = len(sub)
        expected = {
            "n_eval": n_eval,
            "n_train": POPULATION[row.run] - n_eval,
            "n_eval_small": int((sub["y"] == "small").sum()),
            **compute_metrics(sub["y"], sub["score"], sub["pred"]),
        }
        for col, value in expected.items():
            if not close6(value, getattr(row, col)):
                bad.append(f"{key} {col}: {getattr(row, col)} != {value}")
    assert not bad, "\n".join(bad[:15])


def test_baseline_sanity():
    """T6 (f): baseline AP = prevalence of small, ROC-AUC = 0.5, bal. acc. = 0.5."""
    df = metrics_by_fold()
    base = df[df["model"] == BASELINE]
    assert len(base) == len(RUNS) * 25
    for row in base.itertuples(index=False):
        key = (row.run, row.repeat, row.fold)
        assert close6(row.n_eval_small / row.n_eval, row.average_precision_small), key
        assert close6(0.5, row.roc_auc), key
        assert close6(0.5, row.balanced_accuracy), key


def assert_summary_schema(summary: dict, where: str) -> None:
    assert set(summary) == set(MODELS), f"{where}: models {sorted(summary)}"
    for model, per_metric in summary.items():
        assert set(per_metric) == set(METRICS), f"{where}[{model}]"
        for metric, stats in per_metric.items():
            assert set(stats) == {"mean", "std"}, f"{where}[{model}][{metric}]"


def test_metrics_json_schema():
    """Criterion 6: exactly the four models and the seven metrics, mean/std."""
    assert_summary_schema(read_json(processed("metrics.json"), "T7"), "metrics.json")


def test_metrics_json_recomputed_from_metrics_by_fold():
    """Criterion 6 / T6 (e): mean and std (ddof=1) over the 25 main rows."""
    metrics = read_json(processed("metrics.json"), "T7")
    df = metrics_by_fold()
    main = df[df["run"] == "main"]
    assert (main.groupby("model").size() == 25).all()
    bad = summary_mismatches(summary_from_fold_rows(main), metrics, "metrics.json")
    assert not bad, "\n".join(bad[:15])


def load_sensitivity() -> dict:
    return read_json(processed("metrics_sensitivity.json"), "T7")


def test_metrics_sensitivity_keys_and_counts():
    """Contract: exact keys; row_filter; n = count of measured; n_small."""
    sens = load_sensitivity()
    assert set(sens) == {
        "row_filter",
        "n",
        "n_small",
        "exploratory",
        "without_mass",
        "with_mass",
    }
    assert sens["row_filter"] == "mass_provenance == measured"
    measured = measured_row_ids()
    size = size_class_by_row()
    assert type(sens["n"]) is int and sens["n"] == len(measured)
    assert type(sens["n_small"]) is int
    assert sens["n_small"] == sum(size[i] == "small" for i in measured)


def test_exploratory_flag_follows_n_small():
    """T6 (h): exploratory = n_small < 25 (T5)."""
    sens = load_sensitivity()
    assert type(sens["exploratory"]) is bool
    assert sens["exploratory"] == (sens["n_small"] < 25)


def test_metrics_sensitivity_recomputed_from_metrics_by_fold():
    """Contract / T6 (e): with/without_mass from sens_* rows of metrics_by_fold."""
    sens = load_sensitivity()
    df = metrics_by_fold()
    bad = []
    for key, run in (
        ("without_mass", "sens_without_mass"),
        ("with_mass", "sens_with_mass"),
    ):
        assert_summary_schema(sens[key], key)
        expected = summary_from_fold_rows(df[df["run"] == run])
        bad += summary_mismatches(expected, sens[key], key)
    assert not bad, "\n".join(bad[:15])


def load_by_provenance() -> dict:
    return read_json(processed("metrics_by_mass_provenance.json"), "T7")


def test_metrics_by_mass_provenance_keys_and_n():
    """Criterion 4 / T6 (i): exactly three categories; n = count in mass_provenance."""
    data = load_by_provenance()
    assert set(data) == set(PROVENANCE_CATEGORIES)
    counts = mass_provenance()["mass_provenance"].value_counts()
    for category, entry in data.items():
        assert set(entry) == {"n", "metrics"}, category
        assert type(entry["n"]) is int and entry["n"] == counts[category], category
        assert_summary_schema(entry["metrics"], category)


def test_metrics_by_mass_provenance_recomputed_from_predictions():
    """Contract: run main, one OOF prediction per row and repeat, mean/std over 5."""
    data = load_by_provenance()
    size = size_class_by_row()
    mp = mass_provenance()
    preds = predictions()
    main = preds[preds["run"] == "main"].copy()
    main["y"] = main["row_id"].map(size)
    bad = []
    for category in PROVENANCE_CATEGORIES:
        rows = set(mp.loc[mp["mass_provenance"] == category, "row_id"])
        sub_cat = main[main["row_id"].isin(rows)]
        expected = {}
        for model in MODELS:
            per_repeat = [
                compute_metrics(sub["y"], sub["score"], sub["pred"])
                for _, sub in sub_cat[sub_cat["model"] == model].groupby("repeat")
            ]
            assert len(per_repeat) == len(REPEATS), (category, model)
            expected[model] = {
                m: mean_std([values[m] for values in per_repeat]) for m in METRICS
            }
        bad += summary_mismatches(expected, data[category]["metrics"], category)
    assert not bad, "\n".join(bad[:15])

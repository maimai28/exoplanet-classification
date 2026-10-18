"""Brief criterion 6 and contract 'Comparaciones' (comparisons.json); T6 (g).

Nadeau and Bengio (2003) corrected resampled t-test, recomputed from
metrics_by_fold.csv.
"""

from itertools import combinations

import numpy as np
from helpers import MODELS, close6, metrics_by_fold, processed, read_json
from scipy import stats

PAIRS = [f"{a} vs {b}" for a, b in combinations(MODELS, 2)]
FIELDS = {"metric", "mean_diff", "t", "df", "p_value", "test_train_ratio"}
J = 25


def load_comparisons() -> dict:
    return read_json(processed("comparisons.json"), "T7")


def expected_pair(df, a: str, b: str) -> dict:
    metric = "average_precision_small"
    rows_a = df[df["model"] == a].set_index(["repeat", "fold"]).sort_index()
    rows_b = df[df["model"] == b].set_index(["repeat", "fold"]).sort_index()
    assert len(rows_a) == len(rows_b) == J
    assert (rows_a[["n_train", "n_eval"]] == rows_b[["n_train", "n_eval"]]).all().all()
    d = (rows_a[metric] - rows_b[metric]).to_numpy()
    rho = float(np.mean(rows_a["n_eval"] / rows_a["n_train"]))
    t = d.mean() / np.sqrt((1 / J + rho) * d.var(ddof=1))
    return {
        "mean_diff": float(d.mean()),
        "t": float(t),
        "p_value": float(2 * stats.t.sf(abs(t), J - 1)),
        "test_train_ratio": rho,
    }


def test_top_level_keys_follow_exploratory():
    """Contract: 'main' always; 'sensitivity' only if exploratory is false."""
    comparisons = load_comparisons()
    sens = read_json(processed("metrics_sensitivity.json"), "T7")
    expected = {"main"} if sens["exploratory"] else {"main", "sensitivity"}
    assert set(comparisons) == expected


def test_main_has_the_six_pairs_in_contract_order():
    """Contract: six pairs 'A vs B', A before B in the contract model order."""
    assert set(load_comparisons()["main"]) == set(PAIRS)


def test_pair_fields():
    """Contract: metric, mean_diff, t, df, p_value, test_train_ratio; df = 24."""
    comparisons = load_comparisons()
    for run, pairs in comparisons.items():
        for name, pair in pairs.items():
            assert FIELDS <= set(pair), (run, name, sorted(FIELDS - set(pair)))
            assert pair["metric"] == "average_precision_small", (run, name)
            assert pair["df"] == J - 1, (run, name)


def test_sensitivity_compares_with_vs_without_mass_per_model():
    """Contract: 'sensitivity', if present, compares with/without mass per model."""
    comparisons = load_comparisons()
    if "sensitivity" in comparisons:
        assert len(comparisons["sensitivity"]) == len(MODELS)
    else:
        sens = read_json(processed("metrics_sensitivity.json"), "T7")
        assert sens["exploratory"] is True


def test_main_pairs_recomputed_from_metrics_by_fold():
    """Criterion 6 / T6 (g): mean_diff, t, p and rho recomputed (6 decimals)."""
    comparisons = load_comparisons()["main"]
    df = metrics_by_fold()
    main = df[df["run"] == "main"]
    bad = []
    for a, b in combinations(MODELS, 2):
        name = f"{a} vs {b}"
        for field, value in expected_pair(main, a, b).items():
            got = comparisons[name][field]
            if not close6(value, got):
                bad.append(f"{name} {field}: {got} != {value}")
    assert not bad, "\n".join(bad)

"""Contract 'Formato determinista' (what makes criterion 1 byte-comparable).

JSON: sort_keys, indent=2, UTF-8, final newline, floats with 6 fixed decimals,
undefined metrics as null. CSV: floats with 6 decimals (order is checked in the
test of each file).
"""

import json
import re

import pytest
from helpers import METRICS, T7_OUTPUTS, processed, read_csv_str, require

JSON_OUTPUTS = [name for name in T7_OUTPUTS if name.endswith(".json")]
CSV_FLOAT_COLUMNS = {
    "predictions.csv": ["score"],
    "metrics_by_fold.csv": list(METRICS),
}
CSV_INT_COLUMNS = {
    "labels.csv": ["row_id"],
    "folds.csv": ["row_id", "repeat", "fold"],
    "folds_sensitivity.csv": ["row_id", "repeat", "fold"],
    "predictions.csv": ["repeat", "row_id", "fold"],
    "metrics_by_fold.csv": ["repeat", "fold", "n_train", "n_eval", "n_eval_small"],
}
SIX_DECIMALS = re.compile(r"-?\d+\.\d{6}")
INTEGER = re.compile(r"-?\d+")


def canonical(obj, ensure_ascii: bool, level: int = 0) -> str:
    """Reference serialization of the contract format."""
    pad, end = "  " * (level + 1), "  " * level
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [
            f"{pad}{json.dumps(k, ensure_ascii=ensure_ascii)}: "
            f"{canonical(v, ensure_ascii, level + 1)}"
            for k, v in sorted(obj.items())
        ]
        return "{\n" + ",\n".join(items) + "\n" + end + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        items = [f"{pad}{canonical(v, ensure_ascii, level + 1)}" for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + end + "]"
    if isinstance(obj, float):
        return f"{obj:.6f}"
    return json.dumps(obj, ensure_ascii=ensure_ascii)


@pytest.mark.parametrize("name", JSON_OUTPUTS)
def test_json_deterministic_format(name):
    """Contract: sort_keys, indent=2, UTF-8, final newline, 6 fixed decimals."""
    text = require(processed(name), "T7").read_bytes().decode("utf-8")
    obj = json.loads(text)
    candidates = {canonical(obj, flag) + "\n" for flag in (True, False)}
    assert text in candidates, f"{name} is not in the deterministic format"


@pytest.mark.parametrize("name", list(CSV_FLOAT_COLUMNS))
def test_csv_floats_have_six_decimals(name):
    """Contract: CSV floats with 6 decimals."""
    df = read_csv_str(processed(name), "T7")
    for col in CSV_FLOAT_COLUMNS[name]:
        bad = df.loc[~df[col].str.fullmatch(SIX_DECIMALS.pattern), col]
        assert bad.empty, f"{name}:{col} {bad.head().tolist()}"


@pytest.mark.parametrize("name", list(CSV_INT_COLUMNS))
def test_csv_integer_columns_are_plain_integers(name):
    """Contract: row_id, repeat, fold and counts are integers (no '1.0')."""
    df = read_csv_str(processed(name), "T7")
    for col in CSV_INT_COLUMNS[name]:
        bad = df.loc[~df[col].str.fullmatch(INTEGER.pattern), col]
        assert bad.empty, f"{name}:{col} {bad.head().tolist()}"

"""Brief criterion 4 and contract 'Procedencia de la masa por fila' (T3b)."""

import re

import numpy as np
from helpers import N_ROWS, is_sorted, lineage, mass_provenance, processed, read_csv_str

COLUMNS = [
    "row_id",
    "pl_bmassprov",
    "mass_matches_p1",
    "mr_predicted_mass",
    "mr_rel_residual",
    "mr_status",
    "not_testable_reason",
    "mass_provenance",
]
SIX_DECIMALS = re.compile(r"-?\d+\.\d{6}")


def test_columns_and_rows():
    """Contract: 623 rows ordered by row_id with the eight listed columns."""
    df = read_csv_str(processed("mass_provenance.csv"), "T3b")
    assert list(df.columns) == COLUMNS
    df = mass_provenance()
    assert list(df["row_id"]) == list(range(N_ROWS))
    assert is_sorted(df, ["row_id"])


def test_value_domains():
    """Contract: domains of mass_matches_p1, mr_status, reason and category."""
    df = mass_provenance()
    assert set(df["mass_matches_p1"]) <= {"true", "false", ""}
    assert set(df["mr_status"]) <= {"on_relation", "off_relation", "not_testable"}
    assert set(df["not_testable_reason"]) <= {"gap_11.1_14.3", "low_precision", ""}
    assert set(df["mass_provenance"]) <= {"measured", "derived", "unverifiable"}


def test_not_testable_reason_only_when_not_testable():
    """Contract: reason set iff mr_status = not_testable (criterion 4)."""
    df = mass_provenance()
    has_reason = df["not_testable_reason"] != ""
    assert (has_reason == (df["mr_status"] == "not_testable")).all()


def test_mr_columns_empty_only_in_gap():
    """Contract: mr_predicted_mass / mr_rel_residual empty only for the gap."""
    df = mass_provenance()
    gap = df["not_testable_reason"] == "gap_11.1_14.3"
    for col in ("mr_predicted_mass", "mr_rel_residual"):
        assert ((df[col] == "") == gap).all(), col
        values = df.loc[~gap, col]
        bad = [v for v in values if not SIX_DECIMALS.fullmatch(v)]
        assert not bad, f"{col} not at 6 decimals: {bad[:5]}"


def test_empty_fields_follow_lineage():
    """Contract: pl_bmassprov empty without pl_name; match flag empty w/o pair."""
    mp = mass_provenance().set_index("row_id")
    lin = lineage().set_index("row_id")
    assert ((mp["pl_bmassprov"] == "") == (lin["pl_name"] == "")).all()
    no_pair = lin["match_status"] != "unique"
    assert ((mp["mass_matches_p1"] == "") == no_pair).all()


def test_category_follows_combination_rule():
    """Criterion 4: derived / measured / unverifiable combination rule."""
    df = mass_provenance()
    on_relation = df["mr_status"] == "on_relation"
    matches = df["mass_matches_p1"] == "true"
    derived = on_relation | (matches & (df["pl_bmassprov"] == "M-R relationship"))
    measured = matches & df["pl_bmassprov"].isin(["Mass", "Msini"]) & ~on_relation
    expected = np.select([derived, measured], ["derived", "measured"], "unverifiable")
    wrong = df.loc[expected != df["mass_provenance"], "row_id"].tolist()
    assert not wrong, f"rows misclassified: {wrong[:10]}"

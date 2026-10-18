"""Brief criterion 14 and contract 'Linaje' (data/processed/lineage.csv)."""

from helpers import N_ROWS, is_sorted, lineage, processed, read_csv_str


def test_lineage_columns():
    """Contract 'Linaje': row_id, pl_name, hostname, match_status."""
    df = read_csv_str(processed("lineage.csv"), "T1/T3")
    assert list(df.columns) == ["row_id", "pl_name", "hostname", "match_status"]


def test_each_row_id_appears_once():
    """Criterion 14: 'Cada row_id aparece una sola vez en lineage.csv'."""
    df = lineage()
    assert sorted(df["row_id"]) == list(range(N_ROWS))
    assert is_sorted(df, ["row_id"])


def test_match_status_domain():
    """Criterion 14: match_status ∈ {unique, none, ambiguous}."""
    assert set(lineage()["match_status"]) <= {"unique", "none", "ambiguous"}


def test_unique_matches_are_one_to_one():
    """Criterion 14: 'ningún pl_name se repite entre las filas unique'."""
    df = lineage()
    names = df.loc[df["match_status"] == "unique", "pl_name"]
    assert (names != "").all(), "a 'unique' row has no pl_name"
    duplicated = names[names.duplicated(keep=False)]
    assert duplicated.empty, f"repeated pl_name: {sorted(set(duplicated))}"

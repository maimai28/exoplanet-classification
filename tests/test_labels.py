"""Brief criterion 12 and contract 'Etiqueta (T4b)' (data/processed/labels.csv)."""

from helpers import N_ROWS, is_sorted, labels, processed, raw, read_csv_str

MAPPING = {"terrestrial": "small", "gas_giant": "large"}


def test_labels_columns():
    """Contract: columns row_id, planet_type, size_class."""
    df = read_csv_str(processed("labels.csv"), "T7")
    assert list(df.columns) == ["row_id", "planet_type", "size_class"]


def test_labels_rows_ordered_by_row_id():
    """Contract: '623 filas ordenadas por row_id'."""
    df = labels()
    assert list(df["row_id"]) == list(range(N_ROWS))
    assert is_sorted(df, ["row_id"])


def test_planet_type_copied_verbatim_from_raw():
    """Contract: planet_type 'tal como está en data/raw/'."""
    lab = labels().set_index("row_id")
    src = raw().set_index("row_id")
    assert (lab["planet_type"] == src["planet_type"]).all()


def test_size_class_mapping_on_all_rows():
    """Criterion 12: terrestrial→small, gas_giant→large on the 623 raw rows."""
    lab = labels().set_index("row_id")
    src = raw().set_index("row_id")
    expected = src["planet_type"].map(MAPPING)
    assert expected.notna().all(), "raw planet_type outside the mapping"
    assert (lab["size_class"] == expected).all()

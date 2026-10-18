"""Brief criterion 4 and contract 'Variables del modelo (T4)' (features.json).

Includes T6 (k): static check that the notebook builds X only from the file.
Rule fixed by Mai (2026-10-18): the column-name literals appear only in the
cell that writes features.json, and a later cell reads it back with json.
"""

import ast

from helpers import (
    FEATURE_COLUMNS,
    notebook_code_cells,
    parse_cell,
    processed,
    read_json,
)

MAIN = ["orbital_period", "star_mass", "star_radius", "star_teff"]
SENSITIVITY_MASS = [*MAIN, "mass"]


def load_features() -> dict:
    return read_json(processed("features.json"), "T7")


def test_features_json_matches_contract():
    """Contract: exactly four keys with these values and list orders."""
    assert load_features() == {
        "excluded": {"radius": "etiqueta por umbral (T1)"},
        "main": MAIN,
        "sensitivity_mass": SENSITIVITY_MASS,
        "target": "size_class",
    }


def test_radius_excluded_from_model_inputs():
    """Criterion 4: radius not in main nor sensitivity_mass, and in excluded."""
    features = load_features()
    assert "radius" not in features["main"]
    assert "radius" not in features["sensitivity_mass"]
    assert "radius" in features["excluded"]


def test_mass_only_in_sensitivity():
    """Criterion 4 (T4 verdicts): mass stays out of the main model."""
    features = load_features()
    assert "mass" not in features["main"]
    assert "mass" in features["sensitivity_mass"]


def test_target_is_size_class():
    """Contract / amendment (a): target = size_class, not planet_type."""
    assert load_features()["target"] == "size_class"


def _json_calls(tree: ast.Module, names: set[str]) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in names
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "json"
        for node in ast.walk(tree)
    )


def test_notebook_takes_x_only_from_features_json():
    """Contract: 'El notebook toma las columnas de X solo de este archivo' (k)."""
    sources = notebook_code_cells()
    trees = [parse_cell(src) for src in sources]
    with_names = [
        i
        for i, tree in enumerate(trees)
        if any(
            isinstance(node, ast.Constant) and node.value in FEATURE_COLUMNS
            for node in ast.walk(tree)
        )
    ]
    assert len(with_names) == 1, f"column literals in code cells {with_names}"
    writer = with_names[0]
    assert _json_calls(trees[writer], {"dump", "dumps"}), "writer cell lacks json.dump"
    assert any("features.json" in src for src in sources)
    assert any(_json_calls(tree, {"load", "loads"}) for tree in trees[writer + 1 :]), (
        "no cell after the writer reads features.json back with json.load(s)"
    )

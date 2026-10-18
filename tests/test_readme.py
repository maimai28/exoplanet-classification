"""Brief criterion 7 and contract 'README' (results table between markers).

Rule fixed by Mai (2026-10-18): column headers are the seven metric keys and
the first column holds the four model keys, verbatim (backticks allowed).
"""

import re

from helpers import METRICS, MODELS, README, RUN_COMMAND, processed, read_json, require

START, END = "<!-- metrics:start -->", "<!-- metrics:end -->"
CELL = re.compile(r"(-?\d+\.\d{3})\s*±\s*(\d+\.\d{3})")


def split_row(line: str) -> list[str]:
    return [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]


def results_table() -> tuple[list[str], list[list[str]]]:
    text = require(README, "T9").read_text(encoding="utf-8")
    assert text.count(START) == 1 and text.count(END) == 1, "metrics markers missing"
    block = text.split(START, 1)[1].split(END, 1)[0]
    lines = [line for line in block.splitlines() if line.strip().startswith("|")]
    assert len(lines) >= 3, "no markdown table between the markers"
    return split_row(lines[0]), [split_row(line) for line in lines[2:]]


def test_readme_documents_the_run_command():
    """Criterion 1: 'uv sync --locked seguido del comando documentado en el README'."""
    text = require(README, "T9").read_text(encoding="utf-8")
    assert "uv sync --locked" in text
    assert RUN_COMMAND in text


def test_results_table_layout():
    """Contract: one row per model and one column per metric."""
    header, rows = results_table()
    assert sorted(header[1:]) == sorted(METRICS), header
    assert sorted(row[0] for row in rows) == sorted(MODELS)
    assert all(len(row) == len(header) for row in rows)


def test_results_table_matches_metrics_json():
    """Criterion 7: each 'mean ± std' matches metrics.json to 3 decimals."""
    metrics = read_json(processed("metrics.json"), "T7")
    header, rows = results_table()
    bad = []
    for row in rows:
        model = row[0]
        for metric, cell in zip(header[1:], row[1:]):
            match = CELL.fullmatch(cell)
            if match is None:
                bad.append(f"{model}/{metric}: '{cell}' is not 'x.xxx ± y.yyy'")
                continue
            for text, stat in zip(match.groups(), ("mean", "std")):
                value = metrics[model][metric][stat]
                if value is None or abs(float(text) - value) > 0.0005 + 1e-9:
                    bad.append(f"{model}/{metric}/{stat}: {text} vs {value}")
    assert not bad, "\n".join(bad)

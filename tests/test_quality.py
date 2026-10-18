"""Brief criterion 11: `uvx ruff check .` reports nothing.

The other half of the criterion (`uv run pytest -q` passes) is this suite.
"""

import subprocess

from helpers import ROOT


def test_ruff_check_is_clean():
    """Criterion 11: 'uvx ruff check . no reporta nada'."""
    proc = subprocess.run(
        ["uvx", "ruff", "check", "."], cwd=ROOT, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-1000:]

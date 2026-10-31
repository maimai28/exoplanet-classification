"""Brief criterion 2: raw data immutable, checksum recorded, notebook reads it."""

import hashlib
import subprocess

from helpers import RAW_CSV, RAW_DIR, ROOT, notebook_code_cells, raw, require


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_sha256sums() -> dict[str, str]:
    text = require(RAW_DIR / "SHA256SUMS", "T2").read_text(encoding="utf-8")
    entries = {}
    for line in text.splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            entries[name.lstrip("*")] = digest
    return entries


def test_sha256sums_records_raw_csv():
    """Criterion 2: 'su SHA-256 registrado' (contract: data/raw/SHA256SUMS)."""
    entries = read_sha256sums()
    assert "exoplanets_clean.csv" in entries
    assert entries["exoplanets_clean.csv"] == sha256(RAW_CSV.read_bytes())


def test_every_file_in_sha256sums_matches():
    """Criterion 2 / project rule 4: data/raw/ is write-once."""
    for name, digest in read_sha256sums().items():
        path = RAW_DIR / name
        assert path.is_file(), f"SHA256SUMS lists a missing file: {name}"
        assert sha256(path.read_bytes()) == digest, f"{name} changed"


def test_raw_csv_bytes_equal_commit_b316a47():
    """Criterion 2: 'bytes sin cambios respecto al commit b316a47'."""
    blob = subprocess.run(
        ["git", "-C", str(ROOT), "show", "b316a47:exoplanets_clean.csv"],
        capture_output=True,
        check=True,
    ).stdout
    assert RAW_CSV.read_bytes() == blob


def test_raw_csv_has_623_rows():
    """Brief scope 1 and contract 'Datos crudos': the 623-row CSV."""
    assert len(raw()) == 623


def test_notebook_reads_raw_csv_from_data_raw():
    """Criterion 2: 'El notebook lee desde ahí' (static check).

    Every code line that names exoplanets_clean.csv must also refer to the raw
    directory, and none may point outside the repository.
    """
    lines = [
        line
        for cell in notebook_code_cells()
        for line in cell.splitlines()
        if "exoplanets_clean.csv" in line
    ]
    assert lines, "the notebook never names exoplanets_clean.csv"
    for line in lines:
        assert "raw" in line.lower(), f"not read from data/raw/: {line.strip()}"
        assert "~" not in line and "/home/" not in line, f"outside repo: {line}"

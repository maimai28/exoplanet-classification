"""T3b: test each row's mass against the Archive's mass-radius relation and
classify mass provenance with the rule of brief criterion 4.

Usage:
    uv run python src/t3b_mass_provenance.py [P1_EXOPLANETS_CSV]

Relation: NASA Exoplanet Archive, "How the Archive Calculates Values in the
Planetary Systems Composite Parameters Table" (docs/pscp_calc.html), which
inverts Chen & Kipping (2017, ApJ 834, 17) piecewise: M = (R - C) / S with
R = log10(Rp/R_earth), M = log10(Mp/M_earth), no mass for 11.1 <= Rp < 14.3.
"""

import hashlib
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data/raw/exoplanets_clean.csv"
PROV = ROOT / "data/raw/pscomppars_provenance_2026-10-13.csv"
LINEAGE = ROOT / "data/processed/lineage.csv"
OUT = ROOT / "data/processed/mass_provenance.csv"
P1_DEFAULT = Path.home() / "proyectos/exoplanet-analysis/exoplanets.csv"

SHA256 = {
    CSV: "15f10a81606288d4dec71a8380fff47451cd9f8b5346add5b1c34e79bb966378",
    PROV: "4d280c02823322a876d4321aec570643413d57bfc6c622c9b5b5ea9f714baacd",
    "p1": "e5570cbaae8004213616c02ce9c30634a8b3d2c67c0e2acef90344b47fbe28e8",
}

R_JUP_IN_R_EARTH = 11.208981  # factor reconstructed in T1
M_JUP_IN_M_EARTH = 317.8284  # IAU 2015 B3 nominal GM_J / GM_E
# (lower bound, C, S) for Rp in R_earth; [11.1, 14.3) is degenerate.
REGIMES = [(0.0, 0.00346, 0.2790), (1.23, -0.0925, 0.589), (14.3, -2.85, 0.881)]
DEGENERATE = (11.1, 14.3)
# Relative margin for unit conventions (M_J/M_E, R_J/R_E) on top of rounding.
UNIT_MARGIN = 1e-3
P1_RTOL = 0.01  # criterion 4: mass matches P1 pl_bmassj within +/-1 %


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def testable(re_):
    return not (DEGENERATE[0] <= re_ < DEGENERATE[1])


def mr_mass_mj(re_):
    """Archive mass (M_J) for radius re_ (R_earth); None in the degenerate gap."""
    if not testable(re_):
        return None
    _, c, s = [r for r in REGIMES if re_ >= r[0]][-1]
    return 10 ** ((math.log10(re_) - c) / s) / M_JUP_IN_M_EARTH


def half_ulp(text):
    """Half a unit in the last decimal place written in the CSV string."""
    decimals = len(text.split(".")[1]) if "." in text else 0
    return 0.5 * 10.0**-decimals


def clip_testable(re_, side_of):
    """Clip a radius-interval endpoint back to the testable side of re_."""
    lo, hi = DEGENERATE
    if testable(re_):
        return re_
    return math.nextafter(lo, 0) if side_of < lo else hi


def on_relation(mass_s, radius_s):
    """Rounding-interval test: is there (M, R) within the CSV's printed
    precision such that M lies on the relation (plus UNIT_MARGIN)?"""
    m, r = float(mass_s), float(radius_s)
    dm, dr = half_ulp(mass_s), half_ulp(radius_s)
    re_ = r * R_JUP_IN_R_EARTH
    re_lo = clip_testable((r - dr) * R_JUP_IN_R_EARTH, re_)
    re_hi = clip_testable((r + dr) * R_JUP_IN_R_EARTH, re_)
    p_lo = mr_mass_mj(re_lo) * (1 - UNIT_MARGIN)
    p_hi = mr_mass_mj(re_hi) * (1 + UNIT_MARGIN)
    return m - dm <= p_hi and m + dm >= p_lo


def main():
    p1_path = Path(sys.argv[1]) if len(sys.argv) > 1 else P1_DEFAULT
    for path, digest in [(CSV, SHA256[CSV]), (PROV, SHA256[PROV])]:
        assert sha256(path) == digest, f"SHA-256 mismatch: {path}"
    assert sha256(p1_path) == SHA256["p1"], f"SHA-256 mismatch: {p1_path}"

    raw = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    raw.insert(0, "row_id", range(len(raw)))
    lin = pd.read_csv(LINEAGE, dtype={"row_id": int}, keep_default_na=False)
    prov = pd.read_csv(PROV, dtype=str, keep_default_na=False)
    p1 = pd.read_csv(p1_path)[["pl_name", "pl_bmassj"]]

    d = raw.merge(lin, on="row_id", how="left", validate="1:1")
    d = d.merge(prov[["pl_name", "pl_bmassprov"]], on="pl_name", how="left")
    d = d.merge(p1, on="pl_name", how="left")
    d.loc[d.pl_name == "", ["pl_bmassprov", "pl_bmassj"]] = [None, None]
    assert len(d) == 623 and d.row_id.is_unique

    rows = []
    for x in d.itertuples(index=False):
        mass = float(x.mass)
        if x.pl_name == "":
            match = ""
        elif pd.isna(x.pl_bmassj):
            match = "false"
        else:
            match = str(abs(mass - x.pl_bmassj) <= P1_RTOL * x.pl_bmassj).lower()
        re_ = float(x.radius) * R_JUP_IN_R_EARTH
        pred = mr_mass_mj(re_)
        if pred is None:
            status, pred_s, resid_s = "not_testable", "", ""
        else:
            status = "on_relation" if on_relation(x.mass, x.radius) else "off_relation"
            pred_s, resid_s = f"{pred:.6f}", f"{(mass - pred) / pred:.6f}"
        bprov = x.pl_bmassprov if isinstance(x.pl_bmassprov, str) else ""
        if status == "on_relation" or (match == "true" and bprov == "M-R relationship"):
            cls = "derived"
        elif match == "true" and bprov in ("Mass", "Msini"):
            cls = "measured"
        else:
            cls = "unverifiable"
        rows.append((x.row_id, bprov, match, pred_s, resid_s, status, cls))

    out = pd.DataFrame(
        rows,
        columns=[
            "row_id",
            "pl_bmassprov",
            "mass_matches_p1",
            "mr_predicted_mass",
            "mr_rel_residual",
            "mr_status",
            "mass_provenance",
        ],
    ).sort_values("row_id")
    out.to_csv(OUT, index=False, lineterminator="\n")
    print(out.mr_status.value_counts().to_string())
    print(out.mass_provenance.value_counts().to_string())


if __name__ == "__main__":
    main()

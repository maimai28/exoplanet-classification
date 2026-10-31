"""Brief criterion 13 and contract 'Agrupamiento' (grouping_report.json)."""

from collections import defaultdict

from helpers import (
    N_ROWS,
    expected_group_ids,
    folds,
    lineage,
    processed,
    raw,
    read_json,
)

KEYS = {
    "n_rows",
    "n_rows_with_hostname",
    "n_rows_without_hostname",
    "n_groups",
    "n_groups_multi_hostname",
    "n_fallback_rows_joined",
    "max_group_size",
    "tuple_collisions",
    "hostname_collisions",
}


def load_report() -> dict:
    return read_json(processed("grouping_report.json"), "T7")


def expected_report() -> dict:
    groups = expected_group_ids()
    hostname = dict(zip(lineage()["row_id"], lineage()["hostname"]))
    r = raw()
    tuples = dict(
        zip(r["row_id"], zip(r["star_mass"], r["star_radius"], r["star_teff"]))
    )
    members = defaultdict(list)
    for row_id, group in groups.items():
        members[group].append(row_id)
    hosts_in_group = {
        g: {hostname[i] for i in rows if hostname[i]} for g, rows in members.items()
    }
    hosts_by_tuple = defaultdict(set)
    tuples_by_host = defaultdict(set)
    for i in range(N_ROWS):
        if hostname[i]:
            hosts_by_tuple[tuples[i]].add(hostname[i])
            tuples_by_host[hostname[i]].add(tuples[i])
    with_hostname = sum(1 for i in range(N_ROWS) if hostname[i])
    return {
        "n_rows": N_ROWS,
        "n_rows_with_hostname": with_hostname,
        "n_rows_without_hostname": N_ROWS - with_hostname,
        "n_groups": len(members),
        "n_groups_multi_hostname": sum(len(h) > 1 for h in hosts_in_group.values()),
        "n_fallback_rows_joined": sum(
            1 for i in range(N_ROWS) if not hostname[i] and hosts_in_group[groups[i]]
        ),
        "max_group_size": max(len(rows) for rows in members.values()),
        "tuple_collisions": sum(len(h) > 1 for h in hosts_by_tuple.values()),
        "hostname_collisions": sum(len(t) > 1 for t in tuples_by_host.values()),
    }


def test_report_has_contract_keys_as_integers():
    """Contract: the listed keys are present and every value is an integer."""
    report = load_report()
    assert KEYS <= set(report), f"missing: {sorted(KEYS - set(report))}"
    not_int = {k: v for k, v in report.items() if type(v) is not int}
    assert not not_int, f"non-integer values: {not_int}"


def test_report_row_counts_add_up():
    """Contract: n_rows = 623 = with_hostname + without_hostname."""
    report = load_report()
    assert report["n_rows"] == N_ROWS
    assert report["n_rows_with_hostname"] + report["n_rows_without_hostname"] == N_ROWS


def test_n_groups_matches_folds_csv():
    """Contract: n_groups = distinct group_id in folds.csv."""
    assert load_report()["n_groups"] == folds("folds.csv")["group_id"].nunique()


def test_report_matches_components_rebuilt_from_inputs():
    """Criterion 13: each key recomputed from lineage.csv and data/raw/."""
    report = load_report()
    expected = expected_report()
    diff = {k: (report.get(k), v) for k, v in expected.items() if report.get(k) != v}
    assert not diff, f"(report, expected): {diff}"

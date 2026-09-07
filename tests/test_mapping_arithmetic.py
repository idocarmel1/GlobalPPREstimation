"""Tests for the taxon-to-group arithmetic that turns per-group SPPR into per-taxon PPR.

The parts worth testing here are the ones where a wrong answer looks like a right one:
apportionment weights that quietly fall back to a different basis, a composite SPPR that
averages over a method some of its groups did not resolve, a displayed weight set that
does not sum to one. None of those raise; all of them produce a number.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "claude" / "ewe-species-to-group-mapper" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

import mapping_io as mio  # noqa: E402
import build_model_workbook as bmw  # noqa: E402


# --------------------------------------------------------------------- parsing

@pytest.mark.parametrize("cell,expected", [
    ("Piscivores", ["Piscivores"]),
    ("A | B | C", ["A", "B", "C"]),
    ("  A |B  ", ["A", "B"]),
    ("Crabs & Lobster", ["Crabs & Lobster"]),      # ampersands are not separators
    ("A || B", ["A", "B"]),                        # an empty segment is dropped
    ("", []),
    (None, []),
])
def test_parse_groups_cell(cell, expected):
    assert mio.parse_groups_cell(cell) == expected


def test_blank_weights_mean_catch_composition():
    w, basis, err = mio.parse_weights_cell("", 3)
    assert (w, basis, err) == (None, "catch_composition", None)


def test_named_basis_is_passed_through():
    for name in mio.WEIGHT_BASES:
        w, basis, err = mio.parse_weights_cell(name, 2)
        assert (w, basis, err) == (None, name, None)


def test_explicit_weights_are_normalised():
    w, basis, err = mio.parse_weights_cell("2 | 1 | 1", 3)
    assert err is None and basis is None
    assert w == pytest.approx([0.5, 0.25, 0.25])


@pytest.mark.parametrize("cell,n", [
    ("0.5 | 0.5", 3),          # count mismatch
    ("a | b", 2),              # not numeric
    ("-1 | 2", 2),             # negative
    ("0 | 0", 2),              # sums to zero
])
def test_bad_weights_are_rejected(cell, n):
    w, basis, err = mio.parse_weights_cell(cell, n)
    assert err is not None and w is None


# ----------------------------------------------------------------------- rank

@pytest.mark.parametrize("name,rank", [
    ("Sardinella aurita", "species"),
    ("Sardinella", "genus"),
    ("Sciaenidae", "family"),
    ("Clupeiformes", "order"),
    ("Marine fishes not identified", "category"),
    ("Miscellaneous marine crustaceans", "category"),
    ("Other demersal invertebrates", "category"),
])
def test_taxon_rank(name, rank):
    assert mio.taxon_rank(name) == rank


def test_only_species_and_genus_are_fine_grained():
    assert not mio.is_coarse("Sardinella aurita")
    assert not mio.is_coarse("Sardinella")
    assert mio.is_coarse("Sciaenidae")
    assert mio.is_coarse("Marine fishes not identified")


# -------------------------------------------------------------------- weights

GROUPS = {
    "A": {"group_name": "A", "catch": 30.0, "biomass": 1.0},
    "B": {"group_name": "B", "catch": 10.0, "biomass": 3.0},
    "Z": {"group_name": "Z", "catch": 0.0, "biomass": 0.0},
    "Y": {"group_name": "Y", "catch": 0.0, "biomass": 0.0},
}


def test_a_single_group_takes_everything():
    w, used = bmw.resolve_weights(["A"], "catch_composition", None, GROUPS, {})
    assert w == [1.0] and used == "single"


def test_catch_composition_uses_the_ecosystems_own_landings():
    w, used = bmw.resolve_weights(["A", "B"], "catch_composition", None, GROUPS,
                                  {"A": 75.0, "B": 25.0})
    assert used == "catch_composition"
    assert w == pytest.approx([0.75, 0.25])


def test_catch_composition_falls_back_to_model_catch_then_biomass_then_equal():
    """The fallback chain must be visible in the returned basis, not silent."""
    w, used = bmw.resolve_weights(["A", "B"], "catch_composition", None, GROUPS, {})
    assert used == "model_catch" and w == pytest.approx([0.75, 0.25])

    bare = {k: {"group_name": k, "catch": 0.0, "biomass": v["biomass"]}
            for k, v in GROUPS.items()}
    w, used = bmw.resolve_weights(["A", "B"], "catch_composition", None, bare, {})
    assert used == "model_biomass" and w == pytest.approx([0.25, 0.75])

    w, used = bmw.resolve_weights(["Z", "Y"], "catch_composition", None, GROUPS, {})
    assert used == "equal" and w == pytest.approx([0.5, 0.5])


def test_model_biomass_is_honoured_when_asked_for_even_though_catch_exists():
    w, used = bmw.resolve_weights(["A", "B"], "model_biomass", None, GROUPS,
                                  {"A": 999.0, "B": 1.0})
    assert used == "model_biomass" and w == pytest.approx([0.25, 0.75])


def test_explicit_weights_beat_every_basis():
    w, used = bmw.resolve_weights(["A", "B"], "catch_composition", [0.9, 0.1], GROUPS,
                                  {"A": 1.0, "B": 99.0})
    assert used == "explicit" and w == [0.9, 0.1]


# --------------------------------------------------------------- composite SPPR

METHODS = ["m1", "m2", "m3"]
SPPR = {
    "A": [10.0, 100.0, None],
    "B": [20.0, None, 5.0],
}


def row(taxon, group, weights="", conf="medium", ev="composite_split"):
    return {"taxon": taxon, "group": group, "weights": weights,
            "confidence": conf, "evidence": ev, "explanation": "x"}


def test_single_group_sppr_is_the_groups_own():
    out = bmw.build_taxon_sppr([row("t", "A", conf="high", ev="explicit_member")],
                               METHODS, SPPR, GROUPS, {"t": 1.0})
    assert out["t"]["sppr"] == [10.0, 100.0, None]


def test_composite_sppr_is_the_weighted_mean():
    out = bmw.build_taxon_sppr([row("t", "A | B", weights="0.5 | 0.5")],
                               METHODS, SPPR, GROUPS, {"t": 1.0})
    assert out["t"]["sppr"][0] == pytest.approx(15.0)


def test_a_method_missing_from_any_contributing_group_is_none_not_partial():
    """A partial weighted sum would understate the taxon and look like a real number."""
    out = bmw.build_taxon_sppr([row("t", "A | B", weights="0.5 | 0.5")],
                               METHODS, SPPR, GROUPS, {"t": 1.0})
    assert out["t"]["sppr"][1] is None      # B has no m2
    assert out["t"]["sppr"][2] is None      # A has no m3


def test_unresolved_contributes_nothing():
    out = bmw.build_taxon_sppr([row("t", "Unresolved", conf="unresolved", ev="none")],
                               METHODS, SPPR, GROUPS, {"t": 1.0})
    assert out["t"]["names"] == ["Unresolved"]
    assert out["t"]["sppr"] == [None, None, None]


def test_composite_weights_come_only_from_singly_assigned_catch():
    """Otherwise one composite's weights would depend on another's, and on row order."""
    rows = [
        row("solo_a", "A", conf="high", ev="explicit_member"),
        row("solo_b", "B", conf="high", ev="explicit_member"),
        row("wide", "A | B"),
    ]
    totals = {"solo_a": 90.0, "solo_b": 10.0, "wide": 1000.0}
    out = bmw.build_taxon_sppr(rows, METHODS, SPPR, GROUPS, totals)
    assert out["wide"]["basis"] == "catch_composition"
    assert out["wide"]["weights"] == pytest.approx([0.9, 0.1])
    # the composite's own 1000 t must not have leaked into the weights
    assert out["wide"]["sppr"][0] == pytest.approx(0.9 * 10.0 + 0.1 * 20.0)


# ------------------------------------------------------------------- display

@pytest.mark.parametrize("weights", [
    [1 / 3, 1 / 3, 1 / 3],
    [0.3595, 0.2405, 0.4],
    [0.9999, 0.0001],
    [1 / 7] * 7,
])
def test_displayed_weights_always_sum_to_one(weights):
    shown = bmw.show_weights(weights)
    parts = [float(x) for x in shown.split("|")]
    assert len(parts) == len(weights)
    assert sum(parts) == pytest.approx(1.0, abs=1e-12)


def test_displayed_weights_stay_close_to_the_real_ones():
    weights = [0.3595, 0.2405, 0.4]
    parts = [float(x) for x in bmw.show_weights(weights).split("|")]
    for got, want in zip(parts, weights):
        assert abs(got - want) < 1e-3


# --------------------------------------------------------------- the Jensen gap

def test_aggregating_before_exponentiating_always_understates():
    """SPPR is convex in TL, so the group-aggregated estimate cannot exceed the per-taxon
    one. This is the property the two grey rows of `PPR by method` exist to display."""
    catch = {"a": 100.0, "b": 100.0, "c": 50.0}
    tl = {"a": 2.0, "b": 4.0, "c": 3.2}

    per_taxon = sum(c * bmw.simple_sppr(tl[t]) for t, c in catch.items())
    total = sum(catch.values())
    mean_tl = sum(catch[t] * tl[t] for t in catch) / total
    aggregated = total * (1.0 / bmw.TRANSFER_EFFICIENCY) ** (mean_tl - 1.0)

    assert aggregated < per_taxon
    assert aggregated / per_taxon < 0.9      # and by a lot, at this TL spread


def test_the_gap_vanishes_when_every_taxon_shares_a_trophic_level():
    catch = {"a": 100.0, "b": 100.0}
    tl = {"a": 3.0, "b": 3.0}
    per_taxon = sum(c * bmw.simple_sppr(tl[t]) for t, c in catch.items())
    total = sum(catch.values())
    mean_tl = sum(catch[t] * tl[t] for t in catch) / total
    aggregated = total * (1.0 / bmw.TRANSFER_EFFICIENCY) ** (mean_tl - 1.0)
    assert aggregated == pytest.approx(per_taxon)


# ------------------------------------------------------------------ sidecars

def test_sidecar_files_are_not_mistaken_for_mappings(tmp_path):
    d = tmp_path / "data" / "LME_999" / "mapping"
    d.mkdir(parents=True)
    for name in ["m.csv", "m.groups.csv", "m.members.csv", "m.resolved.csv", "m.taxonomy.csv"]:
        (d / name).write_text("taxon\n", encoding="utf-8")
    found = [p.name for p in mio.mapping_files(tmp_path, "LME_999")]
    assert found == ["m.csv"]

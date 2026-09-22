"""Checks for scorer.draw_indices / bootstrap_replicates / summarize_replicates.

Clauses: 6.2.1 (draws, reproducibility, one array for every statistic),
6.2.2 (undefined replicates and withheld intervals), 6.2.3 (defined but
degenerate intervals), 6.6 last paragraph (CI-policy fixtures) and 2.3.7
(paired resampling).

Every bootstrap here uses a small n_replicates passed explicitly; the
default 10,000 is never run. The two 6.6 CI-policy fixtures are synthetic
replicate lists of length 10,000 fed straight to summarize_replicates, with
no bootstrap. Expected values are written by hand, not computed with the
code under test; where a check compares the same function on the same input
twice, or re-derives a replicate in the test body, equality is exact.
The tables are synthetic, not research observations; no API is called.
"""

import numpy as np
import pytest

import scorer
from build_inputs import CONDITIONS
from scorer import (
    PAIRED_CONDITIONS, bootstrap_replicates, delta_key, draw_indices, paired, paired_baseline_key,
    paired_key, standalone, standalone_key, statistic_keys, summarize_replicates,
)
from tests.test_scorer_kappa import A, B, ITEMS_66, REPL, RESOLVED, build

TOL = 1e-12
SEED = 20260919
N_FIXTURE = 10_000   # 6.6: "one undefined value among 10,000" -> proportion 0.0001


def spread(n: int) -> list[float]:
    """n evenly spaced floats from 0.0 to 1.0 inclusive (an unaffected, non-degenerate statistic)."""
    return [i / (n - 1) for i in range(n)]


# --- undefined replicates (6.2.2, 6.6) ------------------------------------------

def test_one_undefined_replicate_withholds_interval():
    values = spread(N_FIXTURE)
    values[4321] = None
    s = summarize_replicates(values, 0.5)
    assert s.n_replicates == N_FIXTURE
    assert s.undefined_count == 1
    assert abs(s.undefined_proportion - 0.0001) < TOL
    assert s.lower is None and s.upper is None
    assert s.withheld_reason is not None
    assert s.degenerate is False


def test_all_defined_replicates_keep_interval():
    s = summarize_replicates(spread(N_FIXTURE), 0.5)
    assert s.undefined_count == 0
    assert abs(s.undefined_proportion - 0.0) < TOL
    assert isinstance(s.lower, float) and isinstance(s.upper, float)
    assert s.withheld_reason is None


def test_not_estimable_point_estimate_withholds_interval():
    s = summarize_replicates(spread(N_FIXTURE), None)
    assert s.undefined_count == 0
    assert s.lower is None and s.upper is None
    assert s.withheld_reason is not None


def test_bootstrap_records_undefined_baseline_as_none():
    # Human [A, A], baseline [A, A], replacement [B, B] (6.6 undefined case):
    # every resample is again all-A on the baseline side, so baseline κ and
    # Δκ are undefined in every replicate while replacement κ stays 0.
    items = [(1, A, (A, RESOLVED), (B, RESOLVED)),
             (2, A, (A, RESOLVED), (B, RESOLVED))]
    table = build(items)
    reps = bootstrap_replicates(table, draw_indices(len(table), n_replicates=20, seed=SEED))
    assert all(len(v) == 20 for v in reps.values.values())
    assert all(v is None for v in reps.values[paired_baseline_key(REPL)])
    assert all(v is None for v in reps.values[delta_key(REPL)])
    assert all(v is not None and abs(v - 0.0) < TOL for v in reps.values[paired_key(REPL)])


# --- degenerate intervals (6.2.3, 6.6) --------------------------------------------

def test_all_zero_delta_fixture_gives_degenerate_zero_interval():
    s = summarize_replicates([0.0] * N_FIXTURE, 0.0)
    assert s.undefined_count == 0
    assert s.withheld_reason is None
    assert abs(s.lower - 0.0) < TOL and abs(s.upper - 0.0) < TOL
    assert s.degenerate is True


def test_spread_values_are_not_degenerate():
    s = summarize_replicates(spread(N_FIXTURE), 0.5)
    assert s.degenerate is False
    assert s.lower < s.upper


def test_identical_labels_bootstrap_delta():
    # Human, baseline and replacement all [A, A, B, B] (6.6 identical case).
    # A resample that is all-A or all-B has undefined κ (6.2.2); with the
    # fixed seed the outcome is deterministic, and both branches below are
    # correct behaviour. Which branch occurs is reported, not asserted.
    items = [(1, A, (A, RESOLVED), (A, RESOLVED)),
             (2, A, (A, RESOLVED), (A, RESOLVED)),
             (3, B, (B, RESOLVED), (B, RESOLVED)),
             (4, B, (B, RESOLVED), (B, RESOLVED))]
    table = build(items)
    reps = bootstrap_replicates(table, draw_indices(len(table), n_replicates=50, seed=SEED))
    deltas = reps.values[delta_key(REPL)]
    assert len(deltas) == 50
    assert all(v is None or abs(v - 0.0) < TOL for v in deltas)
    s = summarize_replicates(deltas, 0.0)
    if s.undefined_count == 0:
        assert abs(s.lower - 0.0) < TOL and abs(s.upper - 0.0) < TOL
        assert s.degenerate is True
        assert s.withheld_reason is None
    else:
        assert s.lower is None and s.upper is None
        assert s.withheld_reason is not None
        assert s.degenerate is False


# --- pairing across conditions (6.2.1, 2.3.7) -------------------------------------

def test_every_statistic_uses_the_same_draw():
    table = build(ITEMS_66)
    draws = draw_indices(len(table), n_replicates=30, seed=SEED)
    reps = bootstrap_replicates(table, draws)
    assert set(reps.values) == set(statistic_keys()) and len(statistic_keys()) == 18
    for r in range(30):
        rep = [table[i] for i in draws.indices[r]]
        for c in CONDITIONS:
            expected = standalone(rep, c).result.kappa
            got = reps.values[standalone_key(c)][r]
            assert (got is None) if expected is None else (got == expected)
        for c in PAIRED_CONDITIONS:
            p = paired(rep, c)
            for key, expected in ((paired_baseline_key(c), p.baseline.kappa),
                                  (paired_key(c), p.result.kappa),
                                  (delta_key(c), p.delta_kappa)):
                got = reps.values[key][r]
                assert (got is None) if expected is None else (got == expected)


def test_draws_are_reproducible_and_carry_their_conditions():
    d1 = draw_indices(6, 30, SEED)
    d2 = draw_indices(6, 30, SEED)
    assert np.array_equal(d1.indices, d2.indices)
    assert not np.array_equal(d1.indices, draw_indices(6, 30, SEED + 1).indices)
    assert d1.indices.shape == (30, 6)
    assert int(d1.indices.min()) >= 0 and int(d1.indices.max()) < 6
    assert (d1.n, d1.n_replicates, d1.seed) == (6, 30, SEED)
    assert d1.numpy_version == np.__version__


def test_draws_match_the_6_2_1_expression():
    expected = np.random.Generator(np.random.PCG64(SEED)).integers(0, 6, size=(30, 6))
    assert np.array_equal(draw_indices(6, 30, SEED).indices, expected)


# --- paired n varies across replicates (6.1.2, 6.2.1) ------------------------------

def test_paired_n_varies_but_every_list_is_full_length():
    table = build(ITEMS_66)
    draws = draw_indices(len(table), n_replicates=100, seed=SEED)
    reps = bootstrap_replicates(table, draws)
    paired_ns = {paired([table[i] for i in draws.indices[r]], REPL).paired_n for r in range(100)}
    assert len(paired_ns) >= 2
    assert len(reps.values) == 18
    assert all(len(v) == 100 for v in reps.values.values())
    assert (reps.n_records, reps.n_replicates, reps.seed) == (6, 100, SEED)


# --- refusals ----------------------------------------------------------------------

def test_draw_indices_rejects_empty_sizes():
    with pytest.raises(ValueError):
        draw_indices(0)
    with pytest.raises(ValueError):
        draw_indices(6, n_replicates=0)


def test_bootstrap_rejects_draws_for_another_table_size():
    table = build(ITEMS_66)
    with pytest.raises(ValueError):
        bootstrap_replicates(table, draw_indices(len(table) + 1, n_replicates=5, seed=SEED))


def test_summarize_rejects_empty_list():
    with pytest.raises(ValueError):
        summarize_replicates([], 0.0)

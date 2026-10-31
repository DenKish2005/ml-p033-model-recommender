"""Independent frozen-0.1 candidate contracts; no estimator fitting or datasets."""

from itertools import product

import pytest

from model_recommender.model_families import (
    GBDT_BASELINE,
    MLP_BASELINE,
    candidates_for_family,
    gbdt_candidates,
    mlp_candidates,
)

# Expected values transcribed from experiment-protocol.md, Model settings / D005.
# Keep these independent of both factories and TOML so either side can drift.
SEARCH = {
    "GBDT": {
        "learning_rate": (0.03, 0.1),
        "max_leaf_nodes": (15, 31, 63),
        "l2_regularization": (0.0, 1.0, 10.0),
        "min_samples_leaf": (10, 20, 40),
    },
    "DNN": {
        "hidden_layer_sizes": ((32, 16), (64, 32), (128, 64)),
        "alpha": (0.0001, 0.001, 0.01),
        "learning_rate_init": (0.0003, 0.001, 0.003),
    },
}
BASELINE = {
    "GBDT": {
        "learning_rate": 0.1,
        "max_leaf_nodes": 31,
        "l2_regularization": 0.0,
        "min_samples_leaf": 20,
    },
    "DNN": {"hidden_layer_sizes": (32, 16), "alpha": 0.0001, "learning_rate_init": 0.001},
}
MODELS = {"GBDT": "hist_gradient_boosting", "DNN": "mlp"}
GRID_SIZE = {"GBDT": 54, "DNN": 27}


def parameter_key(params):
    return tuple(sorted(params.items()))


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
def test_full_cartesian_space_matches_frozen_contract(family):
    search = SEARCH[family]
    expected = {
        parameter_key(dict(zip(search, values, strict=True)))
        for values in product(*search.values())
    }
    candidates = candidates_for_family(family, count=GRID_SIZE[family])
    assert len(expected) == len(candidates) == GRID_SIZE[family]
    assert {parameter_key(candidate.params) for candidate in candidates} == expected
    assert [candidate.order for candidate in candidates] == list(range(GRID_SIZE[family]))
    assert {(candidate.family, candidate.model) for candidate in candidates} == {
        (family, MODELS[family])
    }
    assert candidates[0].params == BASELINE[family]


@pytest.mark.parametrize("family,factory", [("GBDT", gbdt_candidates), ("DNN", mlp_candidates)])
def test_default_sampling_is_distinct_baseline_first_and_repeatable(family, factory):
    candidates = factory()
    assert candidates == factory(count=20, seed=42)
    assert candidates == candidates_for_family(family)
    assert len(candidates) == len({parameter_key(c.params) for c in candidates}) == 20
    assert [c.order for c in candidates] == list(range(20))
    assert candidates[0].params == BASELINE[family]
    assert all(c.family == family and c.model == MODELS[family] for c in candidates)
    changed_seed = factory(count=20, seed=137)
    assert changed_seed[0] == candidates[0]
    assert {parameter_key(c.params) for c in changed_seed[1:]} != {
        parameter_key(c.params) for c in candidates[1:]
    }
    assert factory(count=7, seed=137) == factory(count=7, seed=137)


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
def test_single_candidate_is_baseline_regardless_of_seed(family):
    for seed in (42, 137, 2026):
        candidates = candidates_for_family(family, count=1, seed=seed)
        assert len(candidates) == 1
        assert candidates[0].order == 0
        assert candidates[0].params == BASELINE[family]


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
@pytest.mark.parametrize("boundary", ["negative", "zero", "above-grid"])
def test_invalid_candidate_counts_fail_predictably(family, boundary):
    count = {"negative": -1, "zero": 0, "above-grid": GRID_SIZE[family] + 1}[boundary]
    with pytest.raises(ValueError, match=f"between 1 and {GRID_SIZE[family]}"):
        candidates_for_family(family, count=count)


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
def test_mutating_returned_params_cannot_change_baseline_or_other_calls(family):
    original = candidates_for_family(family)
    mutated = candidates_for_family(family)
    # Both the baseline and sampled dictionaries must be independent per call.
    for candidate in mutated:
        candidate.params.clear()
        candidate.params["unexpected"] = -1
    assert candidates_for_family(family) == original
    assert GBDT_BASELINE == BASELINE["GBDT"]
    assert MLP_BASELINE == BASELINE["DNN"]
    assert len({id(c.params) for c in original}) == 20


@pytest.mark.parametrize("family", ["unknown", "gbdt", "", "MLP"])
def test_unknown_candidate_family_is_rejected(family):
    with pytest.raises(ValueError, match="Unknown model family"):
        candidates_for_family(family)

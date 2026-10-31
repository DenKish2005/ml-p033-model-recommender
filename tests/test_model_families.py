"""Independent frozen-0.1 candidate contracts; no estimator fitting or datasets."""

from itertools import product
from pathlib import Path
from tomllib import loads

import pytest
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

from model_recommender.model_families import (
    GBDT_BASELINE,
    MLP_BASELINE,
    ModelCandidate,
    build_estimator,
    candidates_for_family,
    gbdt_candidates,
    mlp_candidates,
    needs_numeric_scaling,
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
ROOT = Path(__file__).resolve().parents[1]
SETTINGS = {
    "GBDT": {"max_iter": 200, "early_stopping": False},
    "DNN": {"max_iter": 500, "solver": "adam", "activation": "relu", "early_stopping": False},
}


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


@pytest.mark.parametrize("family,filename", [("GBDT", "gbdt.toml"), ("DNN", "dnn.toml")])
def test_model_toml_matches_every_explicit_frozen_setting(family, filename):
    config = loads((ROOT / "configs/models" / filename).read_text(encoding="utf-8"))
    model = MODELS[family]
    assert set(config) == {"family", model}
    assert config["family"] == {"name": family, "models": [model]}
    block = config[model]
    assert set(block) == set(SEARCH[family]) | set(SETTINGS[family]) | {"baseline"}
    search = {key: block[key] for key in SEARCH[family]}
    baseline = block["baseline"].copy()
    if family == "DNN":
        # TOML arrays are lists; sklearn candidates deliberately use immutable tuples.
        assert all(isinstance(value, list) for value in search["hidden_layer_sizes"])
        assert isinstance(baseline["hidden_layer_sizes"], list)
        search["hidden_layer_sizes"] = [tuple(value) for value in search["hidden_layer_sizes"]]
        baseline["hidden_layer_sizes"] = tuple(baseline["hidden_layer_sizes"])
    assert {key: tuple(values) for key, values in search.items()} == SEARCH[family]
    assert baseline == BASELINE[family]
    assert {key: block[key] for key in SETTINGS[family]} == SETTINGS[family]
    # Also compare the actual Cartesian space with TOML, not just cardinalities.
    configured = {
        parameter_key(dict(zip(search, values, strict=True)))
        for values in product(*search.values())
    }
    candidates = candidates_for_family(family, count=GRID_SIZE[family])
    assert {parameter_key(c.params) for c in candidates} == configured
    assert candidates[0].params == baseline


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
@pytest.mark.parametrize("outer_seed", [42, 137, 2026])
def test_estimator_construction_preserves_candidates_and_locked_defaults(family, outer_seed):
    estimator_class = HistGradientBoostingClassifier if family == "GBDT" else MLPClassifier
    for candidate in candidates_for_family(family, count=GRID_SIZE[family]):
        estimator = build_estimator(candidate, random_state=outer_seed)
        assert type(estimator) is estimator_class
        # All unconfigured settings stay at the installed, locked sklearn defaults.
        # Explicit project settings are independently fixed above, even if a default agrees.
        expected = estimator_class().get_params() | SETTINGS[family] | candidate.params
        expected["random_state"] = outer_seed
        assert estimator.get_params() == expected
        if family == "DNN":
            assert isinstance(estimator.hidden_layer_sizes, tuple)
    assert needs_numeric_scaling(family) is (family == "DNN")


def test_unsupported_estimator_and_scaling_families_are_rejected():
    candidate = ModelCandidate("unknown", "unknown", 0, {})
    with pytest.raises(ValueError, match="Unsupported candidate family"):
        build_estimator(candidate, random_state=42)
    with pytest.raises(ValueError, match="Unknown model family"):
        needs_numeric_scaling("unknown")

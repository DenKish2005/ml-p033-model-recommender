import numpy as np
import pandas as pd
import pytest

from model_recommender.features import characterize


def test_mixed_missing_and_imbalanced_data():
    X = pd.DataFrame({"age": [10, np.nan, 30, 40], "category": ["a", "b", "a", "a"]})
    result = characterize(X, pd.Series([0, 0, 0, 1]))
    assert result["missing_fraction"] == 0.125
    assert result["categorical_fraction"] == 0.5
    assert result["imbalance_ratio"] == 3
    assert result["minority_class_fraction"] == 0.25


@pytest.mark.parametrize("target", [[0, None], [0, 0], [0]])
def test_invalid_targets(target):
    with pytest.raises(ValueError):
        characterize(pd.DataFrame({"x": [1, 2]}), pd.Series(target))


def test_misaligned_target():
    with pytest.raises(ValueError, match="matching"):
        characterize(pd.DataFrame({"x": [1, 2]}), pd.Series([0, 1], index=[1, 0]))


def test_empty_and_infinite_features():
    with pytest.raises(ValueError, match="at least one"):
        characterize(pd.DataFrame(), pd.Series(dtype=int))
    with pytest.raises(ValueError, match="infinite"):
        characterize(pd.DataFrame({"x": [1, np.inf]}), pd.Series([0, 1]))

from dataclasses import replace

import pandas as pd

from model_recommender.audit import audit_dataset
from model_recommender.datasets import LoadedDataset, read_registry


def test_duplicate_and_conflict_audit():
    spec = replace(
        read_registry()["credit-g"],
        name="audit-test",
        expected_rows=5,
        numeric_features=["x"],
        categorical_features=["c"],
        excluded_features=[],
    )
    X = pd.DataFrame({"x": [1, 1, 2, 3, 3], "c": ["a", "a", "b", "c", "c"]})
    y = pd.Series([0, 0, 1, 0, 1], name="class")
    result = audit_dataset(LoadedDataset(spec, X, y))
    assert result["duplicate_feature_rows"] == 4
    assert result["exact_duplicate_rows"] == 2
    assert result["conflicting_target_signature_rows"] == 2

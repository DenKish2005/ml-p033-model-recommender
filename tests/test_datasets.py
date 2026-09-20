import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.utils import Bunch

from model_recommender import cli, datasets
from model_recommender.datasets import load_dataset, read_registry


@pytest.fixture
def spec():
    return replace(
        read_registry()["credit-g"],
        expected_rows=4,
        numeric_features=["age"],
        categorical_features=["category"],
        excluded_features=["record_id"],
    )


@pytest.fixture
def source(spec):
    return Bunch(
        details={
            "id": str(spec.openml_id),
            "name": spec.name,
            "version": str(spec.version),
            "md5_checksum": spec.md5_checksum,
        },
        data=pd.DataFrame(
            {
                "age": [20.0, np.nan, 40.0, 50.0],
                "category": pd.Categorical(["a", None, "b", "a"]),
                "record_id": [1, 2, 3, 4],
            }
        ),
        target=pd.Series(["good", "bad", "good", "bad"], name="class"),
    )


def test_pilot_registry():
    registry = read_registry()
    assert len(registry) == 5
    assert len({spec.family for spec in registry.values()}) == 5
    assert all(not spec.clinical for spec in registry.values())
    assert registry["adult"].version == 2
    assert registry["tic-tac-toe"].target == "Class"


def test_load_preserves_missingness_and_encodes_positive_class(monkeypatch, tmp_path, spec, source):
    calls = []

    def fetch(**kwargs):
        calls.append(kwargs)
        return source

    monkeypatch.setattr(datasets, "fetch_openml", fetch)
    loaded = load_dataset(spec, tmp_path)
    assert loaded.X.columns.tolist() == ["age", "category"]
    assert loaded.X.isna().sum().sum() == 2
    assert isinstance(loaded.X["category"].dtype, pd.CategoricalDtype)
    assert loaded.y.tolist() == [0, 1, 0, 1]
    assert loaded.summary()["class_counts"] == {"bad": 2, "good": 2}
    assert calls[0]["data_id"] == 31
    assert calls[0]["target_column"] == "class"
    assert calls[0]["cache"] is True
    assert calls[0]["data_home"] == str(tmp_path)
    assert "record_id" in source.data


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "999"),
        ("version", "2"),
        ("name", "other"),
        ("md5_checksum", "0" * 32),
    ],
)
def test_reject_metadata_drift(monkeypatch, spec, source, field, value):
    source.details[field] = value
    monkeypatch.setattr(datasets, "fetch_openml", lambda **kwargs: source)
    with pytest.raises(ValueError, match="does not match"):
        load_dataset(spec)


@pytest.mark.parametrize(
    "defect", ["rows", "columns", "dtype", "classes", "missing", "index", "inf"]
)
def test_reject_invalid_data(monkeypatch, spec, source, defect):
    if defect == "rows":
        source.data = source.data.iloc[:-1]
    elif defect == "columns":
        source.data["unexpected"] = 0
    elif defect == "dtype":
        source.data["age"] = source.data["age"].astype(str)
    elif defect == "classes":
        source.target.iloc[0] = "unknown"
    elif defect == "missing":
        source.target.iloc[0] = None
    elif defect == "index":
        source.target.index = [3, 2, 1, 0]
    else:
        source.data.loc[0, "age"] = np.inf
    monkeypatch.setattr(datasets, "fetch_openml", lambda **kwargs: source)
    with pytest.raises(ValueError):
        load_dataset(spec)


@pytest.mark.parametrize(
    "changes",
    [
        {"positive_class": "unknown"},
        {"class_labels": ["bad", "good", "bad"]},
        {"categorical_features": ["age"]},
        {"numeric_features": ["class"]},
        {"clinical": "false"},
    ],
)
def test_reject_invalid_spec(spec, changes):
    with pytest.raises(ValueError):
        replace(spec, **changes)


def test_registry_rejects_duplicate_entries(tmp_path):
    original = Path("configs/datasets.toml").read_text()
    duplicate = original + "\n[[datasets]]" + original.split("[[datasets]]")[1]
    path = tmp_path / "datasets.toml"
    path.write_text(duplicate)
    with pytest.raises(ValueError, match="Duplicate"):
        read_registry(path)


def test_cli_fetch_all_skips_clinical_holdout(monkeypatch, capsys, spec, source):
    holdout = replace(spec, name="held-out", clinical=True)
    monkeypatch.setattr(cli, "read_registry", lambda path: {spec.name: spec, holdout.name: holdout})
    monkeypatch.setattr(datasets, "fetch_openml", lambda **kwargs: source)
    monkeypatch.setattr("sys.argv", ["p033", "fetch", "all"])
    cli.main()
    result = json.loads(capsys.readouterr().out)
    assert len(result) == 1
    assert result[0]["dataset"]["name"] == spec.name


def test_cli_unknown_dataset(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["p033", "fetch", "unknown"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    assert "Unknown dataset" in capsys.readouterr().err

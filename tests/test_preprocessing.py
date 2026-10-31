"""Hand-computed contracts for fold-local dense preprocessing (T03)."""

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from model_recommender import runner
from model_recommender.preprocessing import (
    DensePreprocessor,
    fit_transform_checked,
    infer_feature_roles,
    make_preprocessor,
    transform_checked,
)


@pytest.mark.parametrize(
    ("frame", "numeric", "categorical", "names", "expected"),
    [
        (
            pd.DataFrame({"n": [1.0, np.nan, 5.0], "constant": [7.0] * 3}),
            ("n", "constant"),
            (),
            ["n", "constant", "missingindicator_n"],
            [[1, 7, 0], [3, 7, 1], [5, 7, 0]],
        ),
        (
            pd.DataFrame({"c": pd.Categorical(["b", None, "a"]), "constant": ["k"] * 3}),
            (),
            ("c", "constant"),
            ["c___missing__", "c_a", "c_b", "constant_k"],
            [[0, 0, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1]],
        ),
        (
            pd.DataFrame({"c": pd.Categorical(["b", None, "a"]), "n": [1.0, np.nan, 5.0]}),
            ("n",),
            ("c",),
            ["n", "missingindicator_n", "c___missing__", "c_a", "c_b"],
            [[1, 0, 0, 0, 1], [3, 1, 1, 0, 0], [5, 0, 0, 1, 0]],
        ),
        (
            pd.DataFrame({"flag": [True, False, True]}),
            (),
            ("flag",),
            ["flag_False", "flag_True"],
            [[0, 1], [1, 0], [0, 1]],
        ),
    ],
    ids=["numeric", "categorical", "mixed", "bool-is-categorical"],
)
def test_roles_values_and_feature_names(frame, numeric, categorical, names, expected):
    pre = make_preprocessor(frame, scale_numeric=False)
    assert pre.roles.numeric == numeric
    assert pre.roles.categorical == categorical
    result = fit_transform_checked(pre, frame)
    assert result.dtype == np.float64
    assert np.isfinite(result).all()
    assert result.shape == (len(frame), len(names))
    assert_allclose(result, expected)
    assert_array_equal(pre.get_feature_names_out(), names)
    # Callers cannot mutate the fitted name/order contract through the returned array.
    returned = pre.get_feature_names_out()
    returned[0] = "changed"
    assert_array_equal(pre.get_feature_names_out(), names)


@pytest.mark.parametrize("dtype", [object, "str", "string", "category"])
@pytest.mark.parametrize("missing", [None, np.nan, pd.NA], ids=["None", "nan", "pd.NA"])
def test_categorical_missing_representations_use_the_same_token(dtype, missing):
    frame = pd.DataFrame({"c": pd.Series(["a", missing, "b"], dtype=dtype)})
    pre = make_preprocessor(frame, scale_numeric=False)
    result = fit_transform_checked(pre, frame)
    assert_array_equal(pre.get_feature_names_out(), ["c___missing__", "c_a", "c_b"])
    assert_allclose(result, [[0, 1, 0], [1, 0, 0], [0, 0, 1]])
    scoring = pd.DataFrame({"c": pd.Series([missing, "unseen"], dtype=dtype)})
    assert_allclose(transform_checked(pre, scoring), [[1, 0, 0], [0, 0, 0]])


@pytest.mark.parametrize("dtype", [object, "str", "string", "category"])
def test_all_missing_training_columns_are_retained(dtype):
    train = pd.DataFrame({"n": [np.nan] * 3, "c": pd.Series([None] * 3, dtype=dtype)})
    pre = make_preprocessor(train, scale_numeric=False)
    result = fit_transform_checked(pre, train)
    assert result.dtype == np.float64
    assert np.isfinite(result).all()
    assert_array_equal(pre.numeric_imputer.statistics_, [0])
    assert_array_equal(pre.get_feature_names_out(), ["n", "missingindicator_n", "c___missing__"])
    assert_allclose(result, [[0, 1, 1]] * 3)
    scoring = pd.DataFrame({"n": [9.0, np.nan], "c": pd.Series(["new", None], dtype=dtype)})
    assert_allclose(transform_checked(pre, scoring), [[9, 0, 0], [0, 1, 1]])


def test_nullable_bool_keeps_categorical_role_and_missing_token():
    frame = pd.DataFrame({"flag": pd.Series([True, pd.NA, False], dtype="boolean")})
    pre = make_preprocessor(frame, scale_numeric=False)
    assert pre.roles.categorical == ("flag",)
    # A categorical block needs a common representation for boolean values and its string token.
    result = fit_transform_checked(pre, frame)
    assert_array_equal(pre.get_feature_names_out(), ["flag_False", "flag_True", "flag___missing__"])
    assert_allclose(result, [[0, 1, 0], [0, 0, 1], [1, 0, 0]])


@pytest.mark.parametrize("phase", ["infer", "fit", "transform"])
@pytest.mark.parametrize("bad_columns", [["n", "n"], ["n", "c", "n"], ["n"]])
def test_missing_or_duplicate_columns_fail_predictably(phase, bad_columns):
    train = pd.DataFrame({"n": [1.0, 2.0], "c": ["a", "b"]})
    bad = pd.DataFrame([[1] * len(bad_columns)] * 2, columns=bad_columns)
    pre = make_preprocessor(train, scale_numeric=False)
    if phase == "infer":
        if len(set(bad_columns)) == len(bad_columns):
            # Inference has no prior schema; a numeric-only frame is valid.
            assert infer_feature_roles(bad).numeric == ("n",)
        else:
            with pytest.raises(ValueError, match="unique"):
                infer_feature_roles(bad)
    elif phase == "fit":
        with pytest.raises(ValueError, match="unique|Missing preprocessing columns"):
            fit_transform_checked(pre, bad)
    else:
        fit_transform_checked(pre, train)
        with pytest.raises(ValueError, match="unique|Missing preprocessing columns"):
            transform_checked(pre, bad)


def test_unknown_categories_and_late_numeric_missingness_keep_training_width():
    train = pd.DataFrame({"n": [1.0, 5.0], "c": ["a", "b"]})
    pre = make_preprocessor(train, scale_numeric=False)
    fit_transform_checked(pre, train)
    scoring = pd.DataFrame({"c": ["test-only", "a"], "n": [np.nan, 1000.0]})
    assert_allclose(transform_checked(pre, scoring), [[3, 0, 0], [1000, 1, 0]])
    assert_array_equal(pre.get_feature_names_out(), ["n", "c_a", "c_b"])
    assert_array_equal(pre.onehot.categories_[0], ["a", "b"])


@pytest.mark.parametrize("scale_numeric", [False, True])
def test_fit_statistics_and_transforms_use_train_only(monkeypatch, scale_numeric):
    train = pd.DataFrame(
        {"n": [0.0, np.nan, 6.0], "constant": [7.0] * 3, "c": ["a", None, "b"]},
        index=[11, 13, 17],
    )
    numeric_block = np.array([[0, 7, 0], [3, 7, 1], [6, 7, 0]], dtype=np.float64)
    calls = []

    def spy_fit(cls, label):
        original = cls.fit

        def fit(self, X, *args, **kwargs):
            calls.append((label, X.copy()))
            return original(self, X, *args, **kwargs)

        monkeypatch.setattr(cls, "fit", fit)

    spy_fit(SimpleImputer, "imputer")
    spy_fit(OneHotEncoder, "encoder")
    spy_fit(StandardScaler, "scaler")
    pre = make_preprocessor(train, scale_numeric=scale_numeric)
    fitted_train = fit_transform_checked(pre, train)
    assert_array_equal(pre.numeric_imputer.statistics_, [3, 7])
    assert_array_equal(pre.numeric_imputer.indicator_.features_, [0])
    assert_array_equal(pre.categorical_imputer.statistics_, ["__missing__"])
    assert_array_equal(pre.onehot.categories_[0], ["__missing__", "a", "b"])
    assert pre.onehot.handle_unknown == "ignore"
    assert [label for label, _ in calls] == (
        ["imputer", "imputer", "encoder", "scaler"]
        if scale_numeric
        else ["imputer", "imputer", "encoder"]
    )
    for _, frame in calls[:2]:
        assert_array_equal(frame.index, train.index)
    assert_allclose(calls[0][1], train[["n", "constant"]], equal_nan=True)
    assert_array_equal(calls[1][1]["c"].isna(), [False, True, False])
    assert_array_equal(calls[2][1], [["a"], ["__missing__"], ["b"]])
    mean = np.array([3, 7, 1 / 3])
    variance = np.array([6, 0, 2 / 9])
    scale = np.array([np.sqrt(6), 1, np.sqrt(2 / 9)])
    if scale_numeric:
        assert_allclose(calls[3][1], numeric_block)
        assert_allclose(pre.numeric_scaler.mean_, mean)
        assert_allclose(pre.numeric_scaler.var_, variance)
        assert_allclose(pre.numeric_scaler.scale_, scale)
        assert pre.numeric_scaler.n_samples_seen_ == 3
    else:
        assert pre.numeric_scaler is None
    expected_numeric = (numeric_block - mean) / scale if scale_numeric else numeric_block
    assert_allclose(fitted_train[:, :3], expected_numeric)
    assert_allclose(fitted_train[:, 3:], [[0, 1, 0], [1, 0, 0], [0, 0, 1]])

    # Distinct held-out sentinels exercise validation and test independently.
    for outlier, category in [(1_000_003.0, "validation-only"), (-999_997.0, "test-only")]:
        held_out = pd.DataFrame(
            {"n": [outlier, np.nan], "constant": [1007.0, 7.0], "c": [category, None]},
            index=[91, 97],
        )
        result = transform_checked(pre, held_out)
        expected = np.array([[outlier, 1007, 0], [3, 7, 1]])
        if scale_numeric:
            expected = (expected - mean) / scale
        assert result.dtype == np.float64
        assert np.isfinite(result).all()
        assert_allclose(result[:, :3], expected)
        assert_allclose(result[:, 3:], [[0, 0, 0], [1, 0, 0]])
        assert len(calls) == (4 if scale_numeric else 3)  # No fit on either scoring frame.
        assert_array_equal(pre.numeric_imputer.statistics_, [3, 7])
        assert_array_equal(pre.onehot.categories_[0], ["__missing__", "a", "b"])
        if scale_numeric:
            assert_allclose(pre.numeric_scaler.mean_, mean)
            assert_allclose(pre.numeric_scaler.var_, variance)
            assert_allclose(pre.numeric_scaler.scale_, scale)
            assert pre.numeric_scaler.n_samples_seen_ == 3


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
def test_runner_fits_preprocessing_on_inner_train_and_outer_train_only(monkeypatch, family):
    train = pd.DataFrame(
        {"n": [0.0, 1, np.nan, 3, 4, 5, 6, 7], "c": ["a", "b"] * 4},
        index=range(10, 18),
    )
    y = pd.Series([0, 1] * 4, index=train.index)
    test = pd.DataFrame({"n": [1e9, -1e9], "c": ["outer-only"] * 2}, index=[90, 91])
    test_y = pd.Series([0, 1], index=test.index)
    fits = []
    original_structure = DensePreprocessor.fit_structure
    original_scaler = DensePreprocessor.fit_scaler

    def structure(self, X):
        fits.append(("structure", self.scale_numeric, X.copy()))
        return original_structure(self, X)

    def scaler(self, X):
        fits.append(("scaler", self.scale_numeric, X.copy()))
        return original_scaler(self, X)

    monkeypatch.setattr(DensePreprocessor, "fit_structure", structure)
    monkeypatch.setattr(DensePreprocessor, "fit_scaler", scaler)
    # Only preprocessing/caller partitioning is under test; avoid real model search.
    monkeypatch.setattr(runner, "build_estimator", lambda *args, **kwargs: DummyClassifier())
    protocol = runner.BenchmarkProtocol.smoke()
    result = runner._tune_family(train, y, family=family, outer_seed=42, protocol=protocol)
    assert result["all_trials_completed"]
    runner._refit_family(result, train, y, test, test_y, outer_seed=42, protocol=protocol)
    assert result["all_trials_completed"], result["error"]
    expected_frames = [
        train.iloc[fit_index]
        for fit_index, _ in StratifiedKFold(2, shuffle=True, random_state=42).split(train, y)
    ] + [train]
    assert len(fits) == 6
    for (label, scaling, actual), expected in zip(
        fits, [frame for frame in expected_frames for _ in range(2)], strict=True
    ):
        assert label in {"structure", "scaler"}
        assert scaling == (family == "DNN")
        pd.testing.assert_frame_equal(actual, expected)

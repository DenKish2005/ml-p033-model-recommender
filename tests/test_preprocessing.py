"""Hand-computed contracts for fold-local dense preprocessing (T03)."""

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from model_recommender.preprocessing import (
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

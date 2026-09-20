from importlib.metadata import version

from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from model_recommender.features import characterize


def run_demo(seed: int = 42) -> dict:
    dataset = load_breast_cancer(as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(
        dataset.data,
        dataset.target,
        test_size=0.25,
        random_state=seed,
        stratify=dataset.target,
    )
    models = {
        "hist_gradient_boosting": HistGradientBoostingClassifier(random_state=seed),
        "mlp": make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True),
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=seed),
        ),
    }
    scores = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        scores[name] = {
            "balanced_accuracy": float(balanced_accuracy_score(y_test, model.predict(X_test))),
            "roc_auc": float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])),
        }
    return {
        "project": "CSCI447P033",
        "purpose": "Pipeline smoke test; not a validated model recommendation.",
        "dataset": "sklearn:breast_cancer",
        "positive_class": str(dataset.target_names[1]),
        "seed": seed,
        "split": {"method": "stratified_holdout", "train": len(X_train), "test": len(X_test)},
        "meta_features_partition": "train",
        "meta_features": characterize(X_train, y_train),
        "scores": scores,
        "versions": {name: version(name) for name in ("numpy", "pandas", "scikit-learn")},
    }

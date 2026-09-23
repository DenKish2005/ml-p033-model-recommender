# Experiment protocol 0.1

Can training-dataset meta-features select between tuned HistGradientBoostingClassifier and MLPClassifier with less performance loss than a fixed choice? The initial experiment covers binary classification under one preprocessing regime; conclusions apply to these two pipelines, not entire model families.

This protocol is a research plan; the benchmark runner is not yet implemented.

- **Scoring:** balanced accuracy as the primary metric; ROC-AUC, refit time, and search time as secondary measures. Record the positive class for every dataset.
- **Splits:** three stratified 75/25 outer splits with seeds 42, 137, and 2026, with shuffled three-fold inner cross-validation for tuning using the corresponding outer seed. Both models use identical partitions. Patient or temporal structure requires appropriate outer and inner splits registered before fitting. Every training and scoring partition must contain both classes.
- **Preprocessing:** median numeric imputation with missing indicators, constant-token categorical imputation and one-hot encoding that ignores unknown categories, and numeric scaling for the MLP. Preserve empty features. Both models receive dense float64 features (`sparse_output=False` for one-hot encoding). Before allocating each transformed training or scoring matrix, require `n_rows × n_encoded_features × 8` to be at most 512 MiB (536,870,912 bytes); derive the encoded feature count from the fitted training preprocessor. Exclude the dataset from the paired comparison if any matrix exceeds this limit and record the reason. This bounds individual feature matrices, not total process memory. Fit preprocessing only on the current training fold. Exclude identifiers and predictors unavailable at prediction time; extract meta-features from raw outer training data.
- **Tuning:** 20 distinct configurations per model per outer split, including the specified baseline. Sample the other 19 without replacement using tuning seed 42 and reuse the saved candidate order. Select by mean inner balanced accuracy, breaking exact ties by candidate order, then refit on outer training data. This requires 360 inner fits and six refits per dataset; equal trial counts do not imply equal compute time.
- **Failures:** require all 20 configurations to complete all three inner folds for each model on every outer split, plus successful final refits and outer scoring, for a dataset to enter the primary comparison. Exceptions or non-finite predictions or scores count as failures; do not replace failed trials. Convergence warnings alone are not failures: retain finite results at the iteration limit and record the warnings. Report completed trial counts and exclusion reasons, retaining partial results for diagnostics only.
- **Selection:** average paired outer scores and meta-features into one example per dataset. Predict MLP minus GBDT balanced accuracy. Recommend MLP only when its predicted advantage exceeds 0.01; use GBDT otherwise. This practical near-tie rule is not a claim of statistical equivalence.

## Model settings

Disable early stopping for both models and set estimator randomness from the outer seed. Search the Cartesian products below; the baseline counts toward the 20 configurations. Other settings use the locked scikit-learn defaults.

| Model | Parameter | Search values | Baseline |
| --- | --- | --- | --- |
| HistGradientBoostingClassifier | `learning_rate` | 0.03, 0.1 | 0.1 |
| | `max_leaf_nodes` | 15, 31, 63 | 31 |
| | `l2_regularization` | 0, 1, 10 | 0 |
| | `min_samples_leaf` | 10, 20, 40 | 20 |
| MLPClassifier | `hidden_layer_sizes` | (32, 16), (64, 32), (128, 64) | (32, 16) |
| | `alpha` | 0.0001, 0.001, 0.01 | 0.0001 |
| | `learning_rate_init` | 0.0003, 0.001, 0.003 | 0.001 |

Fix GBDT `max_iter` at 200. For the MLP, use `max_iter=500`, `solver="adam"`, and `activation="relu"`.

## Recommender evaluation

Evaluate the recommender on held-out dataset families, keeping duplicate versions and shared cohorts together. Fit recommender transformations and tuning only on training families. Reserve clinical datasets for transfer evaluation after freezing the recommender on nonclinical data. Repeated splits are not independent datasets.

Compare with always choosing each model, the best fixed model selected on training datasets, and an oracle. Report per-dataset results and mean selection regret with equal dataset weights: best candidate balanced accuracy minus selected candidate balanced accuracy, without rounding near-ties to zero.

Next, register five pilot datasets with pinned versions, family membership, clinical status, targets, feature types, and split constraints, then implement the benchmark runner. Version protocol changes before collecting results. A later preprocessing comparison is needed to connect recommendations to the reference paper's feature-engineering findings.

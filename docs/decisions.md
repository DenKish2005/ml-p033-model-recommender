# Research Decisions

This file records decisions that materially affect the scientific interpretation of CSCI447P033.

## D001 — First benchmark compares two concrete pipelines

The first implemented benchmark compares `HistGradientBoostingClassifier` with `MLPClassifier`. Until more models are added, results describe **these two pipelines**, not every GBDT and every deep tabular model.

## D002 — Meta-learning target is a continuous performance gap

The recommender predicts:

`mean balanced accuracy (MLP) - mean balanced accuracy (GBDT)`

This is preferred over direct winner classification because it preserves how large or small the observed advantage is. The actual best pipeline is still recorded for interpretation.

## D003 — Practical recommendation margin

Recommend DNN only when the predicted MLP advantage is **greater than 0.01 balanced-accuracy points**. Otherwise recommend GBDT. This is an operational near-tie rule, not a statistical-equivalence claim.

## D004 — Leakage-safe preprocessing

Every imputer, encoder, and scaler is fitted only on the current training partition. Inner-validation and outer-test rows never participate in preprocessing fit. Meta-features are computed from raw outer-training data only.

## D005 — Equal candidate counts

Each model receives 20 deterministic candidate configurations in the full protocol. Candidate 0 is the documented baseline; the remaining 19 are sampled without replacement using tuning seed 42. The same candidate order is reused across outer splits.

## D006 — Dense-matrix guard

The first protocol uses dense float64 transformed matrices. Before one-hot output is materialized, encoded width is determined and any requested train/validation/test matrix above **512 MiB** is rejected and recorded as a protocol failure.

## D007 — Full versus smoke mode

`full` = 3 outer splits × 20 candidates/model × 3 inner folds and is the only research-valid benchmark mode.

`smoke` = 1 outer split × 2 candidates/model × 2 inner folds and exists only to validate the engineering pipeline quickly.

## D008 — Dataset is the meta-learning observation

One successful full benchmark dataset becomes one meta-dataset row. Repeated outer splits are aggregated and never treated as independent meta-learning samples.

## D009 — Hold out complete dataset families

Recommender evaluation uses complete dataset-family holdouts. Duplicate versions/shared cohorts must remain in the same group to avoid leakage across the meta-learning train/test boundary.

## D010 — Clinical data remain a final transfer holdout

Clinical datasets are not used while designing the initial nonclinical recommender. Their role is external transfer evaluation after the nonclinical pipeline is frozen, with patient-grouped or temporal splits when the source requires them.

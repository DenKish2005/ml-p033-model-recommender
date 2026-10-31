# Data Dictionary

## Registry and review boundary

[configs/datasets.toml](../configs/datasets.toml) is the executable pilot registry.
[DatasetSpec/read_registry/load_dataset](../src/model_recommender/datasets.py)
validate its supported fields; [registry.py](../src/model_recommender/registry.py)
and [openml_loader.py](../src/model_recommender/openml_loader.py) are placeholders.
`openml_id` + `version` + `md5_checksum` pin a source; `name` identifies it in
run/meta artifacts. `positive_class` maps to 1, the other registered label to 0.
Numeric/categorical/excluded lists partition non-target columns. `family` is
source lineage for evaluation, not a claim of row independence; `clinical=false`
for all five pilots. Run/meta schemas remain provisional despite an existing runner.

**P033-003 review date: 2026-10-31 (Asia/Qyzylorda). Metadata only; no dataset
records, ARFF/Parquet/ZIP downloads, benchmarks or upstream execution.** Registry
`verified_on=2026-09-20` and the 2026-10-30 audit are historical, not this review.
The graphify snapshot at `b316b5d` was used for navigation and checked against
current files. New OpenML evidence is retained as a compact, selected-field
[metadata snapshot](sources/pilot_metadata_2026-10-31.json); it is not a raw-data
checksum verification. OpenML `NumberOfFeatures` includes the target: cards state
predictor counts separately. API qualities are publisher-computed metadata,
not newly measured data properties.

`SOURCE ADMITTED` means identified source and evidenced research permissions for
the stated task. It does **not** clear benchmark/result admission, G1, or remaining
P033-004…009 checks. `PENDING` names a specific unresolved source check. The
current loader/runner does not enforce these documentation statuses.

## Permissions and attribution

Each linked UCI dataset page has its own License section explicitly identifying
CC BY 4.0. This is the permission evidence; OpenML's `licence=Public` and public
visibility establish catalogue availability only. Research reuse is supported by
those UCI grants. Redistribution/adaptation is permitted **under the grant's
conditions**, not automatically cleared for a repository release. Follow
[CC BY 4.0 legal code §§2–4](https://creativecommons.org/licenses/by/4.0/legalcode.en)
and [the deed](https://creativecommons.org/licenses/by/4.0/), both read 2026-10-31:
retain supplied creator/copyright/license/disclaimer notices and source link,
link the license, identify modifications and previous modifications, impose no
additional restrictions, and imply no endorsement. Other rights are outside the
grant. Each card supplies its dataset citation; include the OpenML pin and describe
renaming, recoding, merging or filtering when sharing a derived artifact.

The UCI grant is evidence for the underlying dataset linked by OpenML, not proof
of byte identity between providers or a blanket license for every OpenML service
asset. No raw redistribution is performed here; packaging/notice review remains
P033-032/Q10. Repository MIT licensing does not relicense the datasets. No new
registry fields or license/pin substitutions are needed for this documentation.

## credit-g

**Identity and schema.** OpenML **31 / v1**, MD5
`9a475053fed0c26ee95cd4525e50074c`; **1000 × 20 predictors** (21 columns with
target). Live description, feature schema and qualities agree with the registry:
`class`, labels `{bad, good}`, **bad→1, good→0**, 7 numeric + 13 categorical,
no ignored/row-ID columns and no excluded features. Metadata reports zero missing
cells; actual observations and duplicates have not been inspected.

Numeric: `duration`, `credit_amount`, `installment_commitment`, `residence_since`,
`age`, `existing_credits`, `num_dependents`. Categorical: `checking_status`,
`credit_history`, `purpose`, `savings_status`, `employment`, `personal_status`,
`other_parties`, `property_magnitude`, `other_payment_plans`, `housing`, `job`,
`own_telephone`, `foreign_worker`. These are storage/model roles, not a declaration
that ordinal/coded attributes are measurements on an interval scale.

**Source evidence (all accessed 2026-10-31):**

- [OpenML description](https://www.openml.org/api/v1/json/data/31),
  [features](https://www.openml.org/api/v1/json/data/features/31),
  [qualities](https://www.openml.org/api/v1/json/data/qualities/31): identity,
  default target, exact names/types/labels/flags and dimensions; creator Hofmann,
  original UCI link, active/public catalogue status, `licence=Public`.
- [UCI 144](https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data),
  Dataset Information / Creators / Citation / License: Hans Hofmann; symbolic
  original and an edited numeric derivative; dataset-specific CC BY 4.0.
  Citation: Hofmann, H. (1994), *Statlog (German Credit Data)*, UCI,
  [doi:10.24432/C5NC77](https://doi.org/10.24432/C5NC77).
- [Original german.doc](https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.doc),
  §§2–3/6–8: Hofmann at Universität Hamburg; original has 7 numeric/13 categorical
  predictors, numeric derivative 24; UCI good=1/bad=2 coding differs from our
  explicit binary encoding. Original misclassification costs are asymmetric.

**Prediction time and dependence.** Intended scope is static good/bad credit-risk
classification after the listed application attributes are available. History
refers to previous credit; `duration` plausibly denotes loan terms, but the
documentation does not establish exact measurement dates, adjudication horizon
or whether every attribute preceded the outcome. No person/time/group key appears
in the schema; that does not prove unique borrowers or prospective availability.
Sensitive attributes/proxies preclude treating a benchmark score as lending
validation. Balanced accuracy does not reproduce the original cost-sensitive goal.

**Family/policy/status.** `uci-statlog-german-credit` includes symbolic, numeric,
recoded and alternate OpenML copies of this cohort; they cannot supply independent
meta rows or opposite family folds. **SOURCE ADMITTED for the static benchmark
task**, permissions supported by the UCI grant and common conditions above.
P033-008/009 must review exact X/full-row duplicates, conflicting labels and any
recoverable entity links before fitting; retain evidence and do not silently
delete records. Unresolved: original collection/outcome timing, borrower reuse,
actual local integrity and duplicate counts. A prospective lending claim would
require additional evidence and source/task review.

## ionosphere

**Identity and schema.** OpenML **59 / v1**, MD5
`23dd3c8b5693e2848901fd1a0248ef42`; **351 × 34 predictors** (35 columns with
target), `class`, `{b, g}`, **g→1, b→0**. All `a01` through `a34` are numeric;
no categorical/excluded features, ignored columns or row identifiers. Description,
schema and qualities match the registry. Zero missing cells are reported metadata;
constant-column claims in older notes have not been independently measured here.

**Source evidence (all accessed 2026-10-31):**

- [OpenML description](https://www.openml.org/api/v1/json/data/59),
  [features](https://www.openml.org/api/v1/json/data/features/59),
  [qualities](https://www.openml.org/api/v1/json/data/qualities/59): pin, names,
  flags, labels and dimensions; g/b semantics and original UCI lineage.
- [UCI 52](https://archive.ics.uci.edu/dataset/52/ionosphere), Dataset Information /
  Citation / License: radar observations, 351/34, named creators, CC BY 4.0.
  Citation: Sigillito, V., Wing, S., Hutton, L., & Baker, K. (1989), *Ionosphere*,
  UCI, [doi:10.24432/C5W01B](https://doi.org/10.24432/C5W01B).
- [Original ionosphere.names](https://archive.ics.uci.edu/ml/machine-learning-databases/ionosphere/ionosphere.names),
  §§2–8: JHU Applied Physics Laboratory Space Physics Group, donor Vince Sigillito;
  Goose Bay radar, paired complex autocorrelation components across 17 pulses.
  Original method citation: Sigillito et al. (1989), *Classification of radar
  returns from the ionosphere using neural networks*, Johns Hopkins APL Technical
  Digest 10, 262–266. The cited paper was not separately read; its reported scores
  and historical train/test counts are not reproduced evidence.

**Prediction time and dependence.** Classify a processed radar return once all
34 components are available: g indicates ionospheric structure, b its absence.
This is not forecasting future conditions. No schema column identifies a
collection session, pulse-train group, timestamp or site; shared acquisition
conditions could induce dependence. No explicit ID/post-outcome column is
documented, but label-construction independence is not demonstrated. Random
stratified rows do not validate transfer to new sites or collection periods.

**Family/policy/status.** `uci-ionosphere` groups all copies, recodings and subsets
of these observations. **SOURCE ADMITTED for processed-return classification**
under the UCI grant/common attribution conditions. P033-008/009 retain duplicate,
conflict and potential acquisition-group evidence before benchmark admission;
no silent deduplication. Pending: session/entity lineage, actual duplicates,
constant-column/local checksum validation and independent label provenance.

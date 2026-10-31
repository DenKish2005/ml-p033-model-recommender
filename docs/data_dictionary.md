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

## spambase

**Identity and schema.** OpenML **44 / v1**, MD5
`d9ace01aeac3461e326a8e1b2d53fd84`; **4601 × 57 predictors** (58 columns with
target), `class`, labels `{0, 1}` represented as strings, **1→1 (spam), 0→0**.
All 57 predictors are numeric; categorical/excluded lists are empty. The live
schema has no ignored/row-ID fields and agrees with the registry. Exact ordered
names are retained in the [snapshot](sources/pilot_metadata_2026-10-31.json):
48 `word_freq_*`, six character frequencies and three `capital_run_length_*`.
The character fields are literally `char_freq_%3B`, `char_freq_%28`,
`char_freq_%5B`, `char_freq_%21`, `char_freq_%24`, `char_freq_%23` in OpenML;
do not silently decode/rename them to the UCI punctuation names in the loader.

**Source evidence (all accessed 2026-10-31):**

- [OpenML description](https://www.openml.org/api/v1/json/data/44),
  [features](https://www.openml.org/api/v1/json/data/features/44),
  [qualities](https://www.openml.org/api/v1/json/data/qualities/44): matching pin,
  role sets/target labels/dimensions, zero reported missing values and UCI lineage.
- [UCI 94](https://archive.ics.uci.edu/dataset/94/spambase), Dataset Information /
  Creators / Citation / License: email classification, creators and CC BY 4.0.
  Citation: Hopkins, M., Reeber, E., Forman, G., & Suermondt, J. (1999),
  *Spambase*, UCI, [doi:10.24432/C53G6X](https://doi.org/10.24432/C53G6X).
  Its current summary says missing values exist, contrary to OpenML qualities
  and the original documentation. Treat this as a metadata disagreement, not
  evidence that missingness was measured or resolved here.
- [Original spambase.DOCUMENTATION](https://archive.ics.uci.edu/ml/machine-learning-databases/spambase/spambase.DOCUMENTATION),
  §§2/4–9: HP Labs authors, generated June–July 1999; spam from postmaster/filed
  spam, non-spam from personal/work mail; `george`/`650` encode that collection.
  Original documentation states no missing values and 1813 spam/2788 non-spam;
  these are source-reported counts, not a local audit.
- [spambase.names](https://archive.ics.uci.edu/ml/machine-learning-databases/spambase/spambase.names):
  feature definitions and original punctuation names; capital-run statistics
  describe complete-message content, label denotes unsolicited commercial mail.

**Prediction time and dependence.** Scope is classification after receiving the
complete message, before using its label. Word/character frequencies are available
then; no separate outcome-derived column or sender/message/thread/time identifier
is listed. Personal indicators can act as identity/domain shortcuts; absence of
keys does not establish independent senders/messages or exclude repeated campaigns.
This corpus does not establish general-purpose or future-email performance.

**Family/policy/status.** `uci-spambase` groups all copies/recodings/subsets of
this collection. **SOURCE ADMITTED for this historical email corpus**, with UCI
permissions/common attribution conditions. Actual missingness, X/full-row
duplicates, conflicting signatures and any campaign/entity grouping are pending
P033-008/009. Do not strip personal indicators, deduplicate or impute source
disagreements silently: any changed predictors/eligible rows need a recorded
source review and compatible protocol identity before the affected scores.

## adult

**Identity and schema.** OpenML **1590 / v2**, MD5
`bb6510925e5d4b23d136715febb2cdf5`; **48842 × 14 predictors** (15 columns with
target), `class`, `{<=50K, >50K}`, **>50K→1, <=50K→0**. Six numeric:
`age`, `fnlwgt`, `education-num`, `capital-gain`, `capital-loss`, `hours-per-week`.
Eight categorical: `workclass`, `education`, `marital-status`, `occupation`,
`relationship`, `race`, `sex`, `native-country`. No excluded/ignored/row-ID fields.
Live identity/schema/qualities match the registry. OpenML reports 6465 missing
cells in 3620 rows: workclass 2799, occupation 2809, native-country 857; target 0.
These are metadata counts, not new downloaded-data findings. Retain unknowns;
the complete-case 45222-row source variant is not this pin.

**Source evidence (all accessed 2026-10-31):**

- [OpenML description](https://www.openml.org/api/v1/json/data/1590),
  [features](https://www.openml.org/api/v1/json/data/features/1590),
  [qualities](https://www.openml.org/api/v1/json/data/qualities/1590): v2 explicitly
  merges original training and test sets; exact labels have no trailing period.
  These metadata facts do not independently prove the conversion of every row.
- [UCI 2](https://archive.ics.uci.edu/dataset/2/adult), Dataset Information /
  Creators / Citation / License: Becker's extraction from the 1994 Census database,
  48842/14, CC BY 4.0. Citation: Becker, B. & Kohavi, R. (1996), *Adult*, UCI,
  [doi:10.24432/C5XW20](https://doi.org/10.24432/C5XW20).
- [Original adult.names](https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.names),
  opening notes / conversion / final-weight description: original random split
  32561/16281, six duplicate-or-conflicting instances reported without a modern
  audit definition; income threshold from `agrossincome`; `fnlwgt` is a survey
  weight based on demographic/state controls, not a person identifier. The file
  cites Kohavi (1996), *Scaling Up the Accuracy of Naive-Bayes Classifiers: a
  Decision-Tree Hybrid*, KDD; the paper was not independently read in this task.

**Prediction time and dependence.** This is retrospective income classification
from contemporaneous census fields, not prediction of future earnings. Income,
capital gains/losses, hours and occupation can describe the same accounting period;
their availability before a prospective decision is unverified. `fnlwgt` remains
a registered numeric predictor, not a sample weight in the current pipeline.
`education`/`education-num` encode related information. Demographics/relationship
can reveal household structure and sensitive proxies; no household/person/time
key is provided to protect related records. `agrossincome`, a direct target source,
is not a registered predictor. None of these facts proves leak-free independence.

**Family/policy/status.** `uci-adult` covers original partitions, merged/cleaned/
recoded versions and alternate copies from the same extraction, not every distinct
Census dataset merely because of its name. **SOURCE ADMITTED for retrospective
classification**, UCI permissions/common attribution conditions apply. Frozen
random splits over v2 do not reproduce the original split. P033-008/009 must
reconcile duplicate/conflict evidence, actual missingness, local integrity and
any recoverable household/entity links before fitting; do not infer current
duplicate counts from the historical six or delete them automatically. Future
income claims require an independently reviewed time/feature contract.

## tic-tac-toe

**Identity and schema.** OpenML **50 / v1**, MD5
`34b2992c41e5e23c42769817e96305ac`; **958 × 9 predictors** (10 columns with
target). Target is case-sensitive **`Class`** in OpenML (UCI's web table uses
`class`); labels `{negative, positive}`, **positive→1 (x wins), negative→0**.
All nine categorical board cells have values `{x, o, b}` (b means blank, not
missing): `top-left-square`, `top-middle-square`, `top-right-square`,
`middle-left-square`, `middle-middle-square`, `middle-right-square`,
`bottom-left-square`, `bottom-middle-square`, `bottom-right-square`.
Numeric/excluded lists are empty. Live schema/qualities agree with the registry;
zero missing cells, no ignored/row-ID columns are metadata observations.

**Source evidence (all accessed 2026-10-31):**

- [OpenML description](https://www.openml.org/api/v1/json/data/50),
  [features](https://www.openml.org/api/v1/json/data/features/50),
  [qualities](https://www.openml.org/api/v1/json/data/qualities/50): matching pin,
  exact capitalized target, nominal cells/labels and dimensions; David W. Aha.
- [UCI 101](https://archive.ics.uci.edu/dataset/101/tic+tac+toe+endgame), Dataset
  Information / Citation / License: legal endgame configurations, x plays first,
  target is a three-in-a-row win for x; CC BY 4.0. Citation: Aha, D. (1991),
  *Tic-Tac-Toe Endgame*, UCI,
  [doi:10.24432/C5688J](https://doi.org/10.24432/C5688J).
- [Original tic-tac-toe.names](https://archive.ics.uci.edu/ml/machine-learning-databases/tic-tac-toe/tic-tac-toe.names),
  §§2/4–9: creator/donor David W. Aha, 19 August 1991; 958 legal endgame boards,
  cell meanings, no missing values. Initial web-tool access failed; a direct
  HTTPS request successfully read this text documentation (not `.data`).

**Prediction time and dependence.** Recognize an already completed board. The
label is a deterministic rule of those cells, so the task is not forecasting a
winner before game end. Board occupancy is outcome-revealing for that different
task; no attempt is made to remove it and call the same benchmark prospective.
No game/player/move-history identifiers exist in this schema. Rotations/reflections
preserve the label: this is a mathematical relationship of the game, not a newly
measured duplicate count. The source's enumeration claim does not establish
independent games, exact uniqueness of this OpenML copy or symmetry-free splits.

**Family/policy/status.** `uci-tic-tac-toe-endgame` groups all copies, symmetry
transforms and derivatives of this enumeration. **SOURCE ADMITTED for endgame
rule recognition**, with UCI permissions/common attribution conditions.
**Primary benchmark eligibility PENDING** a prospective symmetry/signature review
in P033-008/009 under D019. Do not silently treat rotated boards as independent,
delete equivalents, or introduce grouped splits under frozen 0.1. If equivalent
groups must stay together, register a separate protocol identity and compatible
runs; preserve 0.1 as diagnostic evidence. Quantifying exact/symmetry duplicates
and conflicting labels requires the later authorized data audit. No independent
games or real-world cohort interpretation is admitted by this source review.

## Family and admission conclusions

| Pilot | Family | Source admission for stated task | Before benchmark/result admission |
|---|---|---|---|
| credit-g | uci-statlog-german-credit | ADMITTED, static credit-risk classification | Timing/entity limits; duplicate/conflict/local-integrity audit |
| ionosphere | uci-ionosphere | ADMITTED, processed radar returns | Acquisition-group/label provenance limits; duplicate/local-integrity audit |
| spambase | uci-spambase | ADMITTED, historical email corpus | Missingness disagreement; personal/domain shortcuts; duplicate/entity audit |
| adult | uci-adult | ADMITTED, retrospective income | Historical duplicate/conflict warning; household/weight/timing limits; local audit |
| tic-tac-toe | uci-tic-tac-toe-endgame | ADMITTED, endgame rule recognition | PENDING symmetry policy for primary benchmark; exact/conflict/local audit |

Five distinct registry family names match five different documented source
lineages; they are not a statistical demonstration of five independent samples.
Related versions/cohorts must remain in one family, exact source copies cannot
create independent meta rows, and identified repeated entities must not cross
inner/outer base splits. Family grouping addresses meta-level dependence; it does
not fix row-level leakage. Under [D019](decisions.md#d019--sourcecohortduplicate-policy),
keep original records and audit counts, distinguish X-signature duplicates from
full-row duplicates and conflicting targets, and resolve source-specific
eligibility before fitting. Unknown keys stay unknown. Any correction affecting
rows/predictors/base splits requires recorded identity/compatibility review;
existing outputs are retained rather than relabelled as newly valid.

All sources have UCI permission evidence; no source is admitted solely from
`Public`. All five still await actual data integrity/role/class/missingness and
duplicate audits in P033-009, after the P033-004…008 validity checks. No source
or legal evidence here clears full G1/T09, final artifact publication, clinical
admission or [P033-023](TASK_BACKLOG.md#p033-023--freeze-meta-evaluation-and-optional-nested-selection).
[D012](decisions.md#d012--general-domain-fence-and-feature-allowlist) remains the
general/clinical boundary, and [D017](decisions.md#d017--clinical-split-protocol-requires-source-confirmation)
remains needs confirmation for clinical sources. These five general pilots do
not validate a clinical split engine.

Traceability: FR-001/002 identity/roles checked at metadata level only; FR-003 and
NFR-016 source permissions/citations reviewed for these five tasks; FR-004/006/007,
NFR-001/011/021 and SR-002/003 inform lineage/timing/duplicate safeguards whose
data-level and prospective-manifest implementations remain downstream. This is
the P033-003 subset of T01/T09, not completion of those entire test groups.

## Access and unresolved evidence ledger

- All 15 OpenML description/features/qualities endpoints were read successfully
  with direct HTTPS. Initial web-tool timeout/access failures for 31/59 and
  sandbox DNS failure were access-path failures; permitted direct requests
  resolved them. No pins/checksums were changed to obtain a match.
- All five modern UCI pages, german.doc, ionosphere.names, spambase.names,
  spambase.DOCUMENTATION, adult.names and tic-tac-toe.names were read; legal code
  and deed were read. A guessed static german.doc URL failed; the original
  machine-learning-databases URL above succeeded. Legacy registry URLs remain
  source lineage; use the working modern UCI citations in these cards. DOI values
  are taken from UCI citation sections, not independent DOI-content reviews.
- Pending **P033-008/009**: actual raw-byte checksum, observed schema/classes,
  duplicates/conflicts, missingness reconciliation and source-specific
  entity/symmetry admission. No leakage/duplicates-absent claim is supported.
  Timing/session/household provenance unavailable in the reviewed documentation
  limits prospective/independence claims; it is not filled with invented keys.
- Pending **P033-014/015/023**: expanded source/family eligibility and prospective
  evaluation manifest; **P033-032/Q10**: final derived-artifact notices/publication.
  These are downstream gates, not failed metadata requests or new authorized work.

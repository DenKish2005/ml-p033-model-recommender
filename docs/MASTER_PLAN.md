# CSCI447P033 — MASTER PLAN до воспроизводимой исследовательской сдачи

**Главный entry point. Дата baseline: 2026-10-30.** Студенты: Daniyar Kshibekov, Yerassyl Auyeskhan. Переданный официальный title: **A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data**. Развиваемая система: **Dataset-Aware ML Model Recommender**. Репозиторий: [ml-p033-model-recommender](https://github.com/DenKish2005/ml-p033-model-recommender), audited HEAD `ad17b8b`.

На данном этапе выполнены **аудит и планирование**, а не реализация roadmap. Основной код, frozen protocol и experiment results не изменялись. Дорогие benchmarks и скачивание больших datasets не выполнялись. Все будущие artifacts ниже — цели, не уже полученные результаты.

## 1. Как пользоваться комплектом

1. [PROJECT_AUDIT.md](PROJECT_AUDIT.md): факты о текущем коде,35 passing tests, ограничения и evidence.
2. [REQUIREMENTS.md](REQUIREMENTS.md):40 FR,22 NFR,8 SR; источник/priority/acceptance/verification и полная traceability.
3. [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md): frozen0.1, proposed decisions, datasets, формулы признаков, evaluation/clinical/statistics/compute.
4. [TASK_BACKLOG.md](TASK_BACKLOG.md):38 карточек, первые10 с командами, функции/файлы/dependencies/inputs/outputs/tests/DoD/часы.
5. [TEST_AND_ACCEPTANCE_PLAN.md](TEST_AND_ACCEPTANCE_PLAN.md):14 test groups и gates G0–G6.
6. [FINAL_DELIVERABLES.md](FINAL_DELIVERABLES.md):exact paths outputs,21 report sections,12 slides и demo.
7. [RISKS_AND_OPEN_QUESTIONS.md](RISKS_AND_OPEN_QUESTIONS.md):27 risks,12 questions, fallback и negative-result policy.

Canonical scientific protocol остаётся [experiment-protocol.md](experiment-protocol.md), его alias [experiment_protocol.md](experiment_protocol.md) сохранён. История D001–D010 сохранена. Текущие dispositions D011–D020 — в [decisions.md](decisions.md#d011d020--dispositions-p033-001-2026-10-30): accepted design D011–D014/D019/D020; proposed D015/D016/D018; needs confirmation D017. Accepted design не означает implemented/verified; nested selection, lockbox allocation и numerical upstream attempt отложены до указанных там checks. EXPERIMENT_PLAN синхронизирован с этим ledger, frozen0.1 не изменён.

## 2. Current status и границы требований

Engineering foundation уже существует: pinned5 OpenML registry, raw10 meta-features, duplicate/missingness/conflict audit, dense preprocessing с guard512MiB, deterministic candidates, paired nested tuning и aggregate gap, четыре regression meta-models, family LOGO и regret. **Проверено локально:**35 tests, Ruff и format, lock check19 packages, registry CLI; на HEAD GitHub Ubuntu CI success. Первые ошибки pytest/uv были из-за sandbox Temp/cache, workspace paths позволили успешно повторить проверки.

**Не подтверждено:** real OpenML download/smoke/full и upstream numerical reproduction. **Нет:** реальных benchmark outputs, достаточного meta-dataset, trained/exported recommender, clinical transfer, uncertainty/ablation results, final figures/report/slides. `clinical.py`/`reporting.py` и два scripts — placeholders; registry/openml_loader отдельные модули docstring-only, работающий loader находится в datasets.py.

P0 fixes до expensive runs: result admission mixed smoke/full и fake full; explicit feature allowlist и clinical fence; split_strategy gate и source-level leakage policy; meaningful preprocessing/failure tests. Provenance/recovery добавить до expanded runs. Никакой subjective «проект готов на72%»: software base существенная, empirical research пока на подготовительном этапе, финальная сдача не собрана.

**OFFICIAL:** отдельной university specification/rubric в репозитории нет. ID/title/contributors/objective получены из задания пользователя; deadline, grading weights, mandatory dataset count/report length неизвестны. **REPOSITORY DECISION:** binary HistGBDT vs MLP, BA,3 repeated outer holdouts,3 inner folds,20 candidates и margin.01. **RESEARCH RECOMMENDATION:** strict validation, uncertainty, compact features, Tier B20–30 general datasets/3–5 clinical cohorts. **OPTIONAL:** broader architectures, GUI/API service, landmarking, extensive upstream reproduction. Scope может уменьшаться по ресурсам, но scientific validity не optional.

**P033-001 scope baseline, 2026-10-30:** Tier B выбран рабочей целевой версией по поручению пользователя. Это исследовательский ориентир; dataset counts, 160–260 человеко-часов (190–310 с резервом) и compute scenarios остаются плановыми предположениями до source/resource checks P033-012/014/015/029. OFFICIAL здесь — сведения из пользовательского brief, не независимо проверенная university specification. Полное сопоставление identity, RQ1–RQ3 и текущего кода: [scope baseline в decisions](decisions.md#p033-001--scope-baseline-2026-10-30). `configs/project.toml` сохраняет title расширения, отличающийся от переданного official title и рабочего имени выше; финальный naming/subtitle остаётся Q11, config не переименован. Неизвестная rubric не блокирует независимую работу; соответствие неполученным institutional requirements не сертифицируется.

## 3. Final product vision и research questions

Новый **labelled development tabular dataset** → source/target/feature/split validation → dataset audit → versioned raw descriptors из training-consistent partitions → сохранённый general-trained gap regressor → predicted advantage MLP−GBDT → MLP если>0.01, иначе GBDT → JSON с schema/model/source identities, OOD/fallback reason. Exhaustive benchmarking нужен для research labels/evaluation, а не для каждой inference recommendation. Без development labels нынешние imbalance/entropy features недоступны: label-free API — отдельное расширение.

На research стороне validated full results → one row/source meta-table → held-out-family OOF predictions → fixed baselines/oracle/regret+uncertainty → frozen general recommender → **zero-shot** clinical holdouts → figures/tables/report. Основные ответы: RQ1 unseen-dataset predictive selection, RQ2 stable associations с descriptors, RQ3 general→clinical transfer. Сравнение двух estimators даёт выводы об этих pipelines, не обо всех GBDT/DNN. Отрицательный результат при корректном дизайне считается научно завершённым.

## 4. Целевая архитектура без переписывания существующего проекта

```text
Data sources → configs/datasets.toml → datasets.py → audit.py
                                    ├→ raw training data → features.py
                                    └→ preprocessing.py + model_families.py
                                                     ↓
                                                  runner.py
                                                     ↓
results/raw_model_runs + manifests → meta_dataset.py → recommender.py
                                                       ↓
evaluation.py (family holdouts, baselines, uncertainty) → reporting.py
                                                       ↑
clinical.py (independent public clinical source/splits, frozen inference)

Paper + pinned upstream clone (Linux3.11.7) → reproduction evidence
                    [отдельная ветка; не импорт labels в general meta table]
```

Dataset-level base-model splits отделены от meta-level dataset-family splits. Clinical cohorts не участвуют в general model/feature/hyperparameter selection. Final test outcomes не используются для выбора model/feature/threshold. Source family identity определяется до scores.

```text
configs/                         [существует; сохранять TOML-организацию]
  datasets.toml                  general registry, family/roles/source pins
  datasets/clinical.toml         сейчас planned; будущие clinical source cards
  experiments/                  versioned general/meta/clinical/reproduction decisions
  models/gbdt.toml,dnn.toml       parity с фактическими factories
src/model_recommender/           [существует; не переустраивать ради дерева]
  datasets.py                    DatasetSpec/read_registry/load_dataset (реальная логика)
  registry.py,openml_loader.py    docstrings; не обязательны к наполнению дубликатами
  audit.py                       audit_dataset, source/admission review outputs
  features.py                    characterize + proposed numeric/cat/correlation/schema helpers
  preprocessing.py               DensePreprocessor + checked wrappers
  model_families.py               ModelCandidate/factories/build_estimator
  runner.py                      BenchmarkProtocol + tune/refit/run + future split/provenance checks
  meta_dataset.py                strict admission/conversion/aggregation/allowlist
  recommender.py                 meta-estimators + proposed export/load/fallback
  evaluation.py                  LOGO/regret + proposed metrics/bootstrap/ablation
  clinical.py                    placeholder → adapter/group/time/zero-shot evaluation
  reporting.py                   placeholder → validated tables/figures
  benchmark.py                   separate engineering demo only
  cli.py                         existing CLI + proposed recommend command
scripts/                         existing entry scripts reused, placeholders completed
schemas/                         existing3 schemas tightened/versioned
tests/                           existing tests expanded; new tests only for new contracts
  test_preprocessing.py           planned PH3
  test_model_families.py          planned PH3
  test_cli.py                     planned PH3/14
  test_statistics.py              planned PH13
  test_inference.py               planned PH9/14
  test_reporting.py               planned PH14
data/                            ignored raw/cache/processed; never mandatory upload
artifacts/recommender/            ignored fitted model + manifest; share only if permitted
results/                         future real outputs; explicit publication policy required
  development/                   smoke/synthetic, separate from primary analysis
  raw_model_runs/                canonical full JSON + failures
  manifests/                     source/config/env/splits/meta/evaluation identities
  summaries/                     audits, exclusions, OOF, baselines, uncertainty, clinical
  figures/                       saved-result plots with input fingerprints
docs/                            eight planning docs now; future evidence/report guides
presentation/                    create only PH15: outline + final slides/PDF
external/                        README now; separate upstream clone/env not vendored
notebooks/                       existing5 scaffold notebooks optional analysis views
```

Подробные current status, inputs/dependencies/tests **каждого существующего значимого файла** — в audit tables; proposed functions/new files с contracts — в backlog. Не создавать дополнительные modules, если функции логично помещаются в существующие. Model serialization storage и report формат выбирать при фактической реализации, не устанавливать библиотеки ради плана.

## 5. Detailed Full Roadmap: PH0–PH15

Во всех фазах ниже: steps выполняются по task cards, где указаны функции/inputs/outputs/tests и common DoD. Часы — активная работа, включая review; overlapping tasks в нескольких фазах **не складывать повторно**. Compute counts и time model в EXPERIMENT_PLAN. PH2 может идти независимо от general path; PH10 evaluation protocol freeze нужно сделать **до** PH7 expanded results, даже если код evaluator дорабатывается позднее.

### PHASE 0 — Project Audit and Requirements Freeze

- **Цель/P:** доказательный baseline и проверяемый scope, P0. **Предусловия/зависимости:** current repository/user brief; official rubric если доступна. **Уже:** текущий аудит и этот planning pack; tests/CI baseline.
- **Требуется/steps:** P033-001 определить official unknowns/Tier/resources; P033-003 начать source cards; P033-023 заранее зарегистрировать primary evaluation; пометить accepted/rejected/proposed D011–D020; назначить reviewer и criteria.
- **Существующие files:** docs/decisions.md, configs/project.toml, protocol; **новые:** university source reference только если получен реальный документ, не пустая rubric. **Functions/classes:** не нужны; decisions records input→dated acceptance.
- **Inputs/outputs:** задания/аудит→scope decision, unknown ledger, frozen protocol/meta-selection hashes. **Команды:** `git diff -- docs/decisions.md configs/project.toml`; **тесты/проверка:** T09, category/source/crosslink review.
- **Труд/compute:**2–4h scope +2–4h early evaluation freeze, без ML compute. **Риски:** inventing official constraints, outcome-based redesign. **DoD:** G0; scientific unit/primary model/metric/source rules зафиксированы, unknown rubric честно отмечена.

### PHASE 1 — Research Foundations

- **Цель/P:** определить contribution и limits относительно paper, P1. **Предусловия:** PH0; source reading. **Уже:** reference links/pinned commit, two-pipeline objective/D001–D010.
- **Steps:** P013a прочитать paper methods/appendix; выписать dataset/preprocessing/HPO/evaluation regime; сопоставить с0.1; оформить related-work matrix; сформулировать RQ1–3 и optional RQ4/5 без causal/family overclaim.
- **Files:** existing docs/reproducibility.md/decisions.md; **new:** docs/related_work.md, docs/references.bib при report phase. **Functions:** none, source evidence extraction/review; inputs primary papers→method comparison table.
- **Outputs/commands/tests:** related-work/source notes; read pinned upstream files через GitHub/read-only clone; `git diff -- docs/related_work.md`; T09 проверяет citations/claims. **Correctness:** статья не преподносится как наш BA benchmark.
- **Труд/compute:**2–4h reading+matrix, включено в P013; compute0. **Риски:** неверный research gap/overclaim. **DoD:** distinction reproduction/new contribution/optional extension явна, RQ доказуемы в выбранном scope.

### PHASE 2 — Upstream Reproduction

- **Цель/P:** bounded partial reproduction с настоящими evidence, P1. **Предусловия:** PH1, legal data access/отдельный Linux3.11.7 env; **уже:** helper/checkpoint scripts, upstream not cloned locally.
- **Steps:** P013b–d inspect pinned config/models/requirements; no-submit adapter; isolated setup; source audit; one agreed default/minimalistic attempt; capture failure/success; compare exactly reproduced setting/metric with paper. Не выполнять default direct_submit=true.
- **Files:** scripts/run_reproduction.py, scripts/checkpoint1/*, docs/reproducibility.md; **new:** docs/upstream_reproduction.md, actual results/checkpoint1 logs/manifests. **Functions:** safe subprocess wrapper with timeout/config/environment capture; input separate repo/interpreter/config→evidence JSON/logs.
- **Commands/tests:** safe helper CLI после guard fix, `git -C <upstream-path> rev-parse HEAD`, interpreter `--version`; полные concrete path команды после выбранного clone path. T14 mocked no-submit/exit and manual source comparison; no old stack in modern env.
- **Труд/compute:**6–12h setup/attempt/review beyond PH1; compute отдельно capped после assessment, extensive10-dataset reproduction не обещана. **Риски:** Kaggle/GPU/obsolete dependency/API. **DoD:** reproduced/partial/blocked с reproducible evidence; failure не выдан за numeric match, independent general branch продолжается.

### PHASE 3 — Engineering Validation

- **Цель/P:** доверять supported binary benchmark до дорогих runs, P0. **Предусловия:** PH0; existing working environment. **Уже:**35 tests проходят; rough pipeline implemented.
- **Steps:** P002 CI/portability; P004 preprocessor edge/leakage/guard; P005 candidates/full parity/tie/paired splits; P006 strict admission; P007 clinical+feature fence; P008 unsupported split/class/duplicate gates; P011 provenance/atomic/resume после smoke feedback.
- **Files:** existing datasets/features/preprocessing/factories/runner/meta_dataset/recommender/evaluation/CLI/schema/CI; **new:** tests/test_preprocessing.py, test_model_families.py, test_cli.py. **Functions:** validate_benchmark_result/select_research_results/feature_schema/validate_split/collect_run_metadata/write_result_atomic proposed; precise contracts в cards006–011.
- **Inputs/outputs:** synthetic adversarial frames/results + locked config→passing regression/integration suite и valid result contract. **Commands:** Next10 rows002/004–008; **tests:** T01–T08/T12 contamination; **correctness:** corruption/clinical rows/unsupported split cannot silently pass.
- **Труд/compute:**24–38h включая recovery/CI; cheap tests/stubs, не full. **Риски:** name-only full/config drift/meta leakage. **DoD:** P0 checks green, G1 после real smoke; никакие fixes не меняют frozen settings без decision.

### PHASE 4 — Pilot Benchmark

- **Цель/P:** подтвердить end-to-end на credit-g,ionosphere,spambase,adult,tic-tac-toe; P0→P1. **Предусловия:** source cards, PH3 gates; **уже:**registry5, unit synthetic smoke; real outputs нет.
- **Steps:** P009 fetch/audit5; P010 credit-g smoke затем all5; inspect findings; P012 first full cost; после relevant feature freeze P017 complete full5 с reuse same identity. Full не запускается в текущем planning turn.
- **Files/functions:** reuse loader/audit/run_benchmark/collect script; configs/datasets.toml corrections only verified drift; **new outputs:** development smoke index/audits/full JSON/resource budget; новых modules нет.
- **Input/output:** pinned public pilots→real audit/smoke/full eligibility; **commands:** Next10 rows009–010; позже full CLI P012/017. **Tests/verification:** T01/T02/T04/T05/T08; full actual360 inner+6 refits, smoke10 fits и research_valid=false.
- **Труд/compute:**5–11h active across009/010/012, full completion2–4h active отдельно; smoke50 fits, full5 total1830 (credit-g не считать дважды). **Риски:** source mismatch/adult cost/duplicate bias. **DoD:**M1 реальные5 smoke, M2 first validated full+cost, full-pilot outcomes complete or explicit exclusions.

### PHASE 5 — Dataset Expansion

- **Цель/P:** enough independent diverse nonclinical tasks, P1. **Предусловия:** pilot costs/source policy; **уже:**5 pilots only; proposed shortlist, не registered extra sources.
- **Steps:** P014 verify metadata/terms/map candidates, reject clinical/versions/unsupported tasks before scores; P015 batch pin/fetch/audit/register; coverage matrix n/p/cat/missing/cardinality/imbalance/domain; resource triage; families not artificial n.
- **Files/functions:** configs/datasets.toml, docs/data_dictionary.md, datasets.py validation reuse; **new outputs:** dataset_inventory.csv/admission ledger. `DatasetSpec/read_registry/load_dataset` extend source contract only when needed; input source card→validated LoadedDataset/source manifest.
- **Commands/tests:** `uv run --locked p033 datasets`; fetch/audit per admitted name; T01/T09+metadata/source review. **Correctness:** exact IDs/checksums/positive labels/roles, licence unresolved not silently usable.
- **Труд/compute:**12–24h metadata+registration batches, model compute separatePH7; downloaded sizes prechecked. **Риски:** insufficient independent families/shortlist overlap; **DoD:** target20–30 feasible admitted datasets (или smaller declared Tier A), cohort/source/exclusion/coverage evidence, no selected-by-winner corpus.

### PHASE 6 — Meta-Feature Engineering

- **Цель/P:** defined cheap predictors and compatible inference, P1. **Предусловия:** schema/domain fence, source roles, early feature freeze; **уже:**10 valid v1 descriptors.
- **Steps:** P016 definitions/tests→cheap size/type/missing/cardinality→numeric moments/duplicates/correlation caps→timing; preserve v1; choose compactv2 main/fullv2 ablation; register missing/aggregation policy.
- **Files:** features.py, test_features.py, docs/data_dictionary.md; **new:** no separate feature package needed. **Functions:** characterize reuse; summarize_numeric/categorical/correlations/feature_schema proposed; raw X/y/roles/seed/caps→named numeric features+separate extraction provenance.
- **Outputs/commands/tests:** versioned descriptors and timing; `uv run --locked pytest -q tests/test_features.py`; T02/T10 manual formulas/degenerate inputs; no outcome predictors/no outer-test data.
- **Труд/compute:**8–12h; O(np) cheap stats; correlation sampled O(n p²) with proposed5000×200 caps; not HPO. **Риски:** high p-meta/small n-meta, expensive landmarking; **DoD:** all formula edge cases specified and checked, extraction cheaper measured than exhaustive benchmark, schema freeze before primary evaluation.

### PHASE 7 — Complete Model Benchmarking

- **Цель/P:** consistent full labels for corpus, P1 (validity P0). **Предусловия:** PH3–6, early PH10 freeze, measured budget; **уже:**runner implemented, no real full.
- **Steps:** P017 pilots; P018 new-source smoke then full batches; checkpoint/resume; P019 failures/retries/exclusion bias analysis; retain all candidates even finite warnings; no per-dataset budget changes. Family/model portfolio expansion only P038 separately.
- **Files/functions:** existing runner/model_families/collect script + provenance validators; **new artifacts:** canonical JSON/checkpoints/manifests/exclusions.csv, not new modelling architecture. Inputs validated sources/candidates/splits→paired outer scores+gap.
- **Commands/tests:** existing `collect_openml_results.py --mode full` with explicit selected names after admission; T04/T05/T10; count360+6/dataset, review scores finite/in-range/all paired.
- **Труд/compute:**9–18h active management/failure review;20/30 datasets total7320/10980 fits. Time model separately; several days/weeks plausible on slow CPU, not promised. **Риски:** compute/selection bias/OHE/convergence. **DoD:** all registered experiments attempted/accounted; only complete compatible pairs eligible, partial diagnostics preserved.

### PHASE 8 — Meta-Dataset Construction

- **Цель/P:** scientifically correct row unit and provenance, P0. **Предусловия:** validated full outputs+same schema/split identities; **уже:**basic converter/builder, flaws A01/A04/A06.
- **Steps:** P020 strict admission manifest→canonical source/cohort dedup→equal outer means→gap arithmetic→general-only allowlisted table→snapshot hash; log rejected sources; no treating seeds as rows.
- **Files/functions:** meta_dataset.py/build_meta_dataset.py/schemas; converter/build_meta_dataset reuse + validator from006. **New outputs:**results/meta_dataset.csv/results/manifests/meta_dataset.json; inputs full result set→CSV+manifest+reject ledger.
- **Commands/tests:** `uv run --locked python scripts/build_meta_dataset.py` после fix006; T05/T06 hand aggregation/mixed files/duplicate injection; manual source traceability.
- **Труд/compute:**2–4h, trivial CSV processing; **риски:** forged flags/duplicate source/outcome predictor; **DoD:**G3, one row per selected dataset, compatible complete runs, formula exact, excluded clinical/development rows не leakage.

### PHASE 9 — Recommender Modeling

- **Цель/P:** small-sample regression plus export/inference, P1. **Предусловия:** PH8+predeclaredPH10 policy; **уже:**Dummy/Ridge/tree/RF и gap recommendation.
- **Steps:** P021 fold-local impute/scale; P022 four models+fixed baselines; P025 trusted serialization/schema/domain/fallback/matching descriptor sampler и future CLI recommend; model final all-general fit только после selection/evaluation freeze.
- **Files/functions:** recommender.py/features.py/cli.py/train_recommender.py; make_meta_preprocessor/save/load/characterize_for_recommendation proposed; existing TrainedRecommender reused. **New files:**test_inference.py; artifacts/recommender/model.pkl+manifest.json как outputs.
- **Inputs/outputs:** validated general meta table→fold models/OOF candidates, затем final artifact; labelled unseen development CSV→gap/pipeline/reason. **Commands/tests:**train_recommender existing diagnostic command until export added; T07/T11 roundtrip/no base fit/schema+margin boundaries.
- **Труд/compute:**8–16h incl export; few meta fits vs thousands base fits, RF300 trees internal. **Риски:** in-sample optimism/OOD/unlabelled input expectation; **DoD:**reusable model pipeline+schema, tested inference contract, no training-score claim.

### PHASE 10 — Recommender Evaluation

- **Цель/P:** RQ1 evidence against fixed choice, P0 policy/P1 implementation. **Предусловия:** prospective source/family identities before outcomes for policy; PH8/9 for execution. **Уже:**LOGO/regret/RMSE/simple baselines.
- **Steps:** P023 early primary Ridge/LOGO/regret registration; optional grouped inner tuning only; P024 per-model OOF artifacts/metrics/best-fixed-from-training/CLI output dirs; lockbox if feasible; all four meta-model results secondary, no best-outcome cherry-pick.
- **Files/functions:**evaluation.py/evaluate script/config recommender; extend evaluate_recommender/regret validation, no separate service. **New outputs:**results/manifests/meta_evaluation.json, summaries/recommender/<model>/*; input meta table→per-dataset held-out predictions and baselines.
- **Commands/tests:**evaluate script with `--model` and unique `--predictions`/`--summary`; T07 multirow-family/no-overlap/spied train fixtures; metric manual arithmetic T10.
- **Труд/compute:**5–8h, optional inner selection+3–4h;4×family count meta fits primary. **Риски:** family leakage/post-hoc model selection/tiny n. **DoD:**G4 logical evidence (CIs PH13), every eligible dataset OOF once, all required baselines, primary fixed before final results.

### PHASE 11 — Interpretability and Ablation Studies

- **Цель/P:** RQ2 evidence and error understanding, P1/P2. **Предусловия:**frozen grouped eval/feature versions; **уже:**features available, interpretation absent.
- **Steps:**P027 coefficient stability/feasible held-out permutation; v1/compact/full and feature-group drops; P028 error cases, margin sensitivity, without synthetic/related sources robustness; inspect stable vs unstable patterns.
- **Files/functions:**evaluation.py/reporting.py, optional notebook05; proposed ablation/importance helpers raw meta data+frozen folds→comparison tables; **new outputs:**ablations.csv/feature_importance.csv/error_analysis.csv, tests in test_statistics.py/reporting.py test file.
- **Commands/tests:**future analysis API tested via `uv run --locked pytest -q tests/test_statistics.py`; T10/T13 same folds, transformations train-only, no hardcoded results. Scripts added only if existing evaluate/report CLI cannot own options clearly.
- **Труд/compute:**9–16h incl sensitivity, mostly meta fits; base rerun only if registered preprocessing changes. **Риски:**causal overclaim/unstable importance/multiple testing. **DoD:**paired comparisons and variability, errors/negative findings retained, exploratory labels clear.

### PHASE 12 — Clinical Transfer Evaluation

- **Цель/P:** RQ3 zero-shot general→clinical, P0 gates/P1 results. **Предусловия:**frozen general model/schema/margin, public source cards, grouped/time support; **уже:**policy/config placeholders, no clinical implementation.
- **Steps:**P029 sources/endpoints/permissions; P030 adapter+inner/outer patient/group/time splits and class feasibility; P031 save predictions then independent paired benchmarks, compare fixed baselines, missingness/shift and model hash. Domain-specific fine-tuning separately optional.
- **Files/functions:**clinical.py/run_clinical_evaluation.py/runner.py explicit splitter, clinical config/policy/tests; make_clinical_splits and clinical adapter proposed, raw source+groups/time→development/test partitions; frozen recommender+features→zero-shot predictions.
- **New outputs:**clinical inventory/manifest/summaries; no raw patient data publication. **Commands/tests:**`uv run --locked pytest -q tests/test_clinical.py`; clinical script run arguments defined only after implementation, сейчас raises NotImplementedError. T09/T12, no patient/time/family overlap and no model refit.
- **Труд/compute:**15–28h active;3–5 small cohorts≈1098–1830 fits if identical3×3 design feasible; grouped/time protocol budget separately. **Риски:** follow-up/IDs, severe missingness, clinical n tiny/OOD. **DoD:**G5, genuine independent zero-shot evaluation, per-cohort limitations; no medical deployment claims.

### PHASE 13 — Statistical Analysis and Scientific Conclusions

- **Цель/P:** uncertainty and defensible RQ answers, P1. **Предусловия:**general OOF/clinical results, preregistered comparison; **уже:**point metrics only.
- **Steps:**P026 family-cluster paired regret CI/bootstrap seed; sample unit/conditional uncertainty; P028 robustness/exclusion/near-tie/negative-result interpretation; draft answers with support/unknowns; secondary multiplicity acknowledged.
- **Files/functions:**evaluation.py/test_statistics.py; bootstrap_regret_difference proposed (paired losses+families+seed→estimate/CI/resampling metadata); **new outputs:**uncertainty.json/conclusions table; no new algorithms.
- **Commands/tests:**T10 constant-difference/cluster integrity/seed checks and manual analysis review; no p-values treating repeated outer splits as n=3 datasets.
- **Труд/compute:**3–4h uncertainty + sharedPH11 interpretation,2000 cheap resamples proposed; optional whole-evaluation bootstrap expensive and separate. **Риски:**small effective n/noise/overclaim. **DoD:**each RQ limited to measured data/pipelines, raw regret and intervals present, no gain required to pass.

### PHASE 14 — Reporting and Reproducibility

- **Цель/P:** clean-clone runnable research artifacts and honest figures, P1. **Предусловия:**validated saved results/general model/clinical evaluations; **уже:**basic guides/Makefile but no final outputs.
- **Steps:**P032 artifact allowlist, Windows/CMD/bash commands, source acquisition, clean clone/test/smoke/operator run; P033 tables/figures only from saved results; update old docs without destroying history; link claim→artifact→protocol/env.
- **Files/functions:**reporting.py/make_figures.py, README/ARCHITECTURE/NEXT_STEPS/reproducibility/data dictionary/.gitignore/CI; load_validated_summaries/table builders/figure generator proposed, saved inputs→CSV/SVG/PNG+hash manifest.
- **New files:**test_reporting.py; final figures/manifests (not placeholder files now). **Commands/tests:**existing setup/test workflow; future make_figures only after implementation; T08/T09/T11/T13/T14; visually inspect readability/data alignment.
- **Труд/compute:**10–18h; no full reruns for plotting; independent smoke optional10 fits. **Риски:**accidental raw upload/plot defaults/undocumented deps. **DoD:**M6 reproducible package component, no tokens/patient rows; another reader regenerates tables from licensed saved summaries.

### PHASE 15 — Final Submission and Presentation

- **Цель/P:** complete academic package, P1/P0 final review. **Предусловия:**PH13/14 plus honestPH2 scope; official rubric if received. **Уже:**no report/deck/demo outputs.
- **Steps:**P03421-section report with evidence/citations; P03512-slide story; P036 offline demo; P03770-item RTM status, license/privacy/protocol/claim/source review, submission checklist; include negative findings and unresolved external blockers.
- **Files:**future docs/final_report.md/references.bib/demo_script.md/submission_checklist.md; presentation/outline.md/CSCI447P033_slides.pptx/PDF; functions none beyond tested demo CLI. **Inputs/outputs:**validated artifacts→academic report/slides/demo/reproducible submission manifest.
- **Commands/tests:**run documented offline demo and saved-result regeneration; `git diff --check`; T09/T14 and visual review of exported report/deck when created. No auto git push/destructive Git.
- **Труд/compute:**21–38h active writing/review/demo; compute trivial inference/report export. **Риски:**unverified institution format/unsupported claims. **DoD:**G6: no unresolvedP0, RQ1–3 evidence, actual artifact inventory and independent reproducibility; official compliance only after rubric verified.

## 6. Milestones, critical path и resource budget

| Milestone | Проверяемый outcome / gate | Зависит от |
|---|---|---|
| M0 | requirements/source categories/protocol decisions frozen, G0 | PH0/1 |
| M1 |5 real smoke outcomes, all development-only, engineering findings resolved | PH3/4 |
| M2 |first complete canonical full + measured host budget, G2 | M1 + provenance |
| M3 |admitted independent corpus + all attempted full runs/exclusion ledger + validated meta-table, G3 | M2 + PH5/6/7/8 + early eval freeze |
| M4 |primary held-out family comparison vs fixed baselines, uncertainty, G4 | M3 + PH9/10/13 |
| M5 |frozen zero-shot clinical results, no clinical train, G5 | M4/model freeze + PH12 |
| M6 |regenerable figures/report/slides/demo/evidence checklist, G6 | M5 + PH11/14/15 + honest reproduction scope |

Dependency graph/точный task critical path — в TASK_BACKLOG. Main elapsed bottleneck: expanded benchmarking; main scientific bottlenecks: sufficient independent families, weak gap signal, clinical shift. Upstream access is independent branch and cannot silently substitute for missing RQ1–3 experiments.

Ориентир remaining active labour Tier B **160–260 человеко-часов**, без full numerical upstream study, со reuse existing code; reserve≈20% даёт **190–310 h**. Это effort, не календарный deadline и не сумма фаз с повторяющимися задачами. Engineering task обычно1–4h; большие batch/science tasks разбиты в cards. Двое студентов могут распределять независимые branches, но review/compute/access не ускоряются автоматически вдвое.

Full compute0.1:5 datasets1830 fits;20=7320;30=10980;60=21960. При hypothetical mean fit10s →5.1/20.3/30.5/61h serial estimator time соответственно; при60s →30.5/122/183/366h; preprocessing/I/O add measured overhead. Это **сценарий**, не замер. CPU/RAM/GPU budget UNKNOWN; sklearn baseline GPU не требует. Ресурсы клиники/upstream/optional model portfolios считать отдельно. Управление — cache/provenance/resume/scheduling, без скрытого уменьшения20×3×3.

## 7. Три уровня завершения

Все количества — proposed research scope, не university mandate; n admitted/families публиковать фактически. Negative findings allowed во всех tiers.

| | Tier A — Minimal Viable Research | Tier B — Recommended Final Project | Tier C — Extended / Publication-Oriented |
|---|---|---|---|
| Software | P0 gates, reliable binary pipeline, v1/compact features, fixed Ridge+Dummy/fixed baselines, export/inference, grouped eval | +v2/feature ablation, richer diagnostics/CIs/recovery, all4 meta-models, clean-clone report automation | +broader model adapters/preprocessing regimes/cost experiments, robust nested family selection |
| Datasets |≈15 independent general +2–3 small clinical,5 pilots внутри general; exploratory if fewer |20–30 general +3–5 independent clinical if access/budget, count families |30–60 general +broader clinical sites/cohorts if legally available; overlap all grouped |
| Models/experiments | HistGBDT vs MLP exact0.1; primary LOGO/fixed Ridge, raw regret, source/exclusion review | Same primary; four regressors/baselines, family CI, ablation/margin/OOD, zero-shot clinical |≥2 estimators/family, separate registered pipeline regimes; inner family selection; external lockbox/strong robustness |
| Compute | General≈5490 fits +clinical732–1098 if same design +smoke; all measured separately | General7320–10980 +clinical1098–1830 if applicable +smoke/meta CV | Two-model base10980–21960 before portfolio expansion; K4 doubles to21960–43920 plus regimes; GPU/time budget separately |
| Active effort |≈90–150h, сохраняет validity, сокращает breadth/features/ablations |≈160–260h; reserve190–310h; actual source/setup cost adjusts |Tier B +60–140h minimum,≈220–400h; full upstream portfolio may exceed |
| Results/strength | Reproducible exploratory evidence for RQ1–3 on small selected corpus | Defensible university research package with baselines/uncertainty/limits | Stronger external validity possible; publication не гарантируется количеством packages |
| Limits |Low power, few cohorts, no family claim/causal result |20–30 datasets still small; source-dependent results; two concrete pipelines |Portfolio/resource confounding remains; rigorous scope/compute fairness still required |
| RQ coverage |RQ1 exploratory, RQ2 descriptive, RQ3 small-cohort descriptive |RQ1 held-out comparison, RQ2 stability/ablation, RQ3 zero-shot evidence with uncertainty |Same plus richer family/regime/cost hypotheses; no universal medical utility claim |

Не строить GUI, REST service или произвольную deployment infrastructure до evidence для RQ. API здесь — существующие Python functions/CLI. Optional extensions не имеют права вытеснять dataset quality, fixed baselines, correct splitting или honest reporting.

## 8. Definition of Finished Project

Завершение означает: (1) принят scope/прояснены unknown official requirements; (2) licensed/versioned/audited registry и source/family/split evidence; (3) real complete paired benchmarks в frozen protocols; (4) valid meta-table с source provenance, без clinical/feature leakage; (5) held-out family comparisons со всеми baselines и raw regret/uncertainty; (6) trained/exported general-only recommender с tested labelled inference/fallback; (7) independent clinical zero-shot results/limitations; (8) RQ1–3 answers включают negative/inconclusive findings; (9) final figures/report/presentation/demo sourced from saved artifacts; (10) independent clean-clone test и completed traceability/submission checklist без unresolvedP0. Необязательная победа рекомендателя, универсальный family-level вывод и полное воспроизведение всех upstream experiments в это определение не входят.

Сейчас следующие действия — P033-001…010 из [backlog](TASK_BACKLOG.md). Этот planning turn заканчивается документацией; любые дальнейшие code changes/full experiments — следующий этап выполнения принятого плана.

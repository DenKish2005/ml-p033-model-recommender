# CSCI447P033 — требования и traceability

[Главный план](MASTER_PLAN.md) · [Аудит](PROJECT_AUDIT.md) · [Эксперименты](EXPERIMENT_PLAN.md) · [Тесты](TEST_AND_ACCEPTANCE_PLAN.md) · [Backlog](TASK_BACKLOG.md)

Дата baseline: 2026-10-30. Каталог: **40 FR + 22 NFR + 8 SR = 70 требований**. Это спецификация завершения проекта, а не утверждение, что всё уже реализовано. Текущее покрытие находится в аудите; verification здесь — проверка при будущей приёмке.

## 1. Источники и приоритеты

- **OFFICIAL**: отдельно подтверждённых university requirements нет. Project ID, официальный title, студенты и RQ переданы пользователем; независимая rubric отсутствует. Нельзя выводить из этого обязательный объём datasets, число слайдов, deadline или оценку.
- **REPOSITORY DECISION (RD)**: [experiment-protocol.md](experiment-protocol.md), D001–D010 в [decisions.md](decisions.md). Это действующий binary two-pipeline protocol0.1, а не правило университета.
- **RESEARCH RECOMMENDATION (RR)**: предлагаемый проверяемый минимум качества исследования, требует freeze перед production experiments.
- **OPTIONAL (OP)**: Tier C или расширения; не блокируют Tier A/B.
- **UNKNOWN / TO CONFIRM**: вопросы в [RISKS_AND_OPEN_QUESTIONS.md](RISKS_AND_OPEN_QUESTIONS.md).

P0 — scientific validity/безопасность данных/блокировка запуска; P1 — основной Tier B; P2 — улучшения после основной цепочки; P3 — optional. «Зависимости» в таблицах — IDs требований; task mapping дан ниже. Ссылки T01–T14 означают test groups из test plan. Статус proposed у RR не означает OFFICIAL.

## 2. Functional requirements

Пути `src/model_recommender/` сокращены до `src/…` **только в этой таблице**; `src/datasets.py` означает `src/model_recommender/datasets.py`, а не новый top-level модуль.

| ID / источник / P | Требование и rationale | Implementation files | Зависимости | Acceptance criteria и verification |
|---|---|---|---|---|
| FR-001 RD P0 | Читать versioned registry; запрещать ambiguous identity, overlapping roles и target-as-feature, иначе source не фиксирован | src/datasets.py; configs/datasets.toml | — | Duplicate name/source version, wrong schema/roles отклонены; T01 registry unit tests |
| FR-002 RD P0 | Загружать pinned ID/version и проверять metadata/checksum/shape/types/classes без тихой подмены | src/datasets.py | FR-001 | Mock drift fails; real pilot snapshot соответствует registry; T01/T08 |
| FR-003 RR P0 | Для каждой записи хранить source/license/access/citation evidence с датой, а не только Public | configs/datasets.toml; docs/data_dictionary.md | FR-001 | 100% admitted datasets имеют source card, unresolved licensing → not admitted; T09 manual review |
| FR-004 RR P0 | Сохранять content SHA256, metadata snapshot, cohort/family identity; не дублировать observations под разными names | src/datasets.py; src/meta_dataset.py | FR-002 | Повторный источник/производная версия не создают независимую row; T01/T06 |
| FR-005 RD P0 | Проверять aligned X/y, finite numeric, nonempty predictors, binary labels и допустимые class sizes | src/features.py; src/datasets.py; src/runner.py | FR-002 | Invalid fixtures отклонены до fit с причиной; T01/T02/T04 |
| FR-006 RD P0 | Аудировать exact duplicates, predictor signatures, conflicting labels, missingness/constants; сохранять неизменённый raw source | src/audit.py; scripts/audit_datasets.py | FR-002 | Counts совпадают с ручным fixture; immutable source checksum; T02 |
| FR-007 RR P0 | До benchmarking принять duplicate/group/time/target-availability policy; исключения объяснять до scores | src/runner.py; configs/datasets.toml | FR-006 | Split manifest не пересекает обязательные группы, unsupported strategy rejected; T04/T09 |
| FR-008 RD P0 | Numeric median+indicators, keep_empty; categorical constant+OHE unknown-ignore; scale numeric MLP внутри fit fold | src/preprocessing.py | FR-005 | All numeric/category/mixed/all-missing/unknown fixtures finite с train-defined width; T03 |
| FR-009 RD P0 | Guard dense float64 matrices ≤536870912 B до allocation; диагностировать превышение | src/preprocessing.py; src/runner.py | FR-008 | Boundary accepts, boundary+8 rejects до onehot.transform; T03 |
| FR-010 RD P0 | Fold-local preprocessing; запрет fit на inner validation/outer test; сохранять split identity | src/runner.py; src/preprocessing.py | FR-007/008 | Spy sentinel tests fit indices только training; T03/T04; плюс review source data semantics |
| FR-011 RD P0 | Детерминированные 20 candidates, baseline first, tuning seed42; same partitions для двух pipelines | src/model_families.py; src/runner.py | FR-010 | Candidate uniqueness/order, defaults/TOML parity, split hashes совпадают; T04 |
| FR-012 RD P0 | Full = seeds42/137/2026, .25 test, inner3; smoke=1×2×2 и никогда не scientific | src/runner.py; configs/experiments/general_benchmark.toml | FR-011 | Canonical full validator reject reduced name=full; smoke research_valid=false; T04/T05 |
| FR-013 RD P0 | Выбор HPO по inner mean BA, tie→candidate order, final refit→outer score | src/runner.py | FR-012 | Outer scores не меняют winner HPO; known-score stub выбирает ожидаемый candidate; T04 |
| FR-014 RD P0 | BA primary; positive-class ROC-AUC, search/refit times secondary, finite scores | src/runner.py | FR-013 | Ручной confusion-matrix BA и AUC orientation совпадают; T04 |
| FR-015 RD P0 | Failed trial/fold/refit остаётся diagnostic; all-required success для admission; warnings≠exceptions | src/runner.py | FR-012 | Exception/NaN/incomplete folds exclude whole paired dataset, no replacement; finite convergence-warning retained; T04/T05 |
| FR-016 RR P1 | Structured warnings/errors, run ID, timestamps, progress; interruption/resume с atomic writes | src/runner.py; scripts/collect_openml_results.py | FR-015 | Interrupted fixture не создаёт valid partial final, resume не повторяет verified completed unit; T05 |
| FR-017 RR P0 | Версионировать run schema/protocol/config/candidates/features; provenance git/packages/hardware/checksum | schemas/model_run.schema.json; src/runner.py | FR-004/012 | Каждый admitted run связывает source+code+config+environment; T05/T09 |
| FR-018 RR P0 | Explicit result admission manifest: valid full только, с report обо всех rejects | src/meta_dataset.py; scripts/build_meta_dataset.py | FR-015/017 | Mixed smoke/full/excluded/malformed input даёт predictable accepted set и reasons; corrupted/full mismatch rejected; T06 |
| FR-019 RD P0 | One dataset row; mean paired BA и raw outer-train meta-features; gap=MLP−GBDT | src/meta_dataset.py; src/runner.py | FR-018 | Known triples → exact means/gap; repeated splits не rows; duplicate identity fails; T06 |
| FR-020 RD P0 | Метапризнаки только из разрешённых raw training observations; outcome/ID/provenance не predictors | src/features.py; src/meta_dataset.py | FR-010/019 | Versioned allowlist reject unexpected numeric outcome; T02/T06/T07 |
| FR-021 RR P1 | Versioned extended features с missing/degenerate definitions и deterministic sampling | src/features.py; docs/data_dictionary.md | FR-020 | Все формулы из experiment plan проверены handmade fixtures, repeatable timing; T02 |
| FR-022 RR P1 | Meta preprocessing imputation/scaling/feature selection fit только meta-train families | src/recommender.py; src/evaluation.py | FR-020 | Held-out sentinel не влияет на fitted statistics; undefined feature indicators сохраняются; T07 |
| FR-023 RD P1 | Dummy/Ridge/tree/RF regress gap; >.01→DNN else GBDT; margin config persisted | src/recommender.py | FR-022 | Boundary 0/.01/.010001 и finite output проверены; T07 |
| FR-024 RD P0 | Recommender evaluation на complete unseen families; no derivative versions on both sides | src/evaluation.py | FR-004/023 | Train/test family and cohort intersections empty; predictions exactly once per eligible dataset; T07 |
| FR-025 RR P1 | Fixed primary Ridge или nested grouped meta-selection; запрещён выбор main model по final scores | src/evaluation.py; configs/experiments/recommender.toml | FR-024 | Split/model-selection manifest фиксируется до final, inner folds не видят outer; T07/T09 |
| FR-026 RD P0 | Сравнить always GBDT/MLP, best fixed selected on meta-train, Dummy и oracle | src/evaluation.py | FR-024 | Обе fixed losses и fold-local selected fixed; oracle regret0; all four meta-models report separately; T07 |
| FR-027 RR P1 | Per-dataset MAE/RMSE/accuracy/balanced accuracy где defined, raw regret, win/loss/near-tie | src/evaluation.py | FR-026 | Табличный ручной fixture совпадает; absent winner-class metric=NA с причиной; T07 |
| FR-028 RR P1 | Paired dataset/family bootstrap CIs; margin sensitivity; uncertainty не маскировать equivalence | src/evaluation.py | FR-027 | Seeded resampling manifest, family clusters intact, CI of paired regret difference; T10 |
| FR-029 RR P1 | Сохранять trusted model + feature schema/config/training-domain manifest; version compatibility check | src/recommender.py; scripts/train_recommender.py | FR-025 | Export/load roundtrip даёт равные predictions; corrupted/incompatible rejected; T11 |
| FR-030 RR P1 | Inference для нового labelled development dataset без benchmark outcomes и с training-consistent descriptors | src/cli.py; src/features.py; src/recommender.py | FR-021/029 | Held-out CSV→gap/recommendation JSON без calls base-model.fit; target excluded; T11 |
| FR-031 RR P1 | OOD/missing unsupported inputs дают понятный отказ либо logged best-fixed fallback | src/recommender.py; src/cli.py | FR-030 | No silent fabricated prediction; fallback_reason/model provenance есть; T11 |
| FR-032 RD P0 | Clinical data excluded из nonclinical train/selection/preprocessing/hyperparameter decisions | src/meta_dataset.py; src/recommender.py; src/evaluation.py | FR-024 | clinical=true row в general training raises; tests deliberate contamination; T12 |
| FR-033 RR P0 | Clinical source card: outcome, prediction time, patient/group/time, availability, missing/imbalance/license | src/clinical.py; configs/datasets/clinical.toml | FR-003/007 | Каждый holdout admitted по checklist; неизвестный group structure документирован, не выдан за защищённый; T09/T12 |
| FR-034 RD P1 | Frozen nonclinical recommender zero-shot→clinical; отдельный clinical benchmark для labels/regret | src/clinical.py; scripts/run_clinical_evaluation.py | FR-029/032/033 | Hash модели неизменен; клинические scores не влияют на recommendation; T12 |
| FR-035 RR P1 | Interpretability и ablation внутри grouped evaluation, не causal importance claims | src/evaluation.py; src/reporting.py | FR-025/028 | Feature groups removal, coefficients/permutation stability and error cases reproducible; T10 |
| FR-036 RR P1 | Tables/figures только из saved validated artifacts; no hardcoded favourable results | src/reporting.py; scripts/make_figures.py | FR-027/028/034 | Каждая figure имеет input hash/units/labels/sample size и regenerates; T13 |
| FR-037 RR P1 | CLI documented, help/errors/exit statuses predictable; API service/GUI не требуется | src/cli.py; scripts/*.py; README.md | FR-030/036 | Invalid input exit≠0, batch failure summary clear, smoke visibly marked; T08/T11 |
| FR-038 RR P1 | Upstream environment/evidence отдельно, no-submit по умолчанию, reproduction scope честно указан | scripts/run_reproduction.py; docs/reproducibility.md | FR-003 | Pinned Git/Python/config/log/exit metadata; no outbound submission in local verification; T14 |
| FR-039 RR P0 | Unit/integration/synthetic E2E/schema/leakage checks in CI; real network optional manual job | tests/; .github/workflows/ci.yml | FR-018/024/032 | All offline tests green на supported OS; CI не считает docstring coverage; T01–T14 |
| FR-040 RR P1 | Clean-clone guide, report/presentation/demo and RQ evidence trail | docs/reproducibility.md; docs/FINAL_DELIVERABLES.md; README.md | FR-036/038/039 | Independent operator regenerates chosen public smoke + all saved-result tables; final outputs ledger complete; T09/T13/T14 |

## 3. Non-functional requirements

Все численные budget thresholds ниже, кроме frozen dense guard, — **proposed acceptance procedures**. Их замена требует записанного resource decision до experiments.

| ID / P | Измеримый контракт и rationale | Файлы / зависимости | Verification и acceptance |
|---|---|---|---|
| NFR-001 P0 | Reproducibility: source/config/code/environment fingerprints на 100% admitted runs | runner.py; FR-017 | T05/T09, manifest completeness=100%, no unknown version |
| NFR-002 P1 | Determinism: identical candidates/splits; scores на том же host/lock repeat within proposed atol1e-10; timing исключён | model_families.py/runner.py; FR-011 | T04/T10; при недетерминированном BLAS записать measured tolerance/threads до final |
| NFR-003 P1 | Code quality: Ruff и format без ошибок; tests green | pyproject.toml/CI; FR-039 | T08, exits0; covered scenarios важнее arbitrary coverage percent |
| NFR-004 P1 | Maintainability: protocol constants↔TOML проверяются автоматически | configs/tests; FR-012 | T04; drift fixture fails; protocol update versioned |
| NFR-005 P1 | Modularity: reporting не fit; inference не benchmark; imports no network/training | reporting.py/recommender.py; FR-030/036 | T11/T13 monkeypatch fit/fetch to raise, import/help works |
| NFR-006 P2 | Extensibility: optional third estimator через factory + schema identity, не переписывая split engine | model_families.py; FR-011 | T04 adapter contract test; Tier C only |
| NFR-007 P1 | Compatibility: fresh locked sync + offline suite на Windows и Ubuntu с Python3.14.7 | CI/uv.lock; FR-039 | T08; две OS green, upstream остаётся3.11.7/Linux |
| NFR-008 P1 | Performance: измерить 3 repeats extraction/inference и pilot search, record median/max/hardware | features.py/runner.py; FR-021 | T10; proposed extractor+recommend cost <10% измеренного paired benchmark, иначе убрать дорогие features или явно признать failed efficiency hypothesis |
| NFR-009 P0 | Memory: frozen per-matrix512MiB; RSS измеряется отдельно, no false total-memory guarantee | preprocessing.py; FR-009 | T03/T10; allocations rejected before OHE; observed peak RSS≤заранее выбранного host budget |
| NFR-010 P1 | Compute budget: fit count ledger до запуска; per-dataset estimate и resource cap approved internally | collect_openml_results.py; FR-016 | T09; actual fits vs expected366 tracked; cap stops scheduling, не меняет configured trials |
| NFR-011 P0 | Traceability: каждое final table cell/recommendation ведёт к valid run/model manifest | reporting.py; FR-017/036 | T09/T13 full artifact dependency walk without orphan inputs |
| NFR-012 P1 | Portability: команды без make для CMD/PowerShell/bash; no absolute machine paths in configs | README/reproducibility.md; FR-037 | T08/T14 execute documented smoke sequence per supported platform |
| NFR-013 P0 | Dependency management: lock check passes, no opportunistic upgrade mid-experiment | pyproject.toml/uv.lock; FR-017 | T08; `uv sync --locked`; changed lock→new experiment identity |
| NFR-014 P0 | Security: не commit tokens/env/patient identifiers; no untrusted pickle loading | .gitignore/recommender.py; FR-029 | T09 source/artifact review + synthetic corrupt artifact; only locally produced trusted serialization |
| NFR-015 P0 | Privacy: публикуются aggregate clinical summaries, no record-level clinical rows/log samples | clinical.py/reporting.py; FR-033 | T09/T12 inspect outputs; zero patient IDs/rows; local raw storage ignored |
| NFR-016 P0 | Licensing: 100% admitted datasets имеют reviewed permissions/citation; redistribution отдельно | registry/docs; FR-003 | T09 source evidence ledger; UNKNOWN licence prevents publication/admission decision |
| NFR-017 P1 | Logging: all failures/warnings attributable dataset/split/model/trial; no sensitive payload | runner.py; FR-015/016 | T04/T05 injected failure message has IDs, no raw rows |
| NFR-018 P1 | Testability: fast default suite offline; expensive/network cases explicitly opt-in | tests/CI; FR-039 | T08 socket-disabled offline run; proposed <5 min on CI, baseline timing recorded before threshold freeze |
| NFR-019 P1 | CI reliability: timeout/concurrency, deterministic deps; flaky test не лечится unlimited retries | CI; FR-039 | T08 2 consecutive clean runs after infra change, investigate failure before rerun |
| NFR-020 P1 | Documentation: internal links resolve; commands exist or marked proposed; no conflicting canonical protocol | docs/README; FR-040 | T09 link/identifier command review; all eight planning docs crosslinked |
| NFR-021 P0 | Scientific integrity: retain negative results/exclusions; no post-score dataset curation | experiment plan/registry; FR-018/025 | T09/T10 frozen candidate manifest + exclusion ledger + all baselines |
| NFR-022 P1 | Recovery/storage: atomic writes, checksum gate for skip/resume; generated raw/model blobs ignored | runner/scripts/.gitignore; FR-016/017 | T05 simulated interrupted write/resume; no valid partial or accidental overwrite different identity |

## 4. Scientific requirements

| ID / источник / P | Контракт | Зависимости / implementation | Acceptance / verification |
|---|---|---|---|
| SR-001 RD P0 | RQ1 о **двух pipelines**; не переносить результаты на целые families | FR-012/026; experiment/report | T09 scope review; title/abstract/results согласованы |
| SR-002 RR P0 | Статистическая единица dataset/family; three outer splits зависимы, не independent n | FR-019/028; evaluation.py | T10 bootstrap clusters и stated effective n |
| SR-003 RR P0 | До final evaluation freeze inclusion/exclusion, outcomes, primary model/metric, meta partitions | FR-003/025; decisions.md | T09 dated manifest before scores; deviations separately reported |
| SR-004 RD P0 | RQ3 zero-shot nonclinical→clinical; target labels разрешены только в clinical development subset для descriptors | FR-032/034; clinical.py | T12 model hash/general-only training list unchanged |
| SR-005 RR P1 | RQ2 associations: regularized coefficient/permutation/ablation uncertainty; causal выводы запрещены | FR-035; evaluation/reporting | T10/T13 stability across held-out groups; report caveat |
| SR-006 RR P0 | Отрицательный/неопределённый результат завершает корректное исследование; победа не criterion | FR-026/028/040; report | T09 все baselines и CI published; no gain claim if not supported |
| SR-007 RR P1 | Upstream reproduction — отдельная partial reproduction, не равнозначная новому benchmark | FR-038; reproducibility/report | T14 reproduced/not reproduced/not attempted table с причинами |
| SR-008 OP P3 | Family-level выводы только после multiple models/family и inner family selection | NFR-006/FR-025; Tier C config | T04/T09 separate registered scope; outer model cherry-pick запрещён |

## 5. Requirements Traceability Matrix

Каждый ID включён в строку с verification. RQ0 — инженерная достоверность, RQ4 — дополнительный cost/robustness вопрос. Report section numbers определены в [FINAL_DELIVERABLES.md](FINAL_DELIVERABLES.md). Пути будущих artifacts здесь — целевые, не существующие результаты.

| RQ | Requirements (каждый ID применяется) | Module / tasks | Experiment/test | Result artifact | Report sections |
|---|---|---|---|---|---|
| RQ0/RQ1 | FR-001, FR-002, FR-004, FR-005 | datasets; P033-003/014/015 | T01/T08; source audit | results/summaries/dataset_inventory.csv | 7,8,21 |
| RQ0/RQ3 | FR-003, FR-006, FR-007, FR-033 | audit/clinical; P033-003/008/029 | T02/T09/T12 | results/summaries/dataset_audits/; docs/data_dictionary.md | 8,14,17 |
| RQ1 | FR-008, FR-009, FR-010 | preprocessing; P033-004 | T03 leakage/guard | results/raw_model_runs/; split manifests | 7,10,17 |
| RQ1 | FR-011, FR-012, FR-013, FR-014, FR-015 | factories/runner; P033-005/017 | T04/T05 paired benchmark | results/raw_model_runs/*.full.json | 10,12,21 |
| RQ0 | FR-016, FR-017, FR-037, FR-039 | CLI/runner/CI; P033-011/032 | T05/T08 | results/logs/; results/manifests/ | 7,21 |
| RQ1 | FR-018, FR-019, FR-020 | meta_dataset; P033-006/007/020 | T06 | results/meta_dataset.csv; results/manifests/meta_dataset.json | 9,11,12 |
| RQ1/RQ2 | FR-021, FR-022, FR-023 | features/recommender; P033-016/021/022 | T02/T07 | results/summaries/meta_features.csv; recommender manifest | 9,11 |
| RQ1 | FR-024, FR-025, FR-026, FR-027 | evaluation; P033-023/024 | T07 grouped evaluation | results/summaries/recommender/ | 11,12,13 |
| RQ1/RQ2 | FR-028, FR-035 | evaluation; P033-026/027/028 | T10 CIs/ablation | results/summaries/uncertainty.json; ablations.csv | 12,15,16 |
| RQ1/RQ4 | FR-029, FR-030, FR-031 | recommender/CLI; P033-025 | T11 inference | artifacts/recommender/; results/summaries/inference_demo.json | 11,21 |
| RQ3 | FR-032, FR-034 | clinical; P033-007/030/031 | T12 transfer | results/summaries/clinical_transfer/ | 14,16,17 |
| RQ0/RQ1–3 | FR-036, FR-040 | reporting/docs; P033-032…037 | T09/T13/T14 | results/figures/; docs/final_report.md; presentation/ | 1–21 |
| RQ0 | FR-038 | reproduction; P033-013 | T14 | results/checkpoint1/; docs/upstream_reproduction.md | 6,21 |
| RQ0 | NFR-001, NFR-002, NFR-004, NFR-007, NFR-012, NFR-013 | runner/config/CI; P033-005/011/032 | T04/T05/T08/T14 | results/manifests/environment.json | 7,21 |
| RQ0/RQ4 | NFR-003, NFR-005, NFR-006, NFR-008, NFR-009, NFR-010 | src/tests; P033-004/012/018/038 | T03/T04/T08/T10/T11/T13 | results/summaries/resource_budget.csv | 7,10,16 |
| RQ0/RQ3 | NFR-011, NFR-014, NFR-015, NFR-016, NFR-017, NFR-022 | provenance/clinical/storage; P033-003/011/029/032 | T05/T09/T12/T13 | license/source cards; results/manifests/ | 8,14,17,21 |
| RQ0 | NFR-018, NFR-019, NFR-020, NFR-021 | CI/docs; P033-002/032/037 | T08/T09/T10 | CI URL; docs/submission_checklist.md | 16,17,21 |
| RQ1–3 | SR-001, SR-002, SR-003, SR-004 | methodology; P033-001/023/030 | T09/T10/T12 | decisions; meta split manifest | 3,4,7,14 |
| RQ2/RQ0 | SR-005, SR-006, SR-007, SR-008 | analysis/reproduction; P033-013/027/034/038 | T04/T09/T10/T13/T14 | report; ablations; reproduction evidence | 6,15–20 |

Финальная приёмка: заполнить для каждого ID evidence URI/commit/run/test result и actual status. Наличие строки traceability сейчас не делает требование DONE. Для Tier A/B SR-008 и NFR-006 имеют explicit out-of-scope, а не «выполнено».

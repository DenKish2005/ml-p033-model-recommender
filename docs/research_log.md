# Research Log

## 2026-10-31 — P033-005 Protocol and candidate parity

Выполнена только [P033-005](TASK_BACKLOG.md#p033-005--protocol-and-candidate-parity):
candidate/settings/signature/selection/partition success-path subset T04, relevant
T03/T08/T09. Traceability: FR-010 train-only/paired identity, FR-011 candidate
determinism/parity, FR-012 canonical configuration and development-only smoke,
FR-013 inner selection/refit, FR-014 hand BA/AUC and FR-039 offline checks;
NFR-002 candidate/split determinism (не research-score reproducibility),
NFR-003/004/007/010/013/018/020 в пределах этих checks. Broader FR-012 artifact
admission и FR-015 failure semantics здесь не закрыты. Это новое evidence,
отдельно от historical audit35, P033-002 suite38 и P033-004 suite92.

**Baseline/navigation.** Initial main clean; `git fetch origin` подтвердил
`main=origin/main=97ec721e1f145c1b0ff0e4c15ca858d89fda6fd1`. Применимых AGENTS.md
в ancestors/рабочем дереве не найдено. Graphify skill/README прочитаны, interpreter
отдельный от project env. Из реального vocabulary выбраны `candidate sampling
baseline protocol inner selection paired partitions refit`; query budget2000
дал163 nodes,53 показаны (truncated). Навигационные источники: paired partitions
в protocol/Splits, candidates_for_family/model_families и _tune_family/_refit_family
в runner. Snapshot564 nodes/1124 links/39 communities отражает source b8505f4;
conclusions проверены по current code/config/tests/docs. Snapshot не обновлялся,
query/cache artifacts не включены в commits. До edits locked offline suite:
**92 passed / 25.41s**. Python3.14.7, uv0.12.18 и dependencies/lock сохранены.
Дата — Asia/Qyzylorda; active time отдельно не измерялось.

**Новые contracts/evidence.**

- Independent expected SEARCH/BASELINE/SETTINGS из frozen0.1 проверяют все
  Cartesian values (GBDT54, MLP27), baseline0, model/family/order, default20
  distinct candidates, same seed/count/order, changed non-baseline sample,
  without-replacement/full-grid, count1/invalid boundaries и unknown family.
  Изменение returned dictionaries не затрагивает globals/other candidates/calls.
- Все explicit TOML model settings, search и baseline сверены с independent
  expected values и factories; exact key sets не позволяют silently skip fields.
  TOML hidden_layer_sizes lists явно преобразуются в tuples; Python candidates
  сохраняют tuples. Constructors для всех54/27 candidates и outer seeds42/137/2026:
  correct class/params/random_state, GBDT max_iter200, MLP max_iter500/adam/relu,
  early_stopping=False, scaling только DNN. Остальные params сравниваются
  отдельно с defaults installed locked sklearn1.9.1; estimators здесь не fit.
- Full signature42/137/2026, .25, inner3,20/family, tuning42,536870912 B, margin.01;
  smoke42/.25/inner2/2 candidates. Experiment TOML parity и unknown-name errors.
  Arithmetic и actual stub ledger различают full360 inner fits+6 refits и smoke8+2.
- Real train_test_split/StratifiedKFold и preprocessing; estimator fits/scores
  controlled. Shuffled non-positional row IDs, complete matrices-to-raw-row map,
  y-index/value assertions и exact ordered ledgers сравнивают каждую family,
  candidate/fold, outer refit/scoring. Preprocessor structure/scaler fit только
  inner train/outer train, descriptors только raw outer train; valid/test не fit.
  Проверены tuning seed42/order reuse и estimator outer seed. Selected candidate
  refit на всех60 outer-training rows и score только на20 outer-test rows.
- Literal mean-inner-BA winner. Baseline имеет лучший отдельный fold, last fold
  в full и AUC, но меньший mean BA. Меняющиеся outer-score preferences не меняют
  winner; outer scoring вызывается только для selected candidate. Winners меняются
  на outer seed137, sampling order остаётся тем же. Exact .5 tie с порядком списка
  [7,2,5] выбирает candidate_order2, независимо от list-first/AUC/last-fold.
  Hand confusion fixture: specificity3/4, sensitivity1/2 → BA.625; positive-class
  AUC6/8=.75. Existing real-estimator synthetic runner regression сохранён.

**Mutation evidence/defects.** Temporary script под ignored artifacts/p033005
поменял GBDT max_iter200→201, MLP baseline hidden (32,16)→(32,17) и full
inner_folds3→4 по одному. Каждый actual pytest дал1 failed именно на value
assertion; каждый config восстановлен original bytes через finally, после
восстановления focused **34 passed / 7.76s**. Первый wrapper излишне требовал
слово AssertionError в pytest output; исправлен только ignored probe wrapper,
затем три probes повторены успешно. Намеренный drift не commit/push.
**Production defects не выявлены, fixes не требовались**: src/configs/schemas,
registry/pins, frozen protocol/decisions, pyproject/Python/lock без изменений.

**Финальная локальная проверка (Windows, existing locked env, exits0):**

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'artifacts/uv_cache'
$env:TEMP = Join-Path (Get-Location) 'artifacts/p033005/temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP,'artifacts/p033005/tests' | Out-Null
uv run --locked --offline pytest -q tests/test_model_families.py tests/test_runner.py --basetemp=artifacts/p033005/tests/focused-final --tb=short
uv run --locked --offline pytest -q tests/test_preprocessing.py --basetemp=artifacts/p033005/tests/preprocessing-final --tb=short
uv run --locked --offline pytest -q --basetemp=artifacts/p033005/tests/full-final --tb=short
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv lock --check --offline
git diff --check
```

Actual: **41 focused passed / 10.98s** (27 model +14 runner), **54 preprocessing
passed / 7.87s**, **132 full-suite passed / 12.29s** = prior92 +40 new cases.
Ruff all checks passed; format68 files already formatted; lock19 resolved.
Default conftest socket guard сохранён, disposable basetemp parent создан заранее.
Docs paths/anchors/table widths/task/requirement IDs и diff/cached whitespace
проверены; self-review, без заявления independent human acceptance.

**Небольшие commits, push и actual CI (Windows и Ubuntu jobs/steps):**

- `0f8aa89` — `test(models): verify frozen candidate grids and sampling`:
  candidate block18 green; [CI 41217173010](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41217173010)
  success, обе OS, install/lock/lint/format и два offline pytest steps.
- `4c07222` — `test(protocol): check model and benchmark settings against TOML`:
  estimator/default/TOML/signature parity и restored-drift verification;
  [CI 41217435064](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41217435064)
  success, обе OS и все обязательные steps.
- `d14e0e0` — `test(runner): verify inner selection and paired partitions`:
  controlled selection/tie/partitions/refit ledger и hand BA/AUC;
  [CI 41217726546](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41217726546)
  success, обе OS и все обязательные steps. Actual logs: Windows132 passed /
  10.31s и5.05s; Ubuntu132 passed / 4.95s и2.34s; lock/lint/format green.
- Завершающий `docs(plan): record P033-005 verification and remaining gates`:
  backlog/research log и current master/test-plan navigation; hash и final CI
  берутся из Git history/completion handoff, будущая self-reference не выдумана.

Каждый implementation block проверен локально, diff/staged review и explicit
file staging, main перед commit и каждым `git push origin main`. Push success;
между push дожидались Windows/Ubuntu CI предыдущего. Branches/PR/force/amend/
reset не использовались; чужих изменений не было. Historical audit/decisions
сохранены. Docs обновлены только в статусе, evidence и remaining gates.

**Результат/пределы.** P033-005 DONE в scope своей карточки. P033-006 READY по
dependency005, не начата; P033-023 DECISION. Fake/reduced-full admission не
проверяется этими full-configuration stubs; stub output не published research
artifact. Failed trial/refit/non-finite/warning paths, admission/provenance/schema
и split-strategy/duplicate/group/source policies остаются P033-006/008/009/011/019.
Tic-tac-toe primary eligibility pending symmetry review и Spambase missingness
disagreement сохранены. P033-003 source admission не равно benchmark readiness;
unit tests не исключают semantic leakage. Matrix limit относится к отдельному
output matrix, не total RSS. Реальные datasets/smoke/full/benchmarks/upstream не
скачивались/не запускались, resource/clinical/evaluation gates и весь G1 не закрыты.

## 2026-10-31 — P033-004 Preprocessor edge/leakage verification

Выполнена только [P033-004](TASK_BACKLOG.md#p033-004--preprocessor-edgeleakage-verification):
T03 и preprocessing subset T04/T08/T09, FR-008/009 и train-only fitting subset
FR-010; NFR-003/007/009/013/018/020 в пределах приведённых checks. Это не полное
закрытие FR-010 (split identity/source semantics) или NFR-009 (measured host RSS).
Initial `main` clean, fetch подтвердил `main=origin/main=f286463`; применимых
AGENTS.md не найдено. Работа непосредственно в main, explicit file staging,
небольшие commits/push разрешены пользовательским handoff; branches/PR/force/
amend/reset не использовались. Дата — Asia/Qyzylorda; active time не измерялось.

**Navigation/baseline.** graphify skill/README/query использованы отдельно от
project environment. Initial query `DensePreprocessor preprocessing imputer scaler`
дал93 nodes с budget1800 truncation. Повторная exact-vocabulary проверка обнаружила,
что `imputer` отсутствует как отдельный token; исправленный query:
`graphify query 'dense preprocessing scaler numeric' --budget 1800`, все четыре
tokens присутствуют в graph vocabulary. Snapshot492 nodes на `b316b5d` — только
navigation, не current evidence. Выводы сверены с preprocessing.py, runner.py и model_families.py,
актуальными tests/docs/protocol/decisions/requirements/CI/lock. Graph snapshot не
обновлялся; созданный query cache stamp удалён. Исторический audit35 tests и
P033-002/003 baseline38 не выданы за новые preprocessing checks. Новая проверка
до edits: **38 passed / 11.40s**, locked offline. Project Python3.14.7, uv0.12.18,
numpy2.5.3, pandas3.0.6, sklearn1.9.1, pytest9.1.1, Ruff0.16.8 сохранены.

**Failing regressions → минимальные fixes → green (красные commits не публиковались):**

- Initial roles/missingness run: **10 failed / 21 passed**. Object `None` кодировался
  как `c_None` вместо missing token; `pd.NA` в object/string давал ambiguous-NA
  exception; полностью пустая categorical Series с dtype category передавалась
  sklearn как float64 и отвергала string fill; bool/nullable boolean не проходили
  imputer. `_categorical_frame` приводит categorical block к object, все pandas
  missing representations к `np.nan`, bool values к строкам для совместимости
  с `__missing__` в OHE. Numeric/categorical roles не менялись: bool categorical.
  Object/str/string/category × None/nan/pd.NA cases сохранены с exact assertions.
  После fix focused+existing runner **32 passed / 10.30s**.
- Train-only block: **36 passed / 9.81s** вместе с runner. Manual fixture numeric
  `[0, NA, 6]` имеет median3, imputed variance6; indicator mean1/3, variance2/9;
  constant numeric7 имеет scale1. Проверены imputer statistics, encoder categories,
  scaler mean/var/scale/n_samples, concrete train/scoring values; validation/test
  sentinels не вызывают fit и не меняют параметры. Spies проверяют exact imputer
  fit indices и encoder/scaler inputs. При DNN scaler получает numeric+indicators,
  OHE остаётся 0/1. Отдельный caller test обеих families сравнивает все raw
  inner-training/outer-refit frames с partitions; DummyClassifier заменяет только
  estimator, preprocessing/splits настоящие. Existing synthetic runner test сохранён.
- Direct default guard regression до fix: **DID NOT RAISE MatrixTooLargeError**,
  OHE вызван. Использована искусственная fitted width с одной scoring row без
  большой matrix. Ещё четыре red cases показывали отсутствие keyword limit у
  direct transform; checked fit/scoring guard cases уже были green. Теперь guard
  внутри `DensePreprocessor.transform`, keyword `limit_bytes` default536870912;
  wrappers передают тот же custom limit, fit wrapper сохраняет pre-scaler check.
  Limit per call: custom wrapper limit не становится новым default прямого метода.
- Schema/refit probe: **3 failed / 13 passed**. Дубликаты extra columns молча
  игнорировались на fit/transform; failed checked refit оставлял `_ready=True`.
  Early uniqueness validation и `_ready=False` перед structure refit устранили
  эти воспроизводимые нарушения. Duplicate numeric/categorical/extra columns и
  missing required columns теперь покрыты вместе с readiness regression.
- Guard fixtures: training width5 = 1 numeric +1 indicator +3 OHE, matrix120 B.
  Limit120 допускается; limit112 отклоняет превышение на8 B до numeric-imputer
  output/scaler fit/scaler transform/OHE/hstack (monkeypatch spies). Проверены
  fit_transform_checked, transform_checked и direct transform при scaling False/True,
  unknown-only scoring fixed width, actual output nbytes, custom limit forwarding
  ниже/выше default, integer estimate без overflow и default512MiB=536870912 B.
  Large inputs/outputs не создавались. После fixes focused+runner **55 passed / 10.51s**.

**Compatibility/границы.** Scientific settings, median/indicator/OHE/scaling
contract, role inference, default matrix limit, frozen0.1, candidate configs,
registry/source pins, Python/pyproject/uv.lock сохранены. Корректные ранее
поддержанные fixtures дают прежние значения; ранее ошибочные/неверно imputing
NA/bool inputs могут дать другой encoded output. Старые artifacts не становятся
valid автоматически: reuse требует downstream provenance/admission checks.
`transform(X)` теперь защищён default guard; callers с custom limit используют
checked wrappers или `transform(X, limit_bytes=...)`. Direct transform после
failed refit отклоняется до allocations. Это per-output-matrix bound: categorical
original-width object intermediate нужен уже для fit_structure; imputation,
scaling copies, concatenation и coexistence train/scoring arrays могут увеличить
RSS. Peak RSS/host budget не измерены. Unit tests не доказывают отсутствие
semantic target leakage, shared entities/cohorts или symmetry leakage.

**Финальные локальные команды/results (workspace workaround):**

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'artifacts/uv_cache'
$env:TEMP = Join-Path (Get-Location) 'artifacts/p033004/temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP,'artifacts/p033004/tests' | Out-Null
uv run --locked --offline pytest -q tests/test_preprocessing.py --basetemp=artifacts/p033004/tests/focused-final --tb=short
uv run --locked --offline pytest -q tests/test_runner.py --basetemp=artifacts/p033004/tests/runner-final --tb=short
uv run --locked --offline pytest -q --basetemp=artifacts/p033004/tests/full --tb=short
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv lock --check --offline
git diff --check
```

Actual: **54 focused passed / 7.32s**, **1 runner passed / 9.80s**,
**92 full-suite passed / 12.84s**. Full92 = previous38 +54 new preprocessing cases;
counts не являются coverage percentage. Ruff all checks passed, format66 files
already formatted, lock19 packages resolved, exits0. Basetemp parent создан
заранее; existing environment сохранена, dependency installs/upgrades не нужны.
T09 static/self-review: affected Markdown links/anchors, table widths, task/requirement
identifiers и whitespace checks проходят; changes только source/test и status/evidence
docs. Independent human peer review не заявлен.

**Небольшие commits/push и actual hosted CI:**

- `525ea50` — `fix(preprocessing): normalize categorical missingness and bool inputs`:
  first roles/missingness regressions и minimal normalization fix.
  [CI 41183953569](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41183953569)
  success, Windows/Ubuntu jobs и install/lock/lint/format/оба offline tests steps.
- `3262826` — `test(preprocessing): verify train-only imputation and scaling`:
  exact fitted/scoring values, fit spies, runner partitions обеих families.
  [CI 41184062580](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41184062580)
  success, обе OS и все обязательные steps.
- `adbb478` — `fix(preprocessing): enforce checked dense allocation contract`:
  boundaries/direct guard/custom limits, duplicate validation, refit readiness.
  [CI 41184297674](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41184297674)
  success. Actual logs: Ubuntu **92 passed / 5.89s / 2.86s**, Windows
  **92 passed / 8.95s / 3.92s**; lock/lint/format green, fresh hosted installs.
- Завершающий `docs(plan): record P033-004 validation and remaining gates`:
  backlog/research log, current master navigation и T03 row согласованы.
  Его hash/CI берутся из Git history/итогового handoff, будущий hash не выдуман
  внутри commit. Перед каждым commit/push branch main проверена, diffs и staged
  diff просмотрены, explicit files staged; push origin main success для блоков выше.
  Все CI failures отсутствуют, blind reruns не делались.

**Результат:** P033-004 DONE в synthetic preprocessing acceptance scope.
P033-005 READY по dependency004, не начата; P033-023 остаётся DECISION. G1,
source-specific benchmark readiness и remaining requirements не объявлены DONE.
P033-003 source admission не заменяет P033-008/009: tic-tac-toe primary eligibility
pending symmetry review; Spambase missingness disagreement и остальные source
limitations сохранены. Source dedup/group/symmetry implementation не выполнялась;
datasets не скачивались, реальные smoke/full/benchmarks/upstream не запускались.
Decision ledger и historical audit сохранены; общий research package ещё не готов.

## 2026-10-31 — P033-003 Five pilot source cards

Выполнена только [P033-003](TASK_BACKLOG.md#p033-003--пять-pilot-source-cards):
metadata/source/admission review пяти pilots, T01/T09 в пределах этой карточки.
Initial `main` clean, `git fetch origin` подтвердил `main=origin/main=59eafd8`;
применимых AGENTS.md в ancestors/рабочем дереве не найдено. Работа/небольшие
commits/push непосредственно в main по явному поручению пользователя; branches,
PR, force/amend/reset не использовались, чужих изменений не было. Дата доступа —
2026-10-31, Asia/Qyzylorda; active time отдельно не измерялось, ML compute0.

**Навигация и чтение.** Прочитаны master/audit/backlog/common DoD, requirements,
T01/T09/test gates, decisions (особенно D012/D017/D019), risks, dictionary,
clinical policy, reproducibility, registry, actual DatasetSpec/read_registry/
load_dataset, existing mocked registry/loader tests и CI. Graphify отдельно от
locked project env: system Python3.12, `reflect --if-stale`, vocabulary expansion
`source admission registry family duplicate license`, BFS query `--budget 2500`.
Снимок `b316b5d`: 492 nodes, 885 links; budget вернул 63 из 89 найденных nodes,
поэтому вывод использован только как карта файлов. Current datasets.py/tests и
primary sources проверены отдельно; placeholder registry.py/openml_loader.py и
roadmap nodes не выданы за implementation. Query feedback/navigation bookkeeping
сохранены под ignored `artifacts/p033003`; опубликованный graph snapshot не обновлялся.

**Новые evidence, не повторение исторического аудита.**

- [Dictionary](data_dictionary.md) содержит пять cards: source ID/version/MD5,
  dimensions/target/labels/positive mapping, feature roles, author/citation,
  prediction-time/ID/post-outcome/entity/version/family review, permissions,
  duplicate policy и unresolved gates. Полные списки schema names и selected
  metadata fields — [dated JSON snapshot](sources/pilot_metadata_2026-10-31.json),
  единственный supporting source artifact; это не raw data и не полный API dump.
- Прочитаны 15 OpenML JSON endpoints: `/api/v1/json/data/{31,59,44,1590,50}`,
  `/data/features/{id}`, `/data/qualities/{id}`; все direct URLs в cards/snapshot.
  Временный comparison script проверил каждое identity field, exact label/role
  sets, expected rows/column counts, numeric/symbolic counts (с target), все
  `is_ignore/is_row_identifier=false`, сумму per-feature missingness; все MATCH.
  Positive encoding сопоставлено с текущим loader/registry и source semantics.
  MD5 только сравнен с published metadata: скачанных bytes для hashing нет.
- Все пять modern UCI dataset pages (144/52/94/2/101) прочитаны, включая
  source-specific License/Citation/Creators; original german.doc,
  ionosphere.names, spambase.names и spambase.DOCUMENTATION, adult.names,
  tic-tac-toe.names; CC BY 4.0 deed и legal code. Access date/sections/direct
  URLs/citations записаны в dictionary. DOI values взяты из UCI citation
  sections; referenced method papers/DOI content отдельно не исследовались.
- `Public` — прежнее catalogue field, не permissions proof. Каждый UCI source
  page явно указывает CC BY 4.0; research reuse имеет source evidence,
  redistribution/adaptation сохраняют attribution/license/change/notice
  conditions. Это не certification всех иных прав и не publication clearance
  будущих artifacts. Registry `license`, verified_on, legacy URLs и pins
  сохранены, новых неподдерживаемых loader fields нет; source identity и
  совместимость старых outputs не менялись и не объявлялись validated заново.

**Admission outcome.** Credit-g source-admitted для static risk classification,
ionosphere — processed radar returns, spambase — historical email corpus,
adult — retrospective income classification, tic-tac-toe — endgame recognition.
Это source-level решения, не готовность к benchmark/result admission. Для
credit-g неизвестны точный outcome horizon/measurement time/повторные borrowers;
ionosphere — session/entity/label provenance; spambase — personal/domain shortcuts
и missingness disagreement между UCI web summary и original/OpenML metadata;
adult — historical duplicate/conflicting warning (не новый count), household
dependence и contemporaneous features/weight. Tic-tac-toe label определяется
конечной доской, не future winner; **primary eligibility PENDING symmetry review
P033-008/009**. У всех actual duplicates/conflicts/local integrity не проверялись.

Source-specific lineage groups и no-silent-dedup D019 записаны; group/dedup/
row/predictor/split corrections требуют отдельной identity и совместимых runs,
не тихого изменения frozen0.1. Metadata row-ID flags не доказывают independence.
Новых clinical sources нет; D012 fence остаётся обязательным, D017 needs
confirmation, P033-023 **DECISION** (manifest этим review не создан).

**Access failures и разрешение.** Initial OpenML web tool timeout/access failure,
sandbox DNS и `.git/FETCH_HEAD` write denial разрешены permitted direct HTTPS /
Git execution. У guessed static german.doc URL и web tic-tac-toe.names был
failure; original german.doc URL и direct HTTPS tic-tac-toe.names успешно
прочитаны. Нет нерешённого access blocker для использованных источников; нет
подмены source/pin/permission или заявления pass по failed request. Ограничения
timing/session/household evidence остались unknown в cards.

**Проверки (Windows PowerShell, exit0):** перед командами создан parent
`artifacts/p033003/tests`; workspace `UV_CACHE_DIR=artifacts/uv_cache`,
`TEMP/TMP=artifacts/p033003/temp` по reproducibility guide.

```text
uv run --locked --offline p033 datasets --output artifacts/p033003/registry.json
uv run --locked --offline pytest -q tests/test_datasets.py --basetemp=artifacts/p033003/tests/registry --tb=short
uv run --locked --offline p033 datasets --output artifacts/p033003/registry-final.json
uv lock --check --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline pytest -q --basetemp=artifacts/p033003/tests/final --tb=short
```

Registry/loader tests: **21 passed / 5.53s**; full locked socket-blocked suite:
**38 passed / 10.96s**. Ruff all checks passed, format 66 files unchanged,
lock19 resolved packages. Dataset registry CLI offline, not OpenML fetch.
No new tests/code/dependencies for documentation-only changes. T09 static
self-review: links/anchors/table widths/task+requirement IDs resolve, per-card
citations checked against actually read sources, diff/staged whitespace checks
passed. Scope traceability: FR-001/002 metadata subset, FR-003/NFR-016 permission
evidence, FR-004/006/007 source policy, NFR-001/011/020/021 and SR-002/003 boundaries.
Это не complete T01/T09/70-requirement acceptance и не independent human review.

**Небольшие commits и реальный CI:**

- `47b18f4` — `docs(data): document credit-g and ionosphere source evidence`:
  первая пара cards, review/permissions contract и selected-field metadata.
  После checks/staged review push origin main success.
  [CI 41183011946](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41183011946):
  Windows/Ubuntu jobs и install/lock/lint/format/оба offline suite steps success.
- `59b83d1` — `docs(data): review remaining pilot source admission`: остальные
  три cards, snapshot, family/admission/access conclusions. После metadata/docs/
  full suite/quality checks и staged review push origin main success.
  [CI 41183236859](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41183236859):
  Windows/Ubuntu jobs и install/lock/lint/format/оба offline suite steps success.
- Финальный `docs(plan): record P033-003 validation and source limits`:
  backlog acceptance/status и эта запись; master status/navigation исправлены,
  поскольку иначе main entry point ошибочно называл завершённую P033-003 READY.
  Hash и последний CI run — в Git history/итоговом handoff; будущий hash/status
  не выдумываются внутри самого commit. Decisions не менялись.

**Common DoD/result.** Пять доказательных source cards существуют, current
metadata и разрешения для заявленных задач сверены, lineage/time/role/duplicate
unknowns явно переданы соответствующим downstream gates; acceptance карточки
выполнен. Перед каждым commit diff/checks, explicit file staging, staged review/
check; main проверен перед commit и push. Changes ограничены dictionary,
supporting metadata snapshot, backlog/research log и необходимыми master status
updates. Frozen protocol/alias, configs, ML, Python/dependencies/lock сохранены.
Datasets/benchmarks/smoke/full/upstream не запускались; output scores отсутствуют.

**P033-003 DONE только в metadata/source-review scope; P033-004 READY, не начата.**
Pending: data audit и actual source-specific benchmark admission P033-008/009,
в том числе tic-tac-toe symmetry, expanded family/manifest P033-014/015/023,
publication notices P033-032/Q10 и внешние unknowns предыдущего ledger.
Они не блокируют synthetic preprocessing verification P033-004. G1/PH0/M0/
финальный research package этим review не закрыты; P033-023 остаётся DECISION.

## 2026-09-24 — Benchmark implementation milestone

Implemented the next engineering stage of CSCI447P033:

- leakage-safe numeric/categorical preprocessing;
- pre-allocation dense matrix memory guard;
- deterministic HistGradientBoosting and MLP candidate sets;
- paired outer/inner benchmark runner;
- convergence-warning and failure logging;
- duplicate/conflicting-signature dataset audit;
- development `smoke` versus research `full` modes;
- one-row-per-dataset meta-dataset builder;
- regression recommender target (`MLP - GBDT` balanced accuracy);
- held-out dataset-family recommender evaluation and regret metrics.

Local synthetic/unit validation passes. Real OpenML smoke/full results still need to be collected on the user's machine/network environment.

## 2026-10-30 — P033-001 scope and research decisions

Выполнена только [P033-001](TASK_BACKLOG.md#p033-001--scope-и-research-decisions): согласованный documentation baseline перед engineering, на основе пользовательского поручения, planning snapshot `8b1ef51`, девяти перечисленных project documents/config и локального чтения relevant code. Применимых AGENTS.md в ancestors/root/docs/configs и поиске рабочего дерева не найдено. Исходно `main...origin/main [ahead 1]`, working tree чистое; существующий commit `8b1ef51` сохранён, создана ветка `codex/p033-001-scope-freeze`.

Зафиксированы [scope/source categories и RQ/code mapping](decisions.md#p033-001--scope-baseline-2026-10-30): OFFICIAL означает сведения brief, сохранённые в planning docs, без независимой university verification. ID CSCI447P033 совпадает; official title, reference title в config и working extension name разделены, final naming Q11 не подтверждён; `configs/project.toml` сохранён. Tier B — рабочая цель по поручению пользователя, 20–30 general / 3–5 clinical cohorts и effort/compute scenarios остаются planning assumptions до resource/source admission. Никаких новых external facts, rubric, deadlines или institutional obligations не добавлено.

В [D011–D020 ledger](decisions.md#d011d020--dispositions-p033-001-2026-10-30) для каждого решения записаны rationale, sources/assumptions, protocol compatibility, зависимости, verification timing и tasks. Accepted design: D011 strict admission/provenance, D012 domain/predictor fence, D013 fixed scaled Ridgeα1, D014 family LOGO/paired regret, D019 cohort/entity grouping/no silent dedup, D020 bounded no-submit reproduction. Proposed: D015 sampler, D016 v2/NA policy, D018 bootstrap/sensitivity. D017 needs confirmation по clinical endpoints/keys/folds. Nested selection/lockbox allocation и numerical upstream attempt deferred до соответствующих checks. Accepted design не означает implemented/verified или empirical success.

Scientific boundaries сохранены: HistGradientBoosting vs MLP pipelines, mean BA gap MLP−GBDT, margin0.01 operational (не equivalence), одна row/dataset, complete family holdouts, clinical исключены из general fitting/selection, separate zero-shot transfer. Negative/inconclusive результат допустим при корректной оценке. P033-023 остаётся **DECISION**: перенести baseline D013/D014 и подтвердить source/family/feature/sampler/uncertainty/secondary policies в prospective timestamp/hash manifest до P033-018/final results. Manifest не создан, будущая задача не выполнена; PH0/M0 целиком не закрыты.

Локальные commits по ходу работы:

- `ea1de5a` — `docs(scope): define P033 research scope and requirement sources`: decisions/master/risks, identity/RQ/Tier/source baseline.
- `b6b88e0` — `docs(research): record decisions and unresolved assumptions`: D011–D020 и согласование master/risks/experiment plan. EXPERIMENT_PLAN изменён из-за реального противоречия blanket PROPOSED и утверждённого вида compact schema текущим dispositions; frozen experiment settings не менялись.
- Завершающий блок `docs(plan): reconcile scope baseline and task status` — backlog acceptance/status, master progress, эта запись; его hash берётся из Git history, самоссылку будущего hash в commit не записываем.

Проверки P033-001 (diff/staged review перед каждым commit; итоговый static check полного baseline после записи D011–D020, documentation scope):

- Просмотр diff/logical block и явного списка staged files, `git diff --check` / `git diff --cached --check` без ошибок.
- Локальный Python static check: Markdown relative paths/anchors всех затронутых docs существуют; columns таблиц согласованы; P033 IDs разрешаются в task cards; D001–D020 уникальны/полны, каждый D011–D020 содержит все поля.
- Сравнение с `8b1ef51`: D001–D010 сохранены текстово, frozen `experiment-protocol.md`/alias и все configs/code/scripts/schemas/tests/dependencies без diff. Проверены ID/title в TOML и code target/margin/LOGO; future protections по наличию кода не объявлялись verified.
- T09 self-review против steps/acceptance P033-001: категории источников, scope, assumptions/dispositions, prohibition final-outcome tuning и traceability согласованы; checklist в карточке. Полный project T09 со source admission/final evidence и независимый human review не выполнены и не заявлены. Новые ML tests не добавлялись, suite/benchmarks/dataset downloads/upstream не запускались; прежние 35 tests остаются evidence аудита, не новой проверки.

**Результат:** P033-001 DONE только в указанном объёме. Внешние unknowns: Q01 rubric/deadline/format, Q02 ресурсы, Q03 доступные active hours, Q06 фактический corpus/families/permissions, Q08 clinical sources/keys/endpoints, Q09 upstream access/env/no-submit feasibility, Q11 naming. Source duplicate policies, exact schema/sampler, bootstrap feasibility и publication policy остаются будущими research checks с task mapping в risks/decisions. Они не останавливают независимую работу: **P033-002 READY**, не начата; остальные engineering tasks этим этапом не выполнялись. Push/amend/destructive Git operations не выполнялись.

## 2026-10-30 — P033-002 Environment and CI portability

Работа только по [P033-002](TASK_BACKLOG.md#p033-002--environment-и-ci-portability), T08 environment/offline CI, FR-039 и NFR-003/007/012/013/018/019/020. На старте `main` clean, `git fetch origin` подтвердил main=origin/main=`2ed54bd`; применимых AGENTS.md не найдено. Пользователь явно разрешил небольшие commits/push непосредственно в main. Чужих изменений не было, branches/PR/force/amend/reset не создавались. Даты — 2026-10-30 в Asia/Qyzylorda; active time отдельно не измерялось.

**Изменения:** CI matrix Ubuntu/Windows, uv 0.12.18, Python из `.python-version`, locked sync, explicit offline lock/Ruff/format, 15-minute job и 5-minute install/test timeouts, concurrency, fail-fast false, два pytest processes/job и fresh environments без restored cache. Make check/test используют locked/offline commands. Default pytest socket-blocked; network marker требует `--run-network`, unmarked tests остаются offline даже с этим flag. Добавлены три regressions для accidental socket/connection/DNS; новые live/download tests не добавлены. Подробные [shell commands, evidence и limitations](reproducibility.md#portable-locked-setup-p033-002) синхронизированы с README/master/backlog/test plan.

**Новые локальные evidence, не результаты прежнего аудита:** Windows 11 build 26200, PowerShell; системный Python3.12.10 отличается от project3.14.7. uv0.12.18, gh2.96.0; numpy2.5.3/pandas3.0.6/scikit-learn1.9.1/pytest9.1.1/Ruff0.16.8 совпали с lock. До edits:35 passed/11.66s. После edits в existing `.venv`:38 passed/9.66s и10.04s, exit0; lock/Ruff/format exit0 (19 resolved packages/63 format units). CLI help/registry exit0. Existing `.venv` не удалялась/не пересоздавалась.

**Фактическая установка:** первая новая `artifacts/p033002/clean-env` с пустым cache упала на sandbox DNS к files.pythonhosted.org; partial env сохранена, это failed install. Повтор с разрешённым network в другой новой `artifacts/p033002/clean-env-2`: `uv sync --locked --python .venv/Scripts/python.exe`, workspace UV_CACHE_DIR/TEMP/TMP, **19 packages installed**, exit0; `uv pip check` compatible19. Suite в ней:38 passed/24.34s и10.59s. Не dry-run и не переименование существующей env. CMD/Git Bash с warmed cache фактически установили ещё по19 packages в новых `cmd-env`/`bash-env` и выполнили lock/lint/format, два suite runs и CLI help/registry: exit0. Начальные managed-Python lock/MSYS sandbox denials разрешены permitted execution. Ubuntu локально не запускалась; Linux evidence — hosted Ubuntu CI. Temporary opt-in probe без connections/DNS: default1 passed/1 skipped, flag2 passed, unmarked test всё ещё blocked.

**Небольшие implementation commits/push по ходу работы:**

- `12670b1` — `ci: validate locked environment on Windows and Ubuntu`: CI matrix/checks, Make targets, conftest opt-in/guard и три regressions. После local double suite/clean install/lock/lint/format, diff/staged review — push origin main success.
- `567320d` — `ci: create pytest workspace before offline checks`: исправление обнаруженного реальным CI missing basetemp parent; setup-uv cache-local-path вместо переопределяемого env. На новой локальной parent path дважды38 passed/7.65s и9.75s, lock/Ruff/format green; staged review, отдельный commit/push origin main success.
- Documentation block `docs: record portable setup and P033-002 validation`: commands/evidence/acceptance/statuses; hash берётся из Git history после commit, без self-reference будущего hash.

**Реальный remote CI и NFR-019:**

- [41019463627](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41019463627) на `12670b1`: failure обе OS,34 passed/4 setup errors (FileNotFoundError: parent artifacts/ci отсутствует). Clean installs, lock/lint/format прошли. Локально parent уже создали setup checks, поэтому defect проявился только clean runner. Причина исследована по обоим job logs; blind rerun failure не делался.
- [41019812975 attempt1](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41019812975/attempts/1) на `567320d`: success обе OS. Ubuntu24.04.5:17 applicable packages installed,38 passed/4.49s и1.73s; Windows Server2025 build26100:19 installed,38 passed/5.60s и1.71s. Python3.14.7, uv0.12.18, lock/Ruff/format green.
- [41019812975 attempt2](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41019812975/attempts/2), полный повтор **успешного** run на том же SHA: success обе OS, новые hosted jobs/checkouts/interpreters/env/install без cache restore. Ubuntu38 passed/4.52s и1.88s; Windows38 passed/5.28s и1.57s. Это два последовательных clean matrix attempts после infra fix, а не только два tests в одной env. Статусы/шаги/логи прочитаны через GitHub API/CLI; push-runs listing через gh, поскольку connector commit-workflow wrapper фильтрует PR-triggered events.

**Common DoD/self-review:** перед каждым commit просмотрены diff и staged diff, explicit file staging, `git diff --check`/cached check, относящиеся block checks, local Markdown paths/anchors/identifiers. Сравнение с `2ed54bd` подтвердило отсутствие изменений src/configs/schemas/scripts/notebooks/Python/pyproject/lock/protocol/D001–D020; scientific settings/results неизменны. Results under ignored artifacts — engineering fixtures/logs/env, не research outputs. Фактический статус/traceability отражены в карточке, master/test plan и этом log. Independent human peer acceptance не заявляется.

**Результат:** P033-002 DONE только в environment/CI acceptance scope; нет pending required OS/clean-install checks. Границы: socket fixture не OS firewall и не блокирует collection-time/native/subprocess/заранее сохранённые socket aliases; reviewed default suite не имеет такого network path. Реальные OpenML/download/smoke/full/upstream и future CLI/E2E/full T14 независимого оператора остаются unverified/вне этой задачи; G1 не закрыт. NFR-007 означает проверенные hosted OS images на указанном lock, не все будущие platforms и не bitwise score equality. Никаких dependency upgrades/ML changes/protocol/settings changes, real benchmarks/dataset downloads/upstream runs. **P033-003 READY**, source review ещё не выполнялся; **P033-023 DECISION** сохранён. Внешние Q01/Q02/Q06/Q08/Q09/Q11 остаются в предыдущем ledger, независимая работа не блокируется.

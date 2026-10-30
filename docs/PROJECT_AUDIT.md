# CSCI447P033 — аудит текущего проекта

Дата проверки: **2026-10-30**. Исходный HEAD: `ad17b8b2f3e0b5256664dd74c2f2c64d9300e0bb`. До аудита рабочее дерево было чистым. Главный документ: [MASTER_PLAN.md](MASTER_PLAN.md). Исправления ниже **запланированы**, код в рамках этого аудита не менялся.

## 1. Объём и достоверность

Проверены 82 tracked files: все Python-модули и скрипты, тесты, TOML, JSON schemas, Markdown, CI, lockfile, notebook JSON и история последних семи commits. `AGENTS.md` в рабочем дереве не найден. `.venv`, `.git`, caches и данные не считаются исходными компонентами; их содержимое не перепечатывается. В `data/`, `artifacts/`, `results/` до проверки находились только `.gitkeep`. Upstream clone отсутствует: в `external/` только README. Официальных university specification, rubric, deadline и submission template не найдено.

Факт наличия файла не означает работоспособность. DONE ниже относится только к явно указанному проверенному объёму. IMPLEMENTED BUT UNVERIFIED означает, что код прочитан, но заявленный интеграционный/реальный сценарий не подтверждён. PARTIALLY IMPLEMENTED — есть полезная часть, но существенный контракт отсутствует. PLACEHOLDER — только docstring/NotImplementedError. MISSING — нет реализации/артефакта. BLOCKED — конкретная внешняя зависимость. NEEDS RESEARCH DECISION — требуется заранее записанное научное решение.

## 2. Реальные команды и результаты

Команды выполнены в корне проекта, PowerShell, без скачивания datasets и full benchmarking.

| Проверка | Команда / доказательство | Результат и границы |
|---|---|---|
| Интерпретатор | `.\.venv\Scripts\python.exe -c "import sys; print(sys.version)"` | CPython **3.14.7**, MSC 1944, AMD64; Windows 11 build 26200 |
| Пакеты | `importlib.metadata.version` | numpy 2.5.3; pandas 3.0.6; scikit-learn 1.9.1; pytest 9.1.1; Ruff 0.16.8; uv 0.12.18 |
| Первое pytest | `.\.venv\Scripts\python.exe -m pytest -q` | **31 passed, 4 setup errors**, 23.65 s: sandbox запрещает создавать numbered directories в системном Temp; это не четыре доказанных ошибки продукта |
| Повтор pytest | `.\.venv\Scripts\python.exe -m pytest -q --basetemp=artifacts/audit_pytest_tmp --tb=short` | **35 passed in 10.51 s**. Синтетические данные и mocked OpenML; реальный OpenML не проверен |
| Ruff | `.\.venv\Scripts\python.exe -m ruff check .` | All checks passed |
| Формат | `.\.venv\Scripts\python.exe -m ruff format --check .` | 53 files already formatted |
| Lock | `$env:UV_CACHE_DIR = Join-Path (Get-Location) 'artifacts/audit_uv_cache'`, затем `uv lock --check --offline` | Resolved 19 packages in 27 ms, exit 0 |
| Установка dry run | С тем же UV_CACHE_DIR: `uv sync --locked --offline --dry-run` | Checked 19 packages; Would make no changes. Это не установка из clean clone |
| CLI registry | `uv run --locked --offline p033 datasets --output artifacts/audit_registry.json` | exit 0, пять записей; network не используется |
| Default uv cache | Первая попытка `uv run --locked --offline ...` | access denied при записи interpreter cache вне workspace; перенос UV_CACHE_DIR решил проверку |
| GitHub CI | [run 36002354600](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/36002354600), прочитан через GitHub API | HEAD ad17b8b: completed/success, 2026-09-24; предыдущий 0895bba: failure. Не утверждаем, что будущие изменения уже прошли CI |
| Реальные runs | Инвентаризация `results/`, `data/`, `artifacts/` до проверки | Нет smoke/full JSON, meta CSV, fitted recommender, clinical metrics или upstream evidence |

Локальные audit caches и fixture files лежат в ignored `artifacts/`; это технические следы проверки, не scientific outputs. Команды для повторения и новые проверки: [TEST_AND_ACCEPTANCE_PLAN.md](TEST_AND_ACCEPTANCE_PLAN.md).

## 3. Компоненты и пригодность повторного использования

Все пути ниже относительно корня репозитория. Общие зависимости: pandas/numpy/scikit-learn и `datasets.py` → `features.py`; циклической зависимости в прочитанном пути нет.

| Файл / контракт | Что реализовано и что подтверждено | Статус | Тесты / зависимость / следующий шаг / reuse |
|---|---|---|---|
| `src/model_recommender/datasets.py`: `DatasetSpec`, `read_registry`, `LoadedDataset`, `load_dataset` | 5 pinned OpenML entries; проверяет source metadata id/name/version/md5, rows, columns, numeric roles, binary labels, aligned indices; excludes columns; positive→1; caches fetch | PARTIALLY IMPLEMENTED | `tests/test_datasets.py` — основной набор mocked checks. Metadata checksum сверяется, независимый local SHA256 не сохраняется. Binary only; dataclass не проверяет все типы/enum/URL/license. Reuse loader, расширить provenance/clinical adapter |
| `registry.py`, `openml_loader.py` | По одному docstring, работающая логика находится в datasets.py | PLACEHOLDER | `test_registry.py`, `test_openml_loader.py` тоже docstrings. Не переносить рабочий loader ради дерева файлов; оставить совместимость, документировать реальное владение |
| `features.py`: `characterize` | 10 признаков; валидирует empty/misaligned/missing/single-class target/infinite numeric | DONE для 10 признаков | `test_features.py` — mixed/missing/imbalance и invalid inputs. Не проверены все categorical/numeric/constant крайние случаи. Reuse, добавлять версию и формальные определения |
| `audit.py`: `audit_dataset` | Missingness, constants, feature/full hashes, duplicate groups/rows, conflicting targets; ничего не удаляет | DONE для синтетического примера | `test_audit.py::test_duplicate_and_conflict_audit`; зависит от LoadedDataset. Hash collisions теоретически возможны; duplicated count включает все строки группы, не только повторные. Не управляет split и не блокирует leakage |
| `preprocessing.py`: `FeatureRoles`, `DensePreprocessor`, checked transforms | Training-only median+indicator, constant categorical token, unknown-ignore OHE, MLP scaling; width before dense output; 512 MiB per-matrix | PARTIALLY IMPLEMENTED | Косвенно `test_runner.py`, отдельных tests нет. Нет tests unknown/all-missing/guard boundaries/scaler leakage. `DensePreprocessor.transform` напрямую обходит guard; ограничения на суммарный RSS нет. Reuse checked wrappers, тестировать до full |
| `model_families.py`: candidate factories, `build_estimator` | Baseline first, seeded sampling without replacement; 54 GBDT/27 MLP grid combinations; 20 candidates each; no early stopping | IMPLEMENTED BUT UNVERIFIED для full | Smoke использует 2 candidates; нет tests всех candidates/seed/order. TOML не читается, значения дублируются в Python. Reuse factories; добавить consistency test |
| `runner.py`: `BenchmarkProtocol`, `_tune_family`, `_refit_family`, `run_benchmark` | Paired repeated stratified holdouts, fold-local preprocessing, inner mean selection/order ties, convergence/failure logging, refit, mean BA/gap/meta-features | PARTIALLY IMPLEMENTED | Один synthetic smoke в `test_runner.py`. Full 3×20×3 не запускался. Игнорирует spec.split_strategy, нет provenance/atomic checkpoints; `research_valid` доверяет имени full. Reuse engine, закрыть admission/split contracts |
| `meta_dataset.py`: converter/builder/feature selector | One row per dataset name, aggregate gap, rejects research_valid false, numeric inputs, duplicate-name guard | PARTIALLY IMPLEMENTED | `test_meta_dataset.py`: 3 tests; duplicate guard есть, но отдельного теста нет. Нет strict protocol/schema checks, semantic duplicate/cohort check, clinical filtering, feature allowlist. Reuse converter после admission fixes |
| `recommender.py`: `TrainedRecommender`, `make_meta_estimator`, `train_recommender` | Dummy mean; scaled Ridge α1; tree depth3/leaf2; RF300/depth5/leaf2; margin >.01; rejects NaN | PARTIALLY IMPLEMENTED | `test_recommender.py` один in-sample shape test. Нет serialization, OOD/fallback, schema version, finite input check, nested meta-HPO, meta-imputer. Reuse four estimators; не считать training performance оценкой |
| `evaluation.py`: `LeaveOneGroupOut`, `recommendation_regret` | Family holdouts, training-selected best fixed, each fixed choice/oracle regrets, RMSE/accuracy | PARTIALLY IMPLEMENTED | `test_evaluation.py`: scalar regret и shape/nonnegative check; не доказан actual no-overlap. Нет MAE/CI/ablation/nested model selection/clinical exclusion. `selected` unknown молча treated GBDT. Reuse LOGO, расширить validation |
| `clinical.py`, `reporting.py` | Только docstrings | PLACEHOLDER | `test_clinical.py` docstring; реальных checks/figures нет |
| `benchmark.py::run_demo` | Offline sklearn breast_cancer split + untuned models, versions | IMPLEMENTED BUT UNVERIFIED в этом аудите | Не запускался отдельно. Это медицинский derived feature dataset, только development; не clinical transfer evidence и не frozen benchmark |
| `cli.py::main`, `_write_or_print` | datasets/fetch/audit/benchmark/characterize/demo; JSON allow_nan=False, output mkdir | PARTIALLY IMPLEMENTED | Два mocked CLI tests + реальный datasets. Нет recommend command, error-policy tests/exit semantics для excluded run. `characterize` принимает labelled CSV; не production label-free API |
| `__init__.py` | version 0.1.0 | DONE как константа | Версия должна войти в provenance; не свидетельствует о release readiness |

### Скрипты

| Файл | Реальное поведение | Статус; дальнейшая работа |
|---|---|---|
| `scripts/audit_datasets.py` | Registered nonclinical по умолчанию, JSON по dataset, общий stdout | IMPLEMENTED BUT UNVERIFIED на реальных данных; failures прерывают batch; reuse |
| `scripts/collect_openml_results.py` | Audit→benchmark; skips clinical; exceptions записывает в index; дальше продолжает | PARTIALLY IMPLEMENTED; перезаписывает output/index, нет resume/atomic save; return code не отражает failed batch; reuse orchestration |
| `scripts/build_meta_dataset.py` | `glob('*.json')` в results-dir; optional allow-smoke | PARTIALLY IMPLEMENTED; смесь smoke/full/excluded ломает обычный workflow; нужен manifest/admission report и отдельные development outputs |
| `scripts/train_recommender.py` | All-row diagnostic fit, печатает model/features/margin | PARTIALLY IMPLEMENTED; модель не сохраняет; сам корректно предупреждает об in-sample; нужен export после evaluation |
| `scripts/evaluate_recommender.py` | CSV→LOGO→predictions CSV + summary JSON | PARTIALLY IMPLEMENTED; создаёт parent predictions, но не отдельно parent кастомного summary; outputs разных models по умолчанию overwrite; нужны unique experiment paths |
| `scripts/run_reproduction.py` | Git/Python metadata + безусловный subprocess run_experiment.py | PARTIALLY IMPLEMENTED; это запуск, а не read-only audit. Нет timeout, package/hardware/config hash, upstream-version gate. Не запускать default вслепую: upstream config имеет direct_submit=true |
| `scripts/run_clinical_evaluation.py`, `scripts/make_figures.py` | main raises NotImplementedError | PLACEHOLDER; реализовать PH12/14 |
| `scripts/checkpoint1/mbgm_audit.py` | CSV shapes/missingness/duplicates/overlap, печать первых строк MBGM, regression y; notes о CV | IMPLEMENTED BUT UNVERIFIED на данных; числа о CV проверять по pinned upstream, ID в predictor count включён. Не применять к private clinical data, не смешивать regression с binary метатаблицей |
| `scripts/checkpoint1/run_upstream_audit.sh` | shell metadata + unconditional upstream execution, tee/tail | PARTIALLY IMPLEMENTED; нет pipefail/надёжного propagation failure; stdout может содержать данные. Проверить config/submit и exit policy до запуска |

### Конфигурации, схемы, документы, инфраструктура

| Пути | Состояние / доказательство / дальнейшее действие |
|---|---|
| `configs/datasets.toml` | 5 pilots, schema_version1, verified_on2026-09-20. IDs 31/59/44/1590/50, versions1/1/1/2/1; explicit feature roles/family/positive target. License='Public' — запись каталога, не оформленное доказательство разрешений. DONE структуры; live metadata/licensing UNVERIFIED |
| `configs/project.toml` | ID/contributors/reference commit; project title отличается от переданного official title. REPOSITORY DECISION; уточнить naming без выдуманной rubric |
| `configs/datasets/openml_general.toml`, `clinical.toml` | Первый указывает registry, второй provider=to_be_decided. Не исполняемые selection filters; clinical PLACEHOLDER |
| `configs/models/gbdt.toml`, `dnn.toml` | Параметры соответствуют прочитанным factories, но код их не загружает. IMPLEMENTED BUT UNVERIFIED как единый source of truth |
| `configs/experiments/general_benchmark.toml`, `recommender.toml` | Описание текущего дизайна; не исполняются runner/evaluator. Добавить consistency verification, не обещать config-driven execution |
| `configs/experiments/reproduction.toml`, `clinical_transfer.toml` | planned; zero-shot train_domain general/test clinical; NEEDS RESEARCH DECISION и реализация |
| `schemas/dataset_registry.schema.json` | Поля описаны, additionalProperties=false; runtime dataclass не полноценный JSON-schema validator; ranges/enums недостаточны |
| `schemas/model_run.schema.json`, `meta_dataset.schema.json` | Слабые provisional schemas, nested fields/ranges/finite/gap/protocol не проверяют; ни runner, ни builder не вызывают schema validation |
| `.python-version`, `pyproject.toml`, `uv.lock` | 3.14.7 и >=3.14.7,<3.15; dev deps; hatchling1.32.3; uv lock19 packages; checked. Exact resolved versions в lock, lower bounds в project — не отсутствие pinning |
| `.github/workflows/ci.yml` | Ubuntu only; checkout@v4/setup-uv@v6; locked sync, Ruff, pytest. HEAD CI green. Нет format --check, Windows job, schema/docs-link checks, explicit timeout/permissions/action SHA pin; integration network run не нужен на каждый PR |
| `.gitignore` | ignores data/artifacts/outputs/env/caches; **results/** и **external/** не ignored: raw exports/tokens/model blobs можно случайно tracked. `.env` исключён, kaggle.json отдельно не исключён. Нужна явная artifact publication policy |
| `README.md`, `ARCHITECTURE.md`, `NEXT_STEPS.md` | В основном честно описывают baseline, binary scope, no results. README full research_valid пригодность переобещает без strict validation; make meta workflow ломается при mixed folder. В NEXT_STEPS35 tests реально подтверждены. Добавить entry link, не переписывать историю |
| `docs/experiment-protocol.md` | authoritative frozen0.1; Python соответствует параметрам основной binary ветки; group/time promise пока не реализован |
| `docs/experiment_protocol.md` | Только redirect на hyphenated canonical; полезный alias, не плодить третий frozen protocol |
| `docs/decisions.md` | D001–D010; сохранять, новые решения отдельными D011+ со status proposed/accepted |
| `docs/data_dictionary.md` | Устаревшее «future runner» при уже существующем runner; актуализировать в PH14 |
| `docs/clinical_data_policy.md` | Одно общее правило; нет source cards/split/admission implementation |
| `docs/reproducibility.md`, `docs/research_log.md` | Разделяют окружения, честно отмечают отсутствие real results; нужны clean-clone и manifests |
| `docs/checkpoint1/README.md`, `external/README.md` | Instructions only; evidence не приложено |
| `notebooks/01_reproduction_check.ipynb` … `05_error_analysis.ipynb` | Каждый: одна markdown scaffold-cell, нет executed code/results. PLACEHOLDER; отчёты из saved artifacts, notebooks optional |
| `Makefile` | setup/check/test/demo/data/audit/smoke/full/meta/evaluate; Windows equivalents в NEXT_STEPS; shell make не универсален |
| `CHANGELOG_2026-09-24.md`, `SCAFFOLD_MANIFEST.txt`, `LICENSE` | Исторический snapshot/список/код MIT; не распространяют MIT на datasets. Сохранить; manifest не считать live inventory |
| `tests/fixtures/.gitkeep`, `results/**/.gitkeep` | Только directories, не готовые fixtures/результаты; MISSING research artifacts |

## 4. Приоритетные findings

| Finding | Severity / доказательство | Исправление в backlog |
|---|---|---|
| A01 Mixed smoke/full input | P0 engineering: builder glob all JSON и rejects smoke; если оба файла одного dataset допустить, duplicate row | P033-006; explicit admission report, valid-full manifest, no silent dropping |
| A02 Clinical domain not fenced | P0 scientific: builder/train/evaluate принимают clinical rows; batch skip не гарантирует isolation | P033-007; hard nonclinical-training gate и tests |
| A03 Split strategy ignored | P0 scientific: runner всегда train_test_split + StratifiedKFold; spec.split_strategy только metadata | P033-008; до клиники reject unsupported; затем versioned grouped/temporal protocol |
| A04 Inadequate run validation | P0 scientific: research_valid зависит от `protocol.name=='full'`; custom reduced protocol с именем full может пройти; JSON flag можно подделать/испортить | P033-006/011; canonical signature + actual completed splits/trials check |
| A05 Config drift | P1: TOML не исполняется; code/schema/docs расходятся без теста | P033-005; parity tests или versioned loader, без тихой смены values |
| A06 Feature blocklist | P0 для расширения: meta_feature_columns принимает любое новое numeric поле, если его нет в blocked set; performance/provenance может стать predictor | P033-007; явный versioned allowlist |
| A07 Missing provenance/recovery | P1: benchmark JSON не содержит checksum/config/git/package/hardware/split indices; результаты overwrite и пишутся только в конце dataset | P033-011/019; identity-aware atomic results/resume |
| A08 Test gaps | P0 перед full: один runner smoke не проверяет failures/leakage/preprocessor/20 candidates | P033-004/005/008; см. test plan |
| A09 Selection uncertainty | P1: LOGO без CI/MAE, только фиксированные hyperparameters; выбирать лучший из четырёх по этим же оценкам и публиковать как unbiased нельзя | P033-023/024/026 |
| A10 Inference distribution mismatch | P1: meta rows — mean трех raw outer-train descriptors, CLI characterize — full CSV; no export/recommend pipeline | P033-022/025; matching feature sampling contract; labeled input requirement |
| A11 Upstream default submits | P0 при reproduction: pinned `configs/example.yaml` direct_submit=true, device=cuda; helper запускает его | P033-013; no-submit config/adapter, remote submission отдельно от local reproduction |
| A12 Summaries path/exit status | P1: custom summary parent не создан; failed batch может exit0 | P033-011/024; CLI integration tests |

## 5. История и итог готовности

`15a330b` frozen protocol → `6e9e249` validated loading → `0895bba` benchmark/meta implementation → `ad17b8b` lint fix (все 2026-09-23/24). На HEAD есть проверенный unit-level foundation. Data-level reliability, full benchmarks, substantive meta-learning results, upstream reproduction, clinical transfer, uncertainty analysis, final figures/report/presentation пока не подтверждены или отсутствуют. Процент общей готовности был бы субъективным: по инженерной базе — существенный задел; по исследовательским результатам — подготовительный этап.

Upstream evidence получено чтением pinned [example.yaml](https://github.com/atschalz/dc_tabeval/blob/433b01652bc1f3165048c55912b99fa8c633d583/configs/example.yaml) и [run_experiment.py](https://github.com/atschalz/dc_tabeval/blob/433b01652bc1f3165048c55912b99fa8c633d583/run_experiment.py). Python3.11.7/Linux требование подтверждено [upstream README](https://github.com/atschalz/dc_tabeval#quick-start-linux). Запуск upstream в этом аудите не выполнялся.

Следующий порядок: [требования](REQUIREMENTS.md) → [методология](EXPERIMENT_PLAN.md) → [backlog](TASK_BACKLOG.md) → [приёмка](TEST_AND_ACCEPTANCE_PLAN.md). Полный перечень финальных артефактов: [FINAL_DELIVERABLES.md](FINAL_DELIVERABLES.md).

## 6. Проверка созданного planning pack

После написания выполнена локальная автоматическая проверка восьми документов: все относительные Markdown-ссылки ведут к существующим файлам; число ячеек Markdown-таблиц согласовано; FR-001…040, NFR-001…022, SR-001…008 определены ровно по одному разу и каждый ID присутствует в traceability matrix; все P033-* references разрешаются в38 task cards; в master plan16 фаз. `git diff --check` проходит. Проверка не объявляет будущие requirements выполненными и не заменяет научное peer review.

Итог изменений: восемь новых planning/audit Markdown и navigation links в README.md/NEXT_STEPS.md. Основные Python/TOML/schema/CI/lock files не изменены. Новые synthetic tests/functional fixes/full runs из backlog не выполнялись;35 existing tests были проверены до documentation-only edits, повторять ML tests после Markdown-правок не требовалось. Markdown-таблицы с математическими модулем/мощностью множества экранированы для корректного отображения.

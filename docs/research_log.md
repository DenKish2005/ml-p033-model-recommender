# Research Log

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

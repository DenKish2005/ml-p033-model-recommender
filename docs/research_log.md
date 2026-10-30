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

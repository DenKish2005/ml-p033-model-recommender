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

## P033-001 — Scope baseline, 2026-10-30

Источник baseline: пользовательское поручение P033-001, planning snapshot `8b1ef51`, [MASTER_PLAN.md](MASTER_PLAN.md), [REQUIREMENTS.md](REQUIREMENTS.md), [PROJECT_AUDIT.md](PROJECT_AUDIT.md) и локальные code/config. Отдельная university specification не предоставлена; запись OFFICIAL ниже означает сведения из пользовательского brief, сохранённые в master plan, а не независимую проверку университета или статьи. Новое чтение внешних источников и их admission относятся к будущим задачам.

| Категория | Что фиксируем | Источник / предел утверждения |
|---|---|---|
| OFFICIAL | Project ID `CSCI447P033`; переданный официальный title **A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data**; Daniyar Kshibekov и Yerassyl Auyeskhan; темы RQ1–RQ3 | Пользовательский brief по master plan/requirements; rubric, сроки, grading и обязательный объём из этого не следуют |
| REPOSITORY DECISION | Рабочее название расширения **Dataset-Aware ML Model Recommender**; binary two-pipeline research, continuous gap, dataset/family unit, clinical transfer fence | D001–D010 и [protocol 0.1](experiment-protocol.md); display name не подтверждён как официальный title |
| RESEARCH RECOMMENDATION | **Tier B принят как рабочая целевая версия**; ориентиры 20–30 general datasets и 3–5 independent clinical cohorts, 160–260 человеко-часов, с резервом 190–310 | Выбор P033-001 по поручению пользователя, таблицы Tier/compute в master/experiment plan; количества и effort остаются предположениями до P033-012/014/015/029, не university mandate и не подтверждённый ресурсный план |
| OPTIONAL | Tier C, дополнительные архитектуры/preprocessing regimes, GUI/REST service, landmarking, extensive upstream reproduction; RQ4/RQ5 как дополнительные исследования | После основного RQ1–RQ3; P033-038 и отдельно зарегистрированные experiments |
| UNKNOWN | Официальная rubric/deadlines/submission format; финальный naming; host/time/storage budget; actual admitted datasets/families; clinical endpoints/splits; upstream feasibility | [Q01–Q12](RISKS_AND_OPEN_QUESTIONS.md); отсутствие внешних ответов не блокирует независимую работу |

### Identity, RQ и фактический code scope

`configs/project.toml` содержит тот же ID и contributors, но `project.title` = **Dataset-aware model recommendation for clinical tabular data**, а `reference.title` совпадает с переданным official title. Это три разных роли названия: official title из brief, reference title в config и рабочее имя расширения. Их совпадение/переименование не выводим из содержания статьи. **Q11 остаётся needs confirmation**; config не меняется. В документах сохраняем ID и явно подписываем роли названий, не утверждая утверждённый subtitle отчёта.

| RQ: формулировка baseline (операционализация репозитория) | Что сравниваем / проверим | Текущий код и недостающие evidence |
|---|---|---|
| RQ1: предсказывают ли dataset-level descriptors преимущество одного из двух tuned pipelines на unseen datasets лучше fixed-choice baseline? | General-only family holdouts, paired raw selection regret против best fixed, выбранного только на meta-train; secondary gap error и baselines | [runner.py](../src/model_recommender/runner.py), [meta_dataset.py](../src/model_recommender/meta_dataset.py), [recommender.py](../src/model_recommender/recommender.py), [evaluation.py](../src/model_recommender/evaluation.py): runner/gap/four regressors/LOGO существуют; real full/OOF evidence и строгие fences не подтверждены |
| RQ2: какие характеристики dataset связаны с performance gap и насколько устойчивы associations? | Fold-local interpretation/ablation, без causal claims; feature schema freeze до final evaluation | [features.py](../src/model_recommender/features.py): 10 raw descriptors v1; расширение, cost/stability и ablations ещё впереди |
| RQ3: переносится ли frozen general-only recommender на independent clinical tabular domain? | Отдельный **zero-shot transfer**; clinical datasets исключены из general meta-training, preprocessing fit, feature/model/hyperparameter selection и выбора threshold | [clinical.py](../src/model_recommender/clinical.py) и clinical script — placeholders; sklearn breast-cancer demo не transfer evidence |

Сравниваются **HistGradientBoostingClassifier и MLPClassifier pipelines** с preprocessing/HPO protocol 0.1. `DNN` в существующих outputs означает этот MLP, не всю model family. Target — `performance_gap_mlp_minus_gbdt` = mean balanced accuracy MLP − mean balanced accuracy GBDT. Margin **0.01** означает MLP только при predicted gap >0.01, иначе GBDT: это **operational rule, не statistical equivalence**. Повторные outer splits агрегируются в одну dataset row, family dependence сохраняется при evaluation.

Primary meta-model/evaluation policy должна быть определена **до final results**, а source/family inclusion и feature policy — до затрагиваемых outcomes; P033-023 оформит отдельный prospective manifest, не считается выполненной через P033-001. Clinical development labels допустимы для заранее зарегистрированных descriptors и независимых evaluation labels, но не для adaptation или выбора general recommender. Любое изменение после просмотра OOF errors отмечается exploratory; confirmatory claim требует нового prospective design/untouched evaluation.

Отрицательный или неопределённый ответ RQ1–RQ3 допустим при выполнении validation/experiments и честном указании ограничений. Победа recommender не acceptance criterion. Нет rubric — продолжаем независимую работу, institutional compliance остаётся UNKNOWN до реального источника. При нехватке ресурсов сокращение breadth до Tier A записывается prospectively с rationale; запрещено скрыто уменьшать frozen candidates/folds или отбирать sources по winners. D001–D010 и frozen protocol 0.1 сохранены; принятие дизайна не означает implemented/verified.

## D011–D020 — Dispositions P033-001, 2026-10-30

Все десять исходных предложений — из [EXPERIMENT_PLAN §3](EXPERIMENT_PLAN.md#3-предлагаемые-решения-которые-нужно-freeze). Их текущий authoritative status записан здесь. **accepted design** = выбран принцип будущей реализации, не implemented, tested, verified или empirical finding. **proposed** = кандидат до проверки assumptions; **needs confirmation** = не хватает конкретных source/resource сведений; **deferred** = часть дизайна сознательно отложена. Независимый reviewer ещё не назначен; роли R/V из backlog — предложения, не подтверждение human peer review. Никакой новый experiment этим ledger не разрешён в обход gates.

| ID | Статус | Принятая часть / что ещё открыто | Tasks проверки/реализации |
|---|---|---|---|
| D011 | accepted design | Strict admission/provenance; точная schema/fingerprint ещё не реализована | P033-005/006/011/019/020 |
| D012 | accepted design | General/clinical fence и allowlist; v2 состав не утверждён | P033-007/016/021/023/031 |
| D013 | accepted design | Fixed scaled Ridge α=1 primary; остальные secondary, без post-hoc substitution | P033-021/022/023/024 |
| D014 | accepted design | Family LOGO + primary paired regret; nested tuning и lockbox allocation deferred | P033-014/015/023/024/026 |
| D015 | proposed | Matching three-75% descriptor sampler; проверить feasibility/контракт | P033-016/023/025/030 |
| D016 | proposed | v2/imputation design; exact compact schema и cost ещё проверить | P033-016/021/023/025/027 |
| D017 | needs confirmation | Separate clinical split version; endpoints/groups/folds неизвестны | P033-008/023/029/030/031 |
| D018 | proposed | Family bootstrap B=2000/seed42 и margin sensitivity; stability/few-family policy предстоит freeze | P033-023/026/028 |
| D019 | accepted design | Source/cohort grouping, no silent dedup; source-specific corrections требуют review | P033-003/008/009/014/015/019/020/029 |
| D020 | accepted design | No-submit и bounded partial reproduction; numerical attempt deferred до feasibility | P033-002/013/032/034 |

### D011 — Strict admission, identity and provenance

- **Статус/решение:** accepted design. Принимать в primary meta-table только complete canonical full 0.1 с проверкой actual candidates/folds/refits, finite scores, arithmetic и source/protocol/config/code/environment identity; flag `research_valid` или имя `full` недостаточны. Partial/smoke/rejected attempts сохранять отдельно с причинами.
- **Rationale:** закрыть A01/A04/A07 и сделать labels проверяемыми без изменения научного estimand.
- **Источник/assumptions:** EXPERIMENT_PLAN §3/6, audit A01/A04/A07, D005–D008; предполагаем доступность evidence для проверки, а не наличие готового validator.
- **Protocol/совместимость:** settings и scores 0.1 не меняются; новая admission/schema policy может исключить старый artifact. Старые outputs не перезаписывать: reuse только после восстановления проверяемой provenance, иначе rerun с lineage. Semantic protocol changes получают отдельную identity.
- **Зависимости/момент проверки/tasks:** P033-005 проверит canonical parity, P033-006 — admission, P033-011 — provenance/recovery до expensive full; P033-019/020 — финальная reconciliation/admission до primary meta-table.

### D012 — General-domain fence and feature allowlist

- **Статус/решение:** accepted design. Clinical datasets не участвуют в general meta-training, выборе features/meta-model/hyperparameters/margin, fitting meta transformations и general selection evaluation. Только versioned explicit predictor allowlist; outcomes, identity/provenance и clinical indicators — metadata, не predictors. Clinical transfer — отдельный путь.
- **Rationale:** batch skip clinical и numeric blocklist сейчас не обеспечивают защиту; закрываем A02/A06, сохраняем zero-shot interpretation.
- **Источник/assumptions:** D004/D009/D010, EXPERIMENT_PLAN §6/8, audit A02/A06; clinical/source roles должны быть честно определены до scores.
- **Protocol/совместимость:** base benchmark 0.1 неизменен. Совместимые general v1 rows reusable после D011; contaminated meta-training/OOF artifacts invalid и требуют новой general-only оценки. Состав v2 решается в D016, не этим решением.
- **Зависимости/момент проверки/tasks:** P033-007 — hard fences/allowlist, P033-016/021 — версии/fold-local preprocessing, P033-023 — manifest до final evaluation, P033-031 — проверка frozen general hash/list перед zero-shot.

### D013 — Prespecified primary meta-model

- **Статус/решение:** accepted design. Primary — scaled `Ridge(alpha=1.0)`, без primary hyperparameter search; imputation/indicators при необходимости определяются D016/P033-021 и fit только на meta-train. Dummy mean, existing shallow tree/RF и их OOF результаты secondary. Primary нельзя заменить победителем этих сравнений после final scores.
- **Rationale:** ограничить small-meta-n overfit и winner-selection bias; это методологический выбор, не доказательство превосходства Ridge.
- **Источник/assumptions:** EXPERIMENT_PLAN §3/7, audit A09, existing `make_meta_estimator` в recommender.py; small independent corpus ожидается, достаточный signal неизвестен.
- **Protocol/совместимость:** base labels/full runs reusable по D011. Роль primary регистрируется prospectively; existing in-sample fit/выбор лучшей модели по тем же OOF не становятся unbiased primary evidence. Изменение preprocessing/schema меняет meta experiment identity.
- **Зависимости/момент проверки/tasks:** P033-023 обязан перенести этот baseline в timestamped/hash manifest до P033-018 и final meta evaluation; P033-021/022/024 реализуют и проверят fold-local pipeline, baselines и outputs. Недостаточный n означает ограниченный/неопределённый вывод, не поиск favourable primary.

### D014 — Family holdouts and primary evaluation policy

- **Статус/решение:** accepted design для family LOGO и equal-dataset mean paired regret difference: `D_i = regret(Ridge)_i − regret(best fixed selected on meta-train)_i`; отрицательное среднее в пользу recommender. Best fixed выбирается по mean training BA (точный tie → GBDT). Raw regret не округляется по margin. Always GBDT/MLP, Dummy и observed-two-pipeline oracle обязательны; MAE/RMSE/winner metrics secondary.
- **Rationale:** source dependence не должна пересекать meta folds; comparison соответствует RQ1 и D008/D009. Outer seeds не independent datasets; bootstrap uncertainty — D018.
- **Источник/assumptions:** D008/D009, EXPERIMENT_PLAN §3/7, existing LOGO/best-fixed evaluator; предполагается валидная family map и достаточно training rows/families в каждом fold, что ещё не проверено.
- **Protocol/совместимость:** general full labels 0.1 reusable; изменение family map требует пересчёта meta OOF, не повторения совместимых base benchmarks. LODO допустим как эквивалент только при family=dataset. Нельзя объявить grouped engine/CI проверенными по этому выбору.
- **Deferred части:** nested grouped tuning — optional secondary sensitivity, не замена fixed primary; lockbox allocation зависит от доступных независимых families. Для frozen first design lockbox не обещан; если redesign следует за просмотром OOF, нужны untouched families для confirmatory claim, иначе revised results exploratory. Никакого clinical lockbox для выбора general model.
- **Зависимости/момент проверки/tasks:** P033-014/015 source families → P033-023 freeze folds/eligibility, tie/failure rules, secondary comparisons и lockbox feasibility до P033-018/final results → P033-024 OOF once per dataset, P033-026 uncertainty. P033-023 остаётся незавершённой, её manifest ещё отсутствует.

### D015 — Matching inference descriptor sampling

- **Статус/решение:** proposed. Для labelled development dataset усреднять raw descriptors по трём stratified 75% subsets с seeds 42/137/2026, согласованным с general meta-row extraction; не fit base models и не читать benchmark outcomes. Совпадение с текущим training contract — цель, не проверенный inference API.
- **Rationale:** full-CSV descriptors и mean outer-training descriptors имеют разные size/imbalance/distribution contracts (A10); label-free input несовместим с текущими target-dependent descriptors.
- **Источник/assumptions:** D004/D008, EXPERIMENT_PLAN §3/5/7, runner.py aggregation и audit A10; нужны development labels, feasible class counts и deterministic sampler. Clinical group/time sampling может требовать другого зарегистрированного контракта.
- **Protocol/совместимость:** не меняет full0.1/существующие meta targets. Full-data extraction — отдельная sensitivity/schema identity, не тихая замена. Re-extraction reusable только при тех же source/split identities; другой clinical sampler указывается отдельно, не выдаётся за identical general design.
- **Зависимости/момент проверки/tasks:** P033-016 проверит definitions/aggregation, P033-023 зарегистрирует контракт до final evaluation, P033-025 проверит sampler/no-base-fit и экспорт; P033-030 согласует clinical sampling до transfer. При infeasible sampling — явный отказ/заранее определённый fallback, не скрытая смена folds.

### D016 — Versioned features and missing-value handling

- **Статус/решение:** proposed. Сохранить v1 reference; compact v2 (size/types/missing/cardinality) — кандидат primary schema, full v2 — кандидат ablation. Meta imputation+missing indicators и Ridge scaling fit только на meta-train; exact feature list, undefined/all-missing/aggregation rules и caps ещё не frozen.
- **Rationale:** richer descriptors могут помочь RQ2, но слишком много correlated predictors при малом n увеличивают variance и стоимость; успех расширения не известен.
- **Источник/assumptions:** EXPERIMENT_PLAN §5/6/9, audit A06/A10; формулы/caps и cost <10% из planning requirements — proposals, не measurements и не university requirements.
- **Protocol/совместимость:** новая schema меняет recommender input/OOF/model identity, но не base0.1 labels. Их reuse/backfill допустим при unchanged raw source/base splits/protocol и проверенной provenance; definitions v1 не переписывать под старым version number. Нельзя объединить несовместимые descriptor tables без явной migration.
- **Зависимости/момент проверки/tasks:** P033-016 — fixtures/definitions/runtime/compact feasibility, P033-021 — fold-local NA policy; P033-023 freeze exact primary list до production outcomes, P033-025 compatibility, P033-027 registered ablations. Не выбирать schema по final/clinical performance; если v2 не проходит checks, v1 fallback нужно записать до outcomes.

### D017 — Clinical split protocol requires source confirmation

- **Статус/решение:** needs confirmation для конкретного protocol. D010 protection обязательна: repeated patients/groups держать вместе в inner и outer splits; при реальном temporal prediction соблюдать time order. Proposed clinical variant получает отдельную version/manifest; exact endpoints, folds/seeds и cohorts пока не утверждены.
- **Rationale:** random row split не заменяет patient/time protection; неизвестные keys или follow-up duration не доказывают independence или наличие timestamp.
- **Источник/assumptions:** D010, EXPERIMENT_PLAN §3/8, audit A03, Q08; actual source semantics/group/time keys, class coverage и memory/compute feasibility ещё неизвестны.
- **Protocol/совместимость:** general frozen0.1 не редактируется. Новый clinical split меняет estimand и fit accounting; labels/regret сообщаются отдельно от general training table. Existing unsupported grouped/time request должен отклоняться до fitting, а не падать обратно на stratified split. Ни clinical engine, ни source protection сейчас не verified.
- **Зависимости/момент проверки/tasks:** P033-008 — early gate; P033-023 — general model/evaluation baseline; P033-029 — endpoints/keys/terms; P033-030 — prospective clinical split/version/tests до fitting, P033-031 — zero-shot checks. Если source structure не позволяет корректную оценку, оставить pending/excluded с причиной, не объявлять random rows безопасными.

### D018 — Uncertainty and margin sensitivity

- **Статус/решение:** proposed. Candidate method — paired family-cluster bootstrap фиксированной OOF table, B=2000, seed42, percentile 95% CI для mean D из D014; thresholds 0/.005/.01/.02 — secondary sensitivity, primary 0.01 неизменен. Exact stability procedure/few-family reporting policy ещё должны быть зарегистрированы.
- **Rationale:** overlapping outer splits не independent n; small corpus может дать wide/unstable CI. Stability check endpoints оценивает Monte Carlo error, не является правилом остановки при favourable sign/significance.
- **Источник/assumptions:** EXPERIMENT_PLAN §3/7/9, R21, D008/D009; family map и эффективный n пока неизвестны. B=2000 не подтверждает adequate precision/power.
- **Protocol/совместимость:** base scores и fixed OOF predictions не меняются; новая analysis identity при смене resampling/weights. Брать family blocks целиком, сохранять paired losses и equal-dataset estimand. Такой CI conditional on fixed CV predictions, не full retraining uncertainty, не новый-dataset prediction interval и не equivalence test.
- **Зависимости/момент проверки/tasks:** P033-023 prospectively задаёт method, stability rule и multiplicity/secondary policy; P033-026 проверит cluster/seed/arithmetic/stability до final inference, P033-028 выполнит sensitivity. При слишком малом n — per-dataset descriptive/ограниченный вывод с явной причиной; не выдумывать nominal clinical coverage.

### D019 — Source/cohort/duplicate policy

- **Статус/решение:** accepted design для grouping/no silent deletion: related versions/shared cohorts — одна family, exact source duplicates не дают независимые meta rows; identifiable repeated entities не пересекают base inner/outer splits. Conflicting signatures, symmetry classes и predictor-time issues требуют source-specific admission review, не автоматической очистки.
- **Rationale:** независимость определяется источником, не именем файла; сохраняем data-centric evidence и не подбираем corpus по scores.
- **Источник/assumptions:** D004/D008/D009, EXPERIMENT_PLAN §3/4/6, Q04; lineage/group keys иногда отсутствуют. Unknown dependence документируется, не объявляется устранённой.
- **Protocol/совместимость:** family mapping может потребовать пересчёта meta evaluation. Изменение base grouping/dedup/eligible rows меняет splits/targets — отдельный protocol suffix, новые compatible runs; old0.1 сохраняется как historical/diagnostic evidence, не смешивается в одной primary table с исправленной версией. Непригодные старые outputs не считать валидными из-за сохранения истории.
- **Зависимости/момент проверки/tasks:** P033-003/008/009 review до pilot fitting; P033-014/015 prospective expansion map; P033-019/020 reconciliation/one-row admission, P033-029 clinical lineage. Source-specific решения и exclusions фиксируются до затрагиваемых outcomes; actual source audits этим ledger не выполнены.

### D020 — Bounded no-submit upstream reproduction

- **Статус/решение:** accepted design для no-submit и отдельного bounded attempt: сначала source/config/environment audit, затем максимум один выбранный dataset × одна default/minimalistic model configuration как initial numerical target. Numerical attempt **deferred** до P033-013 feasibility; это planning scope, не обещание доступности или совпадения метрик.
- **Rationale:** сохранить различие partial reproduction/reference paper и нового P033 benchmark; default helper не запускать без проверки outbound behaviour.
- **Источник/assumptions:** EXPERIMENT_PLAN §3/11, audit A11/R27 и сохранённые pinned-source notes; доступность данных, Linux/Python environment, no-submit metric path и compute cap ещё UNKNOWN. В P033-001 upstream не запускался и внешние сведения повторно не проверялись.
- **Protocol/совместимость:** reproduction имеет отдельные environment/config/run identity и metric space; upstream scores не импортируются как binary0.1 BA gaps или general meta rows. D001–D010/full0.1 неизменны; full numerical study optional и требует отдельного scope/budget.
- **Зависимости/момент проверки/tasks:** P033-002 сохраняет project environment; P033-013 проверяет pinned source, permitted data, no-submit adapter/config, local metric и resource cap **до** subprocess. При невозможности — source/env evidence или bounded failure, явно не numeric reproduction; P033-032/034 пакуют evidence/limits. Никаких remote submissions или сообщений третьим лицам этим решением не разрешено.

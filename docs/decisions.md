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

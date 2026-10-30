# CSCI447P033 — план исследований и экспериментов

[Главный план](MASTER_PLAN.md) · [Аудит](PROJECT_AUDIT.md) · [Требования](REQUIREMENTS.md) · [Backlog](TASK_BACKLOG.md) · [Приёмка](TEST_AND_ACCEPTANCE_PLAN.md)

Это **план**, датированный 2026-10-30, без новых experimental results. Действующий protocol0.1 остаётся в [experiment-protocol.md](experiment-protocol.md). Ниже предложения помечены **PROPOSED**: их нужно принять в `docs/decisions.md` до затрагиваемых production runs; этот документ сам по себе не меняет Python/TOML.

## 1. Научная цель и связь с reference paper

RQ1: предсказывают ли dataset-level meta-features преимущество одного из двух tuned pipelines на unseen datasets лучше fixed-choice baseline? RQ2: какие характеристики связаны с этим преимуществом? RQ3: переносится ли general-only recommender на independent clinical tabular domain? Единица анализа — dataset, при зависимости sources — dataset family/cohort.

[Статья v3](https://arxiv.org/html/2407.02112v3) рассматривает десять Kaggle tasks и три режима подготовки: standardized, expert feature engineering, test-time adaptation; сопоставляет HPO и разные модели. Ключевое методологическое следствие для P033: предсказывается качество **pipeline в конкретном режиме подготовки**, а не универсальное свойство названия модели. Наша binary OpenML задача с BA и одним preprocessing regime — новое исследование, а не прямое повторение их leaderboard evaluation. Статья обсуждает изменения rankings при изменении подготовки; из этого не следует, что наш recommender будет успешен.

Перед финальным report PH1 создаёт `docs/related_work.md`: для каждой relevant работы вопрос, выбор datasets, split unit, preprocessing/HPO, baselines, limitations и применимость. Взять минимум первичные reference paper, публикацию о tabular model comparison и методологию algorithm selection/meta-learning; число статей не официальный rubric. Не пересказывать leaderboard percentile как balanced accuracy.

**Дополнительные PROPOSED RQ:** RQ4 — сокращает ли feature extraction+recommendation затраты относительно полного paired search при приемлемом measured regret? RQ5 — насколько устойчивы рекомендации к feature-group ablation и practical margin? В Tier A RQ4 descriptive, RQ5 optional. Не обещать causal effects, clinical utility, universal GBDT-vs-DNN dominance, formal equivalence, discovery of best architecture или publication-level power при 20–30 datasets.

## 2. Frozen protocol0.1: что сохраняем

| Элемент | Действующее решение | Соответствие коду / ограничение |
|---|---|---|
| Scope | binary classification; HistGradientBoostingClassifier vs MLPClassifier | DatasetSpec и runner binary-only; DNN label означает именно MLP |
| Outer evaluation | 3 repeated stratified 75/25 holdouts, seeds42/137/2026 | BenchmarkProtocol.full/run_benchmark; это не 3-fold outer CV и не три независимых datasets |
| Inner HPO | StratifiedKFold3, shuffle=True, outer seed; 20 deterministic configurations/model, tuning seed42 | _tune_family/factories; same indices обеим моделям |
| Preprocessing | Median+indicators, categorical constant+unknown-ignore OHE, numeric scaling MLP, empty features preserved, dense float64 | Checked wrappers; только текущий training fold; individual matrix≤512MiB |
| GBDT | max_iter200, early_stopping=False; LR .03/.1, leaves15/31/63, L2 0/1/10, min leaf10/20/40 | baseline .1/31/0/20; 19 sampled из остальных53 |
| MLP | max_iter500, Adam/ReLU, early_stopping=False; sizes(32,16)/(64,32)/(128,64), α .0001/.001/.01, LR .0003/.001/.003 | baseline(32,16)/.0001/.001; 19 sampled из остальных26 |
| Winner HPO | mean inner BA; exact tie→earlier candidate | Outer scores не участвуют в tuning |
| Research eligibility | all candidates/folds и refits success для обоих pipelines на всех outer seeds | Код частично реализует, но нужно canonical contract validator, не доверие flag/name |
| Meta target | mean BA MLP−mean BA GBDT | gap >0: observed MLP winner; exact0→GBDT for naming; near tie abs(gap)≤.01 отдельно |
| Recommendation | predicted gap >.01→MLP, иначе GBDT | .01 operational margin; не equivalence test |
| Meta features | raw outer training partitions; average3 → one row/dataset | Training size около75% raw n; inference должен совпадать с этим sampling contract |
| Meta evaluation | complete dataset-family holdouts | LOGO implemented; richer tests/CI ещё нужны |

**Metrics:** BA=(TPR+TNR)/2 даёт равный вес двум классам и не скрывает minority failure за majority accuracy; не равна clinical decision utility. AUC=P(score_positive>score_negative)+.5P(equal), требует обеих classes и корректной positive_class; secondary ranking diagnostic без threshold tuning. Search seconds включают preprocessing и inner fitting; refit seconds в текущем коде измеряют estimator.fit после preprocessing, поэтому отдельный end-to-end timing нужен для cost claims. Сохранять hardware/threads, n_iter, convergence warnings. Время нельзя честно сравнивать между несопоставимыми машинами без пояснений.

Equal trial count — бюджет **конфигураций**, не GPU-seconds, complexity или achieved convergence. Primary не обрезать MLP из-за его медленной работы. При превышении resource budget остановить scheduling новых datasets; альтернативный time-budget experiment — другой protocol/version, отдельная таблица и отдельные targets.

**Failures:** exception/nonfinite/невозможный split/guard violation → explicit excluded paired result, retain partial diagnostics, never replace candidate. ConvergenceWarning при finite output остаётся usable и отмечается; частота предупреждений — результат. Помимо ConvergenceWarning запланировать structured capture остальных warnings с category/location, без patient data. Случайный repair row deletion, auto-reduced folds или sample truncation запрещены. All-or-nothing rule может preferentially исключать большие/high-cardinality datasets: publish all-attempted cohort и сравнить descriptors admitted/excluded, не делать missing pipelines равными нулю.

## 3. Предлагаемые решения, которые нужно freeze

| ID | PROPOSED решение | Влияние / момент принятия |
|---|---|---|
| D011 | Строгий canonical protocol fingerprint + schema admission + provenance | Не меняет scores, но старые runs без evidence требуют verification/re-run; PH3 до full |
| D012 | General/clinical fence, versioned meta-feature allowlist | Устраняет leakage; не добавляет clinical train; PH3 |
| D013 | На general meta-level primary заранее fixed Ridgeα1; Dummy/tree/RF secondary; никаких post-hoc main-model substitutions | Минимум winner-selection bias; PH0/9 до final evaluation. Nested selection optional Tier B sensitivity |
| D014 | Family LOGO primary; если нужен model selection — inner grouped CV и external lockbox families | LODO совпадает с LOGO только если family=dataset; число lockbox families выбрать по доступным n, не обещать заранее power |
| D015 | Inference extraction: усреднять descriptors по тем же трём75% stratified development subsets, без outer test outcome/performance | Согласует существующие meta rows. Нужен labelled development sample; full-data extraction — отдельная sensitivity, не silent replacement |
| D016 | Feature schema v2 и meta missing imputation+indicator, train-only | Feature expansion меняет recommender input; labels/performance reusable только при неизменных base splits/protocol и наличии source/split identity |
| D017 | Grouped/temporal clinical split version отдельный от stratified general | Сохраняет medically required leakage protection, меняет estimand; report general/clinical protocols рядом, не объединять без объяснения |
| D018 | Group-cluster bootstrap B=2000, seed42; threshold sensitivity0/.005/.01/.02 | B proposed, остановиться после stability check endpoints. Exploratory sensitivity не выбор нового primary threshold |
| D019 | Source/cohort/duplicate policy: variants same family; при identifiable repeated entity groups always together | Если применить grouped correction к general pilot — новый protocol suffix и обе версии report; не rewrite frozen0.1 |
| D020 | No-submit upstream reproduction, сначала default/minimalistic; scope1 dataset/1 model | Предотвращает автоматическую отправку Kaggle; не полное повторение статьи |

Если решение не принято, downstream task не должен подменять его default удобной библиотеки. Для конфликтующих решений версионировать конфиг и новый run namespace; не смешивать incompatible protocols в primary meta table.

## 4. Dataset admission и расширение

Primary0.1 — только публичные законно доступные binary nonclinical tables с outcome и доступными на prediction time features. Regression/multiclass не превращать произвольно в binary ради n; отдельная task/protocol extension. Предпочитать разнообразие domains, n/p, categorical fraction, missingness, cardinality, imbalance; не отбирать datasets после просмотра winner. Полная сетка quota — descriptive coverage table, не обещание равного количества winners.

Для каждого кандидата: (1) source/access/license citation, (2) source ID/version/checksum, (3) target semantics/positive label, (4) roles/excluded IDs, (5) cohort/family/versions, (6) target availability/prediction time, (7) duplicates/conflicts, (8) group/time keys, (9) minimum class counts **в каждой реально получившейся partition**, (10) encoded memory estimate, (11) expected compute band, (12) accept/reject/reason **до outcomes**. Не считать source MD5 достаточной security checksum: он version marker; local SHA256 — integrity fingerprint.

Существующие pilots: credit-g31/v1/n1000; ionosphere59/v1/n351; spambase44/v1/n4601; adult1590/v2/n48842; tic-tac-toe50/v1/n958 — факты локального registry, live download не проверен. У каждого отдельная family; Adult merged original splits и unknown household dependence, Spambase personal markers, tic-tac-toe symmetries ограничивают claims. Нельзя считать variants независимыми datasets.

### Nonclinical shortlist

Это кандидаты, **не новые admitted registry entries**. L=предположительно low fit cost, M=medium, H=high; часы до pilot measurement неизвестны. Размер со знаком ≈ — planning estimate, а не проверенный размер конкретного OpenML download. «Public» ниже — literal catalogue licence, не самостоятельное юридическое разрешение; original-source terms ещё проверить. Если metadata недоступна, ID не угадывать.

| Кандидат / источник | ID / type / приблизительный n×p / target | Почему включить; leakage и доступ; cost |
|---|---|---|
| [banknote-authentication](https://www.openml.org/api/v1/json/data/1462), [UCI](https://archive.ics.uci.edu/dataset/267/banknote+authentication) | **1462/v1 подтверждён metadata**, binary,1372×4, Class (OpenML) | Small numeric, low p; derived image statistics — табличные predictors. Public metadata; UCI source review; duplicates; L |
| [qsar-biodeg](https://www.openml.org/api/v1/json/data/1494) | **1494/v1 verified metadata**, binary,1055×41, Class | Chemical descriptors/imbalance; related molecular compounds possible dependence; Public metadata; L/M |
| [kc1](https://www.openml.org/api/v1/json/data/1067) | **1067/v1 verified metadata**, binary,≈2109×21, defects | Software defects; NASA source versions/duplicates, group with derivatives; source description contains kc2 URL mismatch, inspect actual data; Public; L |
| [climate-model-simulation-crashes](https://www.openml.org/api/v1/json/data/1467) | **1467/v1 verified metadata**, binary,540 simulations,18 model parameters plus IDs, Class | Imbalance/physics; exclude study/run IDs from predictors, review study grouping; Public metadata; L |
| [madelon](https://www.openml.org/api/v1/json/data/1485) | **1485/v1 verified metadata**, binary,≈2600×500, Class | High p/redundancy/artificial; mark synthetic provenance, report results without it as sensitivity; train+validation merged; Public; M/H |
| [PhishingWebsites](https://www.openml.org/api/v1/json/data/4534) | **4534/v1 verified metadata**, binary,≈11055×30, Result | Discrete website properties; repeated domains/URLs, post-outcome heuristic features need review; Public; M |
| [Mushroom UCI](https://archive.ics.uci.edu/dataset/73/mushroom) → OpenML discovery | OpenML mapping **TO VERIFY**, binary8124×22, edible/poisonous | All categorical/missing; species/template dependence; source public, exact terms snapshot required; M |
| [Bank Marketing UCI](https://archive.ics.uci.edu/dataset/222/bank+marketing) → OpenML discovery | OpenML1461 **не подтверждён в этом аудите (API timeout)**; binary45211×16 reported on UCI, y | Larger mixed, imbalance; repeated contacts, time dependence, duration unavailable before call; variant/schema differences need source card; H |
| [MAGIC Gamma UCI](https://archive.ics.uci.edu/dataset/159/magic+gamma+telescope) → OpenML discovery | OpenML mapping TO VERIFY; binary19020×10, gamma/hadron | Physics numeric; simulation structure, no arbitrary class recoding; source/access terms review; M/H |
| Credit Approval → OpenML discovery | ID/version/n/p/target **TO VERIFY**; binary candidacy needs metadata | Mixed categories/missing; source/cohort and legacy credit variants review; estimated L/M only after shape check |
| Phoneme → OpenML discovery | Все source pin/size/target/terms **TO VERIFY** | Numeric low-dimensional speech features, speaker grouping review; cost unknown |
| Hill-valley → OpenML discovery | Все pin/size/target/terms **TO VERIFY** | High correlated numeric features; noisy/no-noise versions same family; cost unknown |
| Australian credit approval → OpenML discovery | Все pin/size/target/terms **TO VERIFY** | Mixed numeric codes; возможная производная Credit Approval, **не добавлять как independent n**; cost unknown |
| Amazon employee access → OpenML discovery | Все pin/size/target/terms **TO VERIFY** | High cardinality/imbalance, repeated resource/employee groups, dense512MiB risk; H candidate |
| Electricity → OpenML discovery | Все pin/size/target/terms **TO VERIFY** | Temporal stress case, **не primary0.1**, пока нельзя честно обеспечить appropriate splitting; H candidate |

Последние шесть строк — очередь discovery, а не подтверждение данных. После dedup/temporal exclusion shortlist может дать меньше20 independent datasets: продолжить systematic OpenML discovery с frozen rules и admission ledger; не набивать n версиями credit/NASA. В Tier A можно завершить exploratory study на≈15 admitted independent datasets; Tier B target20–30, Tier C30–60 — планы репозитория/предложения, не OFFICIAL. Мощность зависит от числа **families**, дисперсии gaps и дисбаланса winners; никакое число само по себе не гарантирует meaningful learning.

### Clinical shortlist: отдельный holdout pool

У всех ниже UCI source pages проверены 2026-10-30, CC BY4.0 указана на источнике; сохранить attribution/terms snapshot при admission. Raw data не скачивались, локальные checksums/actual missingness ещё неизвестны.

| Dataset / official source | Task, size, target | Scope / риски / split / cost |
|---|---|---|
| [Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease) | Cleveland reported303×13; num0 vs1–4 binary definition | Public clinical mixed; missingness, hospitals/related processed versions same family. Endpoint diagnosis, не future treatment benefit; no synthetic merging Kaggle copies. L |
| [Chronic Kidney Disease](https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease) | 400×24; class ckd/notckd | Public clinical mixed/missing; disease-defining labs могут давать diagnostic circularity, prediction-time review. Correct whitespace/missing tokens per source rule без inspecting test labels. L |
| [Heart Failure Clinical Records](https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records) | 299×12 original; DEATH_EVENT | Exclude follow-up `time` для baseline-time prediction; follow-up-dependent endpoint не fixed-horizon risk. Small single cohort; temporal horizon/censoring limitation, не survival claim. L |
| [Diabetes130-US](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008) | 101766 records,47 features по UCI; readmitted <30 vs others **PROPOSED** | Repeated patient_nbr must group, encounter IDs excluded; discharge-time availability; missing codes; death/hospice/endpoints review; exact target/eligible rows freeze. High-cardinality dense guard; H, Tier B if budget permits |
| [WDBC metadata](https://www.openml.org/api/v1/json/data/1510) | OpenML1510/v1; breast diagnosis from morphology features | Не primary clinical shortlist: derived imaging statistics и sklearn demo уже использует этот source. Оставить development-only или явно secondary with exposure disclosure; не выдавать за untouched clinical validation |

Для первых трёх отсутствие patient/time keys не доказывает независимость пациентов: source documentation review, known duplicate check, limitation. Для Diabetes130-US без actual patient groups не запускать random row split. Запрашивать MIMIC/restricted data не требуется. Полезные clinical descriptors (missingness, imbalance, cardinality, visits/patient where available) либо general features, либо audit-only; новые domain-specific predictive features нельзя добавить после clinical outcomes без отдельного adaptation experiment.

## 5. Meta-feature specification

Обозначения: X имеет n>0 rows,p>0 predictors после удаления IDs/target; N numeric и C categorical columns из роли/типа; m_ij=1 если missing; q_k=n_k/n для observed target classes. Counts не imputing. Undefined numeric summaries→NA + defined-count/indicator; meta-imputer fitted **только meta-training**. Empty X/missing y/one class/infinite numeric reject. На inference предполагается labelled development dataset: imbalance/entropy без labels вычислить нельзя. Label-free recommender — другое future schema, не нынешний контракт.

### Уже реализовано (`features.py::characterize`, schema v1)

| Feature | Точная формула / edge | Test |
|---|---|---|
| n_samples, n_features | n,p текущей raw training partition | 4×2 fixture→4,2 |
| n_classes | число observed nonmissing y classes | binary→2; runner rejects multiclass |
| samples_per_feature | n/p | p0 reject |
| categorical_fraction | 1−\|N\|/p по select_dtypes(number); bool currently nonnumeric | all-numeric0, all-cat1; numeric category codes role decision отдельно |
| missing_fraction | sum(m)/(np) | 1 missing in4×2→.125 |
| rows_with_missing_fraction | sum_i I(sum_j m_ij>0)/n | 1 affected row of4→.25 |
| constant_feature_fraction | sum_j I(nunique_j(dropna=False)≤1)/p | all-missing constant; {value,NA} **не** constant в v1 |
| minority_class_fraction | min_k q_k | 3:1→.25 |
| imbalance_ratio | max_k n_k/min_k n_k | 3:1→3; no zero observed count |

Нельзя тихо изменить определения categorical/constant и продолжить schema v1; сохранять v1 как ablation reference.

### PROPOSED schema v2 (`characterize`/новые helpers в том же features.py)

| Группа / признаки | Формулы и edge cases | Реализация/стоимость / tests |
|---|---|---|
| Size: log_n, log_p | ln(1+n),ln(1+p), natural log | O(1); n1 known log2 |
| Types: numeric_count,categorical_count,binary_count | \|N\|,\|C\|; binary=число columns с ровно2 observed nonmissing levels, независимо от numeric/cat | O(np) nunique; all-missing не binary; roles partition fixture |
| Missing: affected_columns_fraction,max_column_missing | mean_j I(sum_i m_ij>0), max_j sum_i m_ij/n | O(np), all-missing column max1; no missing→0 |
| Target entropy | −sum q_k ln(q_k); optional normalized /ln(K) приK>1 | Binary balanced→ln2; forbidden outer test y; K1 reject |
| Cardinality: mean,max,high_fraction | c_j=nunique(nonmissing), j∈C; mean/max c_j; mean I(c_j>20) | Threshold20 proposed config. C empty→NA+has_categorical0; allmissing cat c0; no outcome use |
| Numeric skew | For column finite observed r≥3 and variance>0: g1=m3/(m2^(3/2)), m_t=mean((x−mean x)^t); aggregate median abs(g1),p90 abs(g1) | No library bias convention ambiguity; r<3/constant→NA. Symmetric{-1,0,1}→0 |
| Numeric kurtosis | g2=m4/(m2²)−3, r≥4,var>0; median/p90 | Population excess convention; no eligible columns→NA+count0; hand fixture checked |
| Variance/nearconstant | Population variance m2 (ddof0); summaries median log1p(m2), nearconstant fraction where m2/(mean(x²)+1e-12)<1e-8 | Units affect variance; threshold proposed, sensitivity and per-column normalization documented; zero constant→nearconstant |
| Duplicates | d=(n−number_unique_predictor_rows)/n; **отличается** от audit count all-members/n | NA patterns treated equal for signature; verify hashes on duplicate groups; fixture [a,a,b]→1/3 |
| Correlation/redundancy | abs Pearson r for eligible numeric pairs with≥3 pairwise observed,var>0; mean, max, fraction выше .95 | n_rows cap5000, eligible columns cap200, seed42 proposed for deterministic O(n p²) bound; exact selected indices/hash saved. <2 cols→NA |
| Sparsity/density | numeric zero_fraction=#observed numeric zeros/#observed numeric cells; density=1−zero_fraction | N empty/all missing→NA; missing≠zero; не OHE density и не категориальная sparsity |

Helpers: `summarize_numeric`, `summarize_categorical`, `summarize_correlations`, `feature_schema` **PROPOSED**, вход raw X/roles/seed/caps, выход only named float fields + extraction metadata (metadata не predictors). Correlation subsampling не зависит от y/scores. Reuse actual split IDs; не извлекать meta-features из standardized/OHE table вместо raw. Runtime/memory benchmark на pilots до freeze. Добавлять десятки коррелированных predictors при≈20 rows опасно: primary compact schema (v1+log size+types+missing/cardinality), v2 full — ablation. Landmarking (small tree/logistic CV score) optional: только development training data, inner-CV, independent timing, risk cost/leakage; не baseline Tier A/B.

## 6. Meta-dataset contract

`results/meta_dataset.csv`: одна row на canonical dataset identity и совместимый protocol. Source columns: dataset,source ID/version,family,clinical; versioned allowlisted numeric features; mean BA обоих pipelines; gap; actual_best_pipeline; near_tie flag. `results/manifests/meta_dataset.json` хранит input SHA256/run IDs, schema/protocol/feature versions, inclusion/exclusion reasons, extraction partition IDs. Provenance columns не подаются в estimator. Reject duplicate names **и** same cohort derivatives как независимые rows; related tasks могут присутствовать только с family grouping и explicit estimand.

Aggregation: BA_G=mean_s BA_Gs, BA_M=mean_s BA_Ms, Δ=mean_s(BA_Ms−BA_Gs); descriptor_j=mean_s f_j(X_train_s,y_train_s). Для undefined v2 descriptor записать aggregation rule заранее: mean finite partitions и count_defined; если0→NA. Нельзя больше взвешивать adult из-за n: equal dataset weights primary. Не брать лучший outer seed, не делать шесть model rows или три independent meta examples. Сохранять split-level values отдельно для uncertainty diagnostics.

Admission steps: parse JSON strict finite→validate schema+canonical actual completion→source/protocol identity→general-domain gate→duplicate/group checks→allowlist/outcome arithmetic→CSV+manifest+reject ledger atomic. Smoke/development outputs живут отдельно; rejects не «теряются», но не вызывают незаметного train-on-smoke. `--allow-smoke` только в clearly named development path, никогда results/meta_dataset.csv primary.

## 7. Recommender design и оценивание

Primary fixed Ridge (scaled numeric meta-features, α1) сохраняет small-sample regularization. Dummy mean predicts train mean Δ, а не выбирает заранее GBDT; shallow tree и RF как уже реализовано — secondary comparisons. Always GBDT, always MLP и best-fixed-from-meta-train обязательны; oracle=best of **observed two pipelines**, не истинный оптимум всех алгоритмов. Regression retains gap magnitude; classification winner model optional sensitivity, near-ties noisy, class imbalance often severe.

Наблюдаемое качество системы:

- Predicted gap MAE=mean|hatΔ−Δ|, RMSE=sqrt(mean(hatΔ−Δ)²).
- Recommendation uses .01 threshold, observed winner uses0; recommendation accuracy и balanced winner accuracy secondary. Если observed winner only one class, balanced recommendation accuracy=NA с объяснением.
- Dataset regret R_i=max(BA_Gi,BA_Mi)−BA_selected,i≥0; near-ties **не округлять** в0. Primary comparison D_i=R_recommender,i−R_bestfixed(meta-train),i; negative mean D favours recommender.
- Win/loss/tie of measured gap exact sign отдельно от practical near-tie flag absΔ≤.01. Не превращать .01 в p-value/equivalence zone.

LOGO primary trains transformations/model на remaining families; тестируется вся held-out family. LODO secondary только если derived versions/cohorts не разделяются. GroupKFold5 возможно при достаточно independent families: заранее frozen group assignment/seed, balanced group allocation без inspecting winner outcomes. При выборе hyperparameters, feature subsets или лучшего из4 meta-models — inner grouped selection внутри meta-train; outer folds remain untouched. При слишком малом n primary fixed Ridge предпочтительнее huge search. Nested grouped HPO search **PROPOSED** α{.1,1,10}, tree depth{2,3}, RF depth{3,5}; минимум3 eligible training families; если недостаточно — predefined default, no row split. Выбранные параметры и fallbacks сохранять.

Если после LOGO увидеть errors и изменить features, исходная LOGO becomes exploratory. Final claim требует frozen redesign и untouched lockbox families либо честного описания exploratory nature. Нельзя выбрать лучший model/threshold по clinical scores. Fit final deployable artifact на всех admitted **general-only** rows после selection freeze, не использовать его in-sample fit для reported performance.

**Inference uncertainty (PROPOSED):** small predicted gap и выход descriptors за train ranges помечать как low-support diagnostic; это не calibrated probability выбора. Базовый продукт возвращает point prediction, observed training support/OOD reason и operational recommendation, не выдуманный confidence percentage. При nonfinite/неподдерживаемой схеме — отказ; при заранее определённом OOD policy — best-fixed-from-general-training fallback с причиной. Interval для отдельного gap optional: residual/conformal calibration только на held-out general families, отдельно проверить coverage/width; при малом числе independent families не обещать nominal95% validity на clinical shift. Bootstrap CI среднего regret из следующего абзаца не является prediction interval нового dataset.

**Uncertainty:** three outer splits перекрываются; sample SD descriptive, не CI из n=3 independent tasks. Для mean paired regret difference bootstrap families B2000/seed42, брать целые family blocks. Сначала получить one OOF prediction per dataset; bootstrap этого фиксированного OOF table оценивает variability across observed families conditional on fitted CV procedure, не полную uncertainty повторного training/search. Stronger optional: повторять entire grouped evaluation in each resample, дороже и не primary. Report both dataset count и family count; при3 clinical cohorts CI очень нестабилен, важнее per-dataset intervals/values и qualitative limitations. CI excludes0 при заранее primary comparison — limited evidence на sampled task population; не универсальная победа. Secondary multiple comparisons exploratory или family-wise correction (Holm) заранее. No post-hoc p-value fishing.

## 8. Clinical zero-shot protocol

1. До открытия clinical performance заморозить nonclinical source list, features, meta-model, margin, fallback policy, artifact SHA256. Source admission metadata review допустим, outcome-based tuning — нет.
2. Установить prediction time/outcome; IDs, post-outcome/follow-up variables исключить. Для repeated patient groups обе base-level inner и outer splits grouped; для реального time order — forward splits и при необходимости embargo. Время follow-up не timestamp разбиения.
3. Неподдерживаемые grouped/time strategies сейчас отклонять. После реализации D017 выбирать feasible clinical splits и class coverage; число refits/inner fits считать по фактическому новому protocol. Нельзя использовать default stratification на repeated visits ради frozen general protocol.
4. Descriptors берутся только из clinical development partitions, y там разрешён для entropy/imbalance. General-trained imputer/scaler/model не refit. Model hash до/после одинаков.
5. Сначала сохранить predictions/fallback reasons; независимо получить paired base-model benchmarks для evaluation labels. Inference не читает их outcomes. Для clinical recommendation training data scale contract повторяет registered clinical development sampling, difference from general explicitly reported.
6. Report per-cohort BA_G/BA_M/gap/prediction/regret/fixed comparisons, unknownness/feature-range distances, missingness/imbalance shifts. Сопоставить distributions с nonclinical holdouts без выдачи cohorts за independent patients across sites.
7. Optional few-shot/adaptation uses отдельные clinical training cohorts и untouched clinical test cohorts; назвать adaptation, не zero-shot. Не строить medical treatment recommendations, не заявлять deployment/clinical benefit из этого benchmark.

## 9. Interpretability, ablation, robustness

PH11: scaled Ridge coefficients with fold variability; tree/RF permutation importance на held-out families, aggregated with uncertainty. При small test groups single fold permutation unstable; use grouped OOF analysis/explicit limitations. No causal feature effect interpretation. Feature group ablations: v1; compactv2; fullv2; без target distribution; без categorical; без numeric moments/correlation. Все transform/selection внутри same meta-folds, сравнить paired regret/MAE, n/p ratio и stability. Threshold0/.005/.01/.02 predetermined sensitivity, .01 primary unchanged. Leave-one-domain/family sensitivity, without synthetic Madelon, excluding known dependent sources по predeclared rule. Если GBDT dominates, report winner count and majority baseline; не искусственно oversample successful MLP tasks для main benchmark.

Для связи с data-centric paper optional отдельный preprocessing experiment: два заранее заданных leakage-safe regimes на subset datasets, одинаковые splits/candidates; outcome becomes dataset×regime but group all regimes of one source together. Не смешивать rows regimes в one-row-per-dataset primary schema. Это новая версия исследования с дополнительными fits, не обязательная «починка» baseline.

## 10. Compute accounting и practical budget

Полный0.1: 3×2×20×3=**360 inner estimator fits** +3×2=**6 refits** =366/dataset. Smoke:1×2×2×2=8 inner+2 refits=10. Preprocessing fits full:3×2×(3 inner+1 refit)=24; они не входят в estimator fit count. Actual successful count может меньше при failure; ledger хранит attempted/succeeded/failed отдельно.

| Datasets | Full inner fits | Full refits | Всего | Smoke estimator fits отдельно |
|---:|---:|---:|---:|---:|
| 5 | 1800 | 30 | 1830 | 50 |
| 20 | 7200 | 120 | 7320 | 200 |
| 30 | 10800 | 180 | 10980 | 300 |
| 60 | 21600 | 360 | 21960 | 600 |

Для грубой чувствительности, **не измеренные затраты**: при среднем estimator fit1/10/60 s итого5 datasets≈.51/5.08/30.5 h;20≈2.03/20.33/122 h;30≈3.05/30.5/183 h;60≈6.1/61/366 h. Реальные MLP fits на adult/high-p могут быть гораздо дольше; add measured I/O/preprocessing, не переносить small synthetic timings. Формула T=sum_dataset,sum_fit t_fit + t_preprocess+I/O. CPU-seconds/core-hours отдельно от wall time; outer parallelism и BLAS threads не double count. GPU для sklearn baseline не нужен; наличие GPU не ускоряет MLPClassifier автоматически.

Практика без изменения0.1: сначала cheap smoke; measure один representative full после P0 fixes; batch по predicted n×encoded_p; cap simultaneous jobs1 на неизвестном host; record threads; cache immutable downloads/checked transformed folds без train-test mixing; run IDs/atomic per-outer checkpoint; resume только matching source/protocol/config/code identity; не перезапускать successful runs из-за косметического report edit. Parallel tasks ≤RAM/peakRSS и CPU budget, без thread oversubscription. Missing GPU — blocker optional neural upstream models, не general pipeline. Ресурсы upstream не складывать с0.1 без отдельного ledger.

## 11. Upstream partial reproduction

[Upstream README](https://github.com/atschalz/dc_tabeval) требует отдельные Linux/Python3.11.7 и Kaggle access; конфиги задают dataset/preprocessing/HPO. Репозиторию P033 не нужен токен в Git. Проверенный pinned commit `433b01652bc1f3165048c55912b99fa8c633d583`: [example.yaml](https://github.com/atschalz/dc_tabeval/blob/433b01652bc1f3165048c55912b99fa8c633d583/configs/example.yaml) включает **direct_submit=true**, device=cuda и default CatBoost/MBGM. Наш reproduction helper сейчас вызывает upstream скрипт без защиты. Поэтому read-only inspection→локальный no-submit adapter/config→setup→согласованный bounded run. Никакой default automatic Kaggle submission в будущем local smoke workflow.

PH2 minimum: source commit+requirements inventory, MBGM data audit если законно доступны files, one local default CatBoost/minimalistic attempt, capture exact error/exit если stack/GPU/access недоступны. Target outputs: environment/config/source fingerprints, stdout/stderr, metrics if produced, table expected paper setting vs actual scope. Для научного сравнения reproducible subset можно расширить на expert FE того же source, но private leaderboard/old submission infrastructure может быть недоступна. «Запустился» не значит «совпали результаты статьи»; missing expected metric/validation procedure → partial reproduction. Полное повторение10 tasks×models×regimes дорого и optional; failure с диагностикой приемлем как reproducibility finding, но не заменяет новое P033 исследование.

## 12. Что считается валидным результатом

Совместимый validated full artifact + complete candidate/fold/refit evidence + pinned data/code/environment + zero split/meta leakage findings + prospective selection policy + all baselines/exclusions. Smoke, sklearn demo, in-sample fit, synthetic fixtures и флаг research_valid сами по себе — engineering evidence. Для RQ1 может получиться «на выбранных datasets не превзошли best fixed»; для RQ2 — «устойчивых associations не обнаружено»; для RQ3 — «перенос нестабилен на данных cohorts». Это полноценные результаты при соблюдении протокола. Выводы и графики появятся **после** экспериментов, сейчас чисел качества нет.

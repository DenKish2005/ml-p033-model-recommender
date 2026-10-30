# CSCI447P033 — риски, решения и неизвестные требования

[Главный план](MASTER_PLAN.md) · [Аудит](PROJECT_AUDIT.md) · [Требования](REQUIREMENTS.md) · [Методология](EXPERIMENT_PLAN.md) · [Backlog](TASK_BACKLOG.md)

Дата2026-10-30. Likelihood/impact qualitative L/M/H — экспертная оценка, не измеренная вероятность. Владелец E/R/V — предлагаемые роли из backlog. Пока нет официальной rubric, compute inventory и реальных benchmark scores, часть рисков может только уточняться. P0 findings из аудита входят в admission gates, не маскируются общим positive status.

## 1. Risk register

| ID / владелец | Риск / likelihood / impact | Early warning | Mitigation / task | Fallback и допустимый вывод |
|---|---|---|---|---|
| R01 R | Мало independent datasets / H / H | <15 accepted sources либо много related variants | Prospective expansion+family audit, P014/015; publish n datasets и n families | Tier A exploratory, wide uncertainty; не обещать доказать generality |
| R02 R | Слабое разнообразие / M / H | Corpus почти весь small numeric UCI, no missingness/cats | Metadata coverage matrix до outcomes; целенаправленно искать domains/types по frozen rules | Ограничить population claim, не добавлять datasets по observed winners |
| R03 R | Слабый performance signal / H / H | Большинство abs(gap)≤.01, noisy signs | Continuous regression+raw regret, repeated paired splits, uncertainty P026 | Near-ties and no reliable selection advantage — valid negative result |
| R04 R | GBDT выигрывает почти везде / H / H | Winner distribution highly imbalanced | Always-GBDT/best-fixed baselines, balanced accuracy for recommendation only if defined | Сообщить strong fixed baseline; не балансировать corpus по wins задним числом |
| R05 R | Recommender хуже fixed choice / M / H | OOF regret difference≥0/CI includes0 | Predeclare primary model/metric, all baselines P023/024 | Завершить исследование с доказательным отрицательным/неопределённым ответом |
| R06 E+R | Meta-model overfit small n/high p / H / H | train error≈0, unstable OOF/coefs, RF optimistic | Fixed regularized Ridge, compact schema, grouped CV, no huge tuning P016/021/023 | Dummy/best-fixed as practical recommendation, complexity claims ограничить |
| R07 E+V | Preprocessing/target leakage / M / H | validation categories/statistics in fitted train; post-outcome features | Spy tests+source prediction-time review T03/T09, P004/008/029 | Invalidate affected run lineage; rerun compatible corrected protocol, no use old scores |
| R08 R+V | Dataset-family/cohort leakage / M / H | Same data variants in meta-train/test, inflated n | SHA/cohort mapping/family LOGO P007/014/020 | Merge/exclude duplicate sources prospectively, recalculate effective n |
| R09 E | Invalid gap/row target/schema / M / H | Flag full but fewer folds/trials, score difference mismatch | Canonical validator/schema/finite/arithmetic P006/020 | Reject corrupted runs with ledger, regenerate rather than fill values |
| R10 R | Biased exclusion/all-or-nothing / H / H | Excluded mostly large/high-cardinality tasks | All-attempted ledger, descriptors admitted vs excluded P019 | Scope claim to feasible corpus; alternate resource protocol separately preregistered |
| R11 E | HPO слишком дорого / H / H | MLP adult fit minutes, total projected exceeds budget | Measure representative full, schedule batches, immutable caching/resume P011/012 | Stop scheduling, smaller predeclared Tier A corpus; no hidden trial reduction |
| R12 E | Нет GPU / M / M | Upstream CUDA-only configuration/modern NN adapters fail | sklearn baseline CPU, upstream compatibility audit P013 | Partial upstream evidence; optional Tier C GPU models defer, general research продолжается |
| R13 E | Memory/OHE explosion / M / H | encoded width predicts>512MiB or high process RSS | Preallocation guard, separate peakRSS cap, concurrency1 initially P004/012 | Logged paired exclusion; alternative native-cat/sparse protocol new version only |
| R14 E | Dependencies/old-new environments conflict / M / H | Installing upstream breaks project, absent wheels | Separate Linux3.11.7 upstream; locked3.14.7 project, no cross-install P002/013 | Record blocker; no opportunistic package mixing or unreported upgrade |
| R15 E+R | OpenML timeout/drift/cache corruption / M / M | Metadata hash/version differs, retry failures | Pin/check source, cache SHA, bounded retry logging P003/009 | Candidate pending/excluded; source mirror only verified exact identity and terms |
| R16 R | Kaggle access/competition rules / H / M | Token/rules/submission leaderboard unavailable | Legal source acquisition independently, no tokens in Git; inspect upstream config P013 | Source/environment audit and failed partial reproduction honestly labelled |
| R17 R+V | Clinical licensing/privacy restrictions / M / H | No clear terms, patient identifiers in raw/log | Public UCI source cards; only aggregate export; no restricted datasets requirement P029/032 | Choose another prospectively approved public cohort, preserve exclusion reason |
| R18 R | Patient/group leakage / M / H | Repeated patient across train/test; unknown group key | Clinical grouped inner+outer, explicit unknown limitations P030 | Reject repeated-visit source without keys or narrow cohort; no assertion leak-free |
| R19 R | Temporal/domain shift / H / H | Clinical descriptors outside general range; follow-up column strongly predictive | Prediction-time review, forward split where valid, OOD diagnostics P029/030/031 | Fixed-general fallback/explicit refusal; RQ3 limited/negative; no adaptation called zero-shot |
| R20 R | Incomparable metrics/protocols / M / H | Kaggle percentile mixed BA, grouped clinical compared as same random holdout | Separate experiment identities/strata; BA primary within registered binary task P023/030 | Report side-by-side with caveats; don't pool inconsistent meta targets |
| R21 R+V | Неверные statistical claims / H / H | n=3 outer seeds treated independent, threshold=.01 called equivalence | Family bootstrap, dataset unit, prespecified main comparison P026/034 | Descriptive results/CI; no causal/universal/equivalence claim |
| R22 E | CI gaps/flakiness/Windows differences / M / M | Ubuntu green but Windows temp/paths fail; smoke absent | OS matrix/offline synthetic suite/format check P002 | Record environment-specific limitation; keep reproducibility path on verified OS |
| R23 E+R | Upstream невозможно воспроизвести / H / M | Old stack/GPU/API/private scores unavailable | Bounded partial reproduction/no-submit/config evidence P013 | Explain failed components, no fake numeric match; new P033 evidence remains separate |
| R24 E | Silent result overwrite/lost long-run work / M / H | Same dataset/model summary overwritten; partial output accepted | Unique identity/atomic checkpoint/resume P011/024 | Recover validated attempts; no mixing attempts/configs |
| R25 E | Inference feature distribution mismatch / H / M | Full CSV n vs training descriptor0.75n; undefined metas | Matching sampling/extraction contract, labelled input, OOD/fallback P025 | Explicit unsupported input refusal; full-data variant separate sensitivity |
| R26 R+V | Scope creep displaces research / H / H | Web UI/API/many model packages before real full/OOF | Tiered scope and gates, P038 after core | Drop GUI/deep portfolios/landmarking first, never drop baselines/clinical fence |
| R27 E+R | Accidental outbound submission / M / H | upstream direct_submit=true, helper unconditional run | No-submit adapter/config verification P013; no token read/log needed | Stop numerical upstream attempt, retain read-only audit; remote submission only separately authorized |

## 2. Open questions и владельцы решения

| Q | Тип / что неизвестно | Почему существенно | Как закрыть / task / interim assumption |
|---|---|---|---|
| Q01 | UNKNOWN/OFFICIAL: university spec/rubric, milestones/deadline, required format/report length/presentation duration | Нельзя certify institutional submission без критериев | Получить реальный документ от преподавателя/студентов, attach source path/date; P001/037. Пока research package Tier B PROPOSED, даты не выдуманы |
| Q02 | UNKNOWN: CPU cores/RAM/GPU/доступный wall/energy/storage budget | Determines corpus/parallelism/optional models | P012 host inventory+one full timing; no need менять код ради assumed GPU; initial concurrency1 |
| Q03 | NEEDS RESEARCH DECISION: Tier A/B/C и доступные active hours | Нет оснований обещать full publication scope | P001 принять Tier B target20–30 либо честно Tier A≈15; source counts не OFFICIAL |
| Q04 | NEEDS RESEARCH DECISION: duplicates/conflicting signatures/symmetries policy | Random split may share equivalent observations | Source review P003/008; preserve0.1 or version corrected grouped sensitivity; no silent row deletion |
| Q05 | NEEDS RESEARCH DECISION: meta-model tuning vs fixed primary | Selection bias при small meta n | D013/D014/P023; рекомендован fixed Ridgeα1 primary, all others secondary |
| Q06 | UNKNOWN: exact general dataset count after license/dedup/memory admission | Shortlist содержит unverified candidates | P014/015 produce actual admitted count/family coverage; не обещать20 rows до checks |
| Q07 | NEEDS RESEARCH DECISION: compactv2 vs v1 main descriptors | Feature explosion и input compatibility | D015/D016/P016; freeze features before final evaluation; preserve v1 reference |
| Q08 | UNKNOWN: clinical endpoint timing/group keys/feasible folds | Clinical source may require different protocol | P029/030; small public diagnosis cohorts first, large repeated-visit source only if keys usable |
| Q09 | UNKNOWN: upstream legal data access, GPU support, permitted no-submit local metric path | Default helper unsafe and local metric flow may assume submission | P013 source inspection; allow documented partial failure; no requirement to send predictions |
| Q10 | NEEDS RESEARCH DECISION: summary/model artifact publication | results/ currently tracked by default, model storage ignored | P032 allowlist aggregate summaries, provide checksum/acquisition for restricted artifacts; raw clinical never required |
| Q11 | UNKNOWN: official title vs configs/project.toml title | Переданный title — статья, config — extension | P001 keep official title with extension subtitle in report, update config only after explicit recorded naming choice |
| Q12 | OPTIONAL: strongest family-level conclusion/preprocessing study | Current two-pipeline design insufficient | Tier C/P038 separate protocol/compute; not blocking base RQ on concrete pipelines |

Вопросы не требуют останавливать подготовку плана. Никаких писем преподавателю или внешним людям этим заданием не разрешено; этот документ — готовый список для самостоятельного уточнения студентами.

## 3. Отрицательный результат: заранее допустимый сценарий

Если best fixed выигрывает: проверить leakage/data/schema/metric correctness, затем показать all OOF losses, uncertainty, winner imbalance, gap magnitude, sample/family counts, exclusions и feature stability. Разделить «нет доказательства улучшения» и «доказана эквивалентность» — второе не следует из wide CI. Допустимые explanations — гипотезы (малый n, низкий signal, homogeneous corpus, domain shift), проверяемые ablations; нельзя выдавать их за causal proof. Main recommender может остаться исследовательским artifact, а practical fallback — best fixed из general training. Не менять оценивание, чтобы гарантировать успех.

Проект завершён научно, если корректные эксперименты отвечают на вопросы в границах данных, даже при неуспехе meta-learning. Проект не завершён, если отрицательный вывод заменяет отсутствующие experiments, validation или clinical evaluation без documented external blocker и scope decision.

## 4. Как обновлять register

На M0/M2/M3/M5 обновлять likelihood/evidence/owner/status; unresolvedP0 блокирует соответствующий gate. Access blocker upstream не блокирует независимую general ветку. При сокращении scope фиксировать rationale **до просмотра затрагиваемых outcomes**, сохранять rejected/attempted sources и не удалять историю decisions. Final report threat-to-validity section должен ссылаться на реально проявившиеся risks, а не только generic checklist.

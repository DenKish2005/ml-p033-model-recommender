# CSCI447P033 — конечные результаты, report, presentation и demo

[Главный план](MASTER_PLAN.md) · [Аудит](PROJECT_AUDIT.md) · [Методология](EXPERIMENT_PLAN.md) · [Требования](REQUIREMENTS.md) · [Backlog](TASK_BACKLOG.md) · [Приёмка](TEST_AND_ACCEPTANCE_PLAN.md)

Это **спецификация будущей сдачи** на2026-10-30. Реальных experimental metrics, trained artifacts, figures или научных выводов ещё нет. Названия ниже — целевые; файлы не создаются пустыми заранее. Если university template/format отличается, сначала подтвердить rubric и recorded output naming decision. Главная reproducible source-of-truth — machine-readable artifacts+manifests, а не вручную переписанная таблица в слайдах.

## 1. Deliverables ledger: exact paths и критерии

E=существует код/документ, но финальная версия может требовать работы; NEW=будущий artifact/file. Для ignored или restricted content путь — локальный, а не требование GitHub upload. Коммитить только source и проверенные разрешённые aggregate outputs согласно artifact allowlist.

| ID / category | Exact filename/path / current state | Responsible phase/tasks | Acceptance criteria / evidence |
|---|---|---|---|
| D01 Software | `src/model_recommender/datasets.py`, `configs/datasets.toml` E | PH3/5,P003/009/014/015 | Pinned validated loader, actual accepted corpus; T01/T08; local cache не обязательно tracked |
| D02 Software | `src/model_recommender/audit.py`, `scripts/audit_datasets.py` E | PH3/4,P008/009 | Duplicates/conflicts/missingness/constants correct, no silent deletion; T02 |
| D03 Software | `src/model_recommender/features.py` E | PH6,P016 | v1/compact/full definitions/schema, raw training-only extraction, tests/timings; T02/T10 |
| D04 Software | `src/model_recommender/preprocessing.py`, `model_families.py`, `runner.py` E | PH3/7,P004/005/008/011/017/018 | Paired full protocol, all fits/failures logged, preallocation guard; T03–T05 |
| D05 Software | `src/model_recommender/meta_dataset.py`, `scripts/build_meta_dataset.py`, `schemas/model_run.schema.json`, `schemas/meta_dataset.schema.json` E | PH3/8,P006/007/020 | Strict actual completion+identity admission, no mixed smoke/clinical/outcome predictors; T05/T06 |
| D06 Software | `src/model_recommender/recommender.py`, `scripts/train_recommender.py`, `src/model_recommender/cli.py` E | PH9/14,P021/022/025 | General-only training, trusted export and unseen labelled inference/fallback; T07/T11 |
| D07 Software | `src/model_recommender/evaluation.py`, `scripts/evaluate_recommender.py` E | PH10/13,P023/024/026/027 | Held-out families, baselines/MAE/RMSE/accuracy/raw regret/CIs and paired comparisons; T07/T10 |
| D08 Software | `src/model_recommender/clinical.py`, `scripts/run_clinical_evaluation.py` placeholders→implemented | PH12,P029/030/031 | Source/split adapters, no patient/time leakage found in verified scope, frozen zero-shot; T12 |
| D09 Software | `src/model_recommender/reporting.py`, `scripts/make_figures.py` placeholders→implemented | PH14,P033 | Saved-artifact tables/figures only; no fit/network side effects; T13 |
| D10 Data | `results/summaries/dataset_inventory.csv` NEW | PH5,P014/015 | Actual name/source/version/checksum/family/domain/n/p/types/license/admission reason; accepted+rejected, no fabricated IDs |
| D11 Data | `results/summaries/dataset_audits/<dataset>.json` NEW | PH4/5,P009/015 | Every admitted source audit, checksums linked, review decisions; no raw records |
| D12 Data | `results/development/smoke/<dataset>.smoke.json`, `results/development/smoke_index.json` NEW | PH4,P010 | Engineering-only, all research_valid=false, separate from primary analysis |
| D13 Data | `results/raw_model_runs/<dataset>.full.json` NEW | PH7,P012/017/018 | Real canonical full only eligible, complete trials/seeds/refits and provenance; excluded diagnostics also retained |
| D14 Data | `results/manifests/environment.json`, `results/manifests/general_benchmark.json`, `results/manifests/splits/<run_id>.json` NEW | PH3/7,P011 | git/versions/OS/hardware/threads/source/config/candidates/split IDs; nonprivate hashes or local-only indices when required |
| D15 Data | `results/summaries/resource_budget.csv`, `results/summaries/exclusions.csv` NEW | PH7/13,P012/019 | Predicted vs observed time/RSS/fits with units, exclusions/attempt lineage and bias discussion |
| D16 Data | `results/meta_dataset.csv`, `results/manifests/meta_dataset.json` NEW | PH8,P020 | One row/dataset, general-only primary, compatible versions, meanBA/gap/features exact, raw input hashes |
| D17 Data | `results/summaries/recommender/<model>/predictions.csv`, `summary.json`; model∈dummy_mean/ridge/decision_tree/random_forest NEW | PH10,P024 | Each eligible dataset once OOF, actual/predicted gap/recommendation/losses/all fixed baselines/oracle, no file overwrites |
| D18 Data | `results/manifests/meta_evaluation.json` NEW | EarlyPH10,P023 | Frozen model/threshold/features/families/folds/primary metric and selection policy before final results |
| D19 Data | `results/summaries/uncertainty.json`, `ablations.csv`, `feature_importance.csv`, `error_analysis.csv` NEW | PH11/13,P026/027/028 | Paired family CI metadata, stability and negative findings, margins primary vs sensitivity explicitly separated |
| D20 Clinical data | `results/manifests/clinical_transfer.json`, `results/summaries/clinical_transfer/predictions.csv`, `benchmark_comparison.csv`, `summary.json` NEW | PH12,P031 | General model hash unchanged, no clinical tuning, actual source/endpoint/split differences, per-cohort gaps/regrets and uncertainty limits |
| D21 Models | `artifacts/recommender/baseline.pkl`, `baseline_manifest.json`, `model.pkl`, `manifest.json` NEW, ignored/local by default | PH9,P025 | Baseline Dummy and primary Ridge (или separately preselected model), training source list all-general, schema/margin/lock hashes, trusted roundtrip T11; share binary only if needed/permitted |
| D22 Models/inference | `results/summaries/inference_demo.json` NEW | PH14/15,P025/036 | Previously unseen labelled development dataset→features→gap/choice/fallback, no outcomes read/base benchmarking, compatible extraction sampling |
| D23 Reproduction | `results/checkpoint1/upstream_reproduction.json`, `upstream_stdout.log`, `upstream_stderr.log`, `environment.json`, `config.yaml` NEW | PH2,P013 | Actual pinned commit/interpreter/config/exit+errors, no-submit path; classification reproduced/partial/blocked; sanitized no tokens/raw rows |
| D24 Figures | `results/figures/benchmark_comparison.svg`, `.png` NEW | PH14,P033 | Paired BA per-dataset HistGBDT/MLP, labels/n/families/scope; CIs only where justified |
| D25 Figures | `results/figures/performance_gap_distribution.svg`, `.png` NEW | PH14,P033 | Signed gap distribution,0 and practical±.01 annotated, counts/exclusions known, no equivalence claim |
| D26 Figures | `results/figures/meta_feature_advantage.svg`, `.png` NEW | PH14,P033 | Selected prespecified features vs gap, exploratory associations, not causal; all data points/units |
| D27 Figures | `results/figures/recommender_baselines.svg`, `.png` NEW | PH14,P033 | Primary raw mean regret and fixed baselines, family-level uncertainty/paired difference; oracle labelled retrospective |
| D28 Figures | `results/figures/regret_by_dataset.svg`, `.png` NEW | PH14,P033 | Per-dataset selected loss and best-fixed comparison; near-ties never silently zeroed |
| D29 Figures | `results/figures/error_analysis.svg`, `.png` NEW | PH14,P033 | Actual vs predicted gap and worst failures/feature ablation, positive/negative results both visible |
| D30 Figures | `results/figures/clinical_transfer.svg`, `.png` NEW | PH14,P033 | Zero-shot per-cohort regret/gap compared general heldouts; small-cohort limitations and protocol differences |
| D31 Figure provenance | `results/figures/manifest.json` NEW | PH14,P033 | input artifact hashes, generation command/versions, output hashes, no fabricated fixture numbers used in final plots |
| D32 Docs | `README.md`, `ARCHITECTURE.md`, `NEXT_STEPS.md`, `docs/reproducibility.md`, `docs/data_dictionary.md`, `docs/clinical_data_policy.md` E | PH14,P032 | Facts/commands match actual code, independent clean clone path, terms/citations/source acquisition, privacy and domain limits |
| D33 Docs | `docs/experiment-protocol.md`, `docs/decisions.md` E | PH0–13,P001/023/030 | Frozen0.1 preserved; accepted clinical/meta changes versioned, deviations explained; no duplicated contradictory canon |
| D34 Docs | `docs/related_work.md`, `docs/upstream_reproduction.md`, `docs/references.bib` NEW | PH1/2/15,P013/034 | Primary-source method matrix/citations, actual vs reference settings, bounded reproduction claims |
| D35 Research report | `docs/final_report.md`, `docs/final_report.pdf` NEW (PDF after required format known) | PH15,P034 |21 sections below, every empirical claim→artifact, RQ answers/negative findings/uncertainty/limitations, exported layout reviewed |
| D36 Presentation | `presentation/outline.md`, `presentation/CSCI447P033_slides.pptx`, `presentation/CSCI447P033_slides.pdf` NEW | PH15,P035 |12 slides proposed, readable sourced plots, claims/n/units match report, presentation duration confirmed or marked proposed |
| D37 Demo | `docs/demo_script.md` NEW | PH15,P036 | Offline repeatable sequence with exact implemented CLI, prepared lawful fixtures, clear engineering/research distinction |
| D38 Submission | `docs/submission_checklist.md`, `results/manifests/final_submission.json` NEW | PH15,P037 | Paths/hashes/requirements evidence, no unresolvedP0, rubric compliance checked only if actual rubric supplied |

В D04 compact filenames `model_families.py`, `runner.py` означают тот же `src/model_recommender/`. D17 summary.json живёт **внутри каждого model dir**. D19 все четыре filenames находятся в `results/summaries/`. Exact path при реализации менять только recorded decision и обновлением всех references, не случайно по CLI default overwrite.

## 2. Что должно быть научно получено

RQ1: actual held-out-family comparisons: selected pipeline BA/regret vs alwaysGBDT/alwaysMLP/best-fixed-from-training/Dummy+oracle reference. RQ2: fitted relationship stability, ablation/error evidence, uncertainty and noncausal scope. RQ3: frozen general-only artifact applied to independent clinical development descriptors, compared to observed paired clinical benchmark gaps без refit/recalibration. RQ answers содержат confidence/limitations и могут быть negative/inconclusive.

До выполнения experiments допустимы только design claims («реализовано», «проверено тестом»), не performance claims. Успех на synthetic fixtures не является доказательством generalization. Значение .01 — practical choice margin, не статистическая эквивалентность; oracle over observed candidate portfolio не universal optimum. Никаких фиктивных table cells вместо missing run: NA+reason и status excluded/blocked.

## 3. Academic report:21 раздел

Нумерация совпадает с RTM в REQUIREMENTS. Объём страниц и стиль библиографии UNKNOWN. Source Markdown удобен для review; university Word/LaTeX/PDF template применять после получения. Финальный file authoring/rendering — будущая отдельная задача, сейчас только план.

| № / раздел | Что писать и откуда брать данные | Что должно быть завершено / figures-tables | Допустимые claims / необходимое evidence |
|---|---|---|---|
| 1 Abstract | Problem, corpus/family counts, two pipelines, primary eval, actual main result, clinical finding, limitation | PH10/12/13/15; D17/D20/D19 | Только реальные числа primary metrics/CI; никакого «outperforms» без paired evidence |
| 2 Introduction | Tabular algorithm selection и стоимость exhaustive search; clinical transfer motivation | PH1; related_work/citations | Motivation vs demonstrated result разделены; не медицинская decision-support система |
| 3 Problem Statement | Input labelled development table, output gap/model choice, operational margin, pipeline scope | PH0/9; architecture/input schema | Exactly supported binary setting, no claim label-free recommendation |
| 4 Research Questions | RQ1–3, optional RQ4/5, hypotheses/estimands | PH0 freeze/meta eval manifest | Questions preregistered; exploratory questions помечены |
| 5 Related Work | Tabular comparisons, data-centric preprocessing, algorithm selection/meta-learning; matrix assumptions | PH1/2; docs/related_work.md/references.bib | Primary source citations, distinguish evidence vs proposed contribution |
| 6 Original Paper and Research Gap | Paper regimes/task metrics; our extension; actual upstream partial reproduction | PH1/2; D23/D34, comparison table settings/success/failure | No claim full reproduction from one default local run; Kaggle percentile≠BA |
| 7 Methodology | Separate base/meta/final-domain boundaries; split diagrams/seeds/schema/version | PH3/8/10; D14/D18, protocol table | Leakage controls supported by tests/source reviews; no absolute guarantee |
| 8 Dataset Collection | Prospective selection, versions/terms/families/roles/clinical flags, n/p/types/imbalance/missingness, exclusions | PH5/12; D10/D11/D15; inventory+coverage+exclusion tables | Actual admitted and attempted counts; source variants not independent tasks |
| 9 Meta-Feature Extraction | Exact v1/v2 formulas, raw partitions, undefined stats/sampling/time, label requirement | PH6; D03/data dictionary, feature schema/table/runtime | Descriptors known without benchmarking outcomes; no outer-test outcome use |
| 10 Model Benchmarking Protocol | HistGBDT/MLP preprocessing/grids/candidates, inner tuning/paired outer, failures/times | PH7; D13/D14/D15; search-space table, D24/D25 | Claims about these concrete pipelines; equal20 trials≠equal compute; finite convergence retained |
| 11 Meta-Learning Recommender | Gap aggregation, compact model/regularization, fixed/inner-only selection, training/export/inference | PH8/9/10; D16/D18/D21/D22 | No in-sample performance claim; frozen schema/model/domain provenance |
| 12 Experimental Results | Per-dataset base scores/gaps, primary OOF loss/gap prediction and uncertainty | PH10/13; D17/D19; D24/D25/D28/D29 | Unbiased only to declared held-out procedure/scope; altered designs labelled exploratory |
| 13 Baseline Comparison | AlwaysGBDT/MLP, Dummy, best-fixed-from-training, tree/RF secondary, oracle upper reference | PH10/13; D17/D19, D27 | Best-fixed chosen training only, oracle retrospective, all baselines shown even superior |
| 14 Clinical Transfer Results | Source/endpoints/prediction time/group/time splits, zero-shot gaps/losses, shift/OOD/fallback | PH12; D20/D30 + clinical source cards | Model unchanged, no clinical selection; small cohort generality/temporal limits explicit |
| 15 Interpretation and Discussion | Stable associations, feature importance/ablation, worst regret cases, why fixed baseline strong | PH11/13; D19/D26/D29 | Hypotheses vs demonstrated associations; no causal feature statement |
| 16 Limitations | Small meta n/families, restricted models/preprocessing, compute/scope/negative signal/domain shift | PH13; risks manifested and exclusion evidence | Honest no-gain/inconclusive findings; no definitive equivalence from wide CI |
| 17 Threats to Validity | Internal/leakage/selection/exclusion bias; construct validity BA/clinical endpoint; external dataset dependence | PH3/5/10/12/13; T09/D15/family manifest | Each threat linked mitigation and residual limitation, not generic checklist |
| 18 Conclusion | Answer RQ1/RQ2/RQ3 with measured metrics/limits; practical recommendation if supported | PH13/15; conclusions ledger | Negative answer scientifically complete; no stronger scope than experiments |
| 19 Future Work | Broader models/regimes, new cohorts, label-free descriptors, cost-sensitive selection/adaptation | PH15; Tier C/P038 explicitly unperformed | Future proposals only, no implied implemented capability |
| 20 References | Original datasets/licenses/papers/frameworks exact versions/DOIs/URLs/access dates | PH1/5/15; D34 | Every borrowed claim/figure credited; no fabricated citation |
| 21 Appendix / Reproducibility | Clean clone commands, lock/git/env/candidates/folds/full tables/test report/failed runs/RTM/demo | PH14/15; D14/D18/D23/D32/D38 | Independent operator instructions; no tokens/raw clinical data; actual scope reproduced vs blocked |

Для каждой empirical figure/table рядом указывать experiment ID, sample unit, n datasets/families, version/method, metric units и uncertainty method. Claim ledger можно вести в appendix report таблицей claim→artifact→protocol→limitation; отдельный файл не обязателен. Final abstract/conclusion писать последними, после reconciliation всех чисел.

## 4. Presentation:12 proposed slides

12 slides вписываются в requested10–15; точное время UNKNOWN, initial rehearsal≈10–12 min **PROPOSED**, подстроить под преподавателя. Презентация рассказывает о результате, а не перечисляет все38 задач.

| Slide | Содержание / visual / evidence | Speaker goal |
|---|---|---|
| 1 | Title/ID/students, dataset-aware selection subtitle, concrete two-pipeline scope | Что исследовали |
| 2 | Problem: dataset characteristics→pipeline performance; cost of benchmarking; clinical tabular motivation | Зачем нужен research question |
| 3 | Reference paper vs our contribution; preprocessing/HPO distinction; partial reproduction status | Где extension и где reproduction |
| 4 | RQ1–3 и заранее frozen primary criterion (regret vs best fixed) | Что считается evidence, победа не гарантирована |
| 5 | Data sources/admission/families/clinical holdout; coverage table actual n/p/missingness | На чём исследовали и почему independent n ограничен |
| 6 | Base pipeline diagram: paired outer train/test, inner HPO, fold-local preprocessing | Как предотвращали optimistic tuning |
| 7 | Meta-features/one-row-per-dataset gap target; compact model and .01 margin | Как работает recommender без base-model benchmarking при inference |
| 8 | Held-out-family evaluation + fixed/Dummy/oracle baselines | Почему comparison честный |
| 9 | Actual main OOF regret/CI plot D27 and gap distribution D25 | Главный результат включая negative/inconclusive |
| 10 | Feature ablation/error cases D26/D29 | Что удалось/не удалось объяснить, no causal claim |
| 11 | Clinical zero-shot D30, unchanged model, patient/time/endpoint limitations | Насколько переносится и чего нельзя заключать |
| 12 | Answers RQ1–3, limitations, reproducibility link/commit and next research | Что было достигнуто и как проверить |

Appendix slides optional:search spaces/resource costs/exclusions/upstream failure log, без замены основной истории. Не показывать идентифицирующие clinical rows/screenshots. Версии таблиц/слайдов/отчёта должны совпадать.

## 5. Technical demo:3–5 min proposed

До demo подготовить lawful cached public dataset или synthetic engineering fixture, frozen model artifacts, validated OOF summaries/figures. Synthetic demo помечать как engineering; не показывать его invented score как research result. Не обучать тысячи models live.

1. **Registry/audit (≈30–45s):** existing `uv run --locked p033 datasets`, затем saved audit/source card. Объяснить pinned source/family/target и duplicates, не print raw clinical rows.
2. **Characterize (≈30–45s):** existing `uv run --locked p033 characterize <local-labelled.csv> --target <target>` для raw sanity; пояснить, что future recommend использует matching75% sampling contract и schema, а не blindly full CSV features.
3. **Recommend (≈45–60s):** после P025 future command `uv run --locked p033 recommend <local-labelled.csv> --target <target> --model-dir artifacts/recommender --output results/summaries/inference_demo.json` — **PROPOSED syntax**, зафиксировать реальную implemented help в demo_script.md. Показать gap/model/.01/unknownness/fallback reason; no benchmark outcomes read.
4. **Evaluate (≈45–60s):** открыть saved general OOF plot/table и one per-dataset regret calculation. Объяснить best-fixed training-only и oracle retrospective, не in-sample fit.
5. **Clinical/reproducibility (≈45–60s):** saved zero-shot aggregate result/model hash/limits; exact clone/lock/test/regenerate instructions. Если real smoke показывается, явно development-only, research_valid=false.

Offline contingency: network не нужен при подготовленном cache/artifacts; если model artifact не прошёл проверку, demo не называет случайный выбор рекомендацией. Live demo возможен только после implementedCLI/tested artifact; сейчас этого command ещё нет.

## 6. Clean-clone release workflow, который нужно реализовать и проверить

Сохранить existing setup convention. Базовые commands (CMD/PowerShell/bash без make):

```text
git clone https://github.com/DenKish2005/ml-p033-model-recommender.git
cd ml-p033-model-recommender
uv python install 3.14.7
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q --basetemp=artifacts/pytest_tmp
uv run --locked p033 datasets
uv run --locked p033 fetch credit-g
uv run --locked p033 audit credit-g --output results/summaries/dataset_audits/credit-g.json
uv run --locked p033 benchmark credit-g --mode smoke --output results/development/credit-g.smoke.json
```

Это achievable current commands; source acquisition network нужен для public fetch. При sandbox uv cache permissions использовать workspace UV_CACHE_DIR из test/backlog. До expensive full gates mandatory. После будущей реализации primary full→meta→evaluate→export→clinical→figures commands прописать в `docs/reproducibility.md` с фактическими flags и immutable manifest selection; не выдавать пока placeholder `make_figures.py` за working command. Exact revision checkout/select инструкции в final guide должны ссылаться на actual release commit, сейчас он неизвестен.

Обеспечить два уровня воспроизведения: **A** saved validated aggregate artifacts→all metrics/figures/report numbers без training (быстро); **B** source acquisition→real full benchmarks→meta data→evaluation/model (дорого, measured budget). Raw clinical source data/токены не входят в GitHub package; sources/checksums/terms instructions — входят. Если не разрешено распространять machine-readable sensitive input, публиковать aggregate allowed products и reproducible local acquisition route, честно указать ограничения.

## 7. Final acceptance checklist

- Real source/version/license/family/split evidence for actual corpus, no made-up IDs/sizes/licenses.
- Exact full protocol or explicitly versioned clinical exception, complete failures/exclusion ledger, smoke isolated.
- One dataset observation, explicit predictor allowlist, no base/meta/patient/temporal leakage found в проверенном scope.
- Held-out comparisons against all required baselines, mean raw regret/uncertainty, primary model fixed prospectively.
- Frozen general-only export/inference works, fallback logged, clinical zero-shot independent.
- RQ1–3 answered по evidence, включая negative/inconclusive findings; no universal family/medical deployment claim.
- All figures/tables regenerate from saved artifacts with hashes; report/deck/demo counts/units match.
- Tests/CI/clean-clone/operator review pass,70 requirements имеют evidence/status или justified out-of-scope for optional.
- No secrets/raw clinical rows/restricted source copies inadvertently tracked; institutional required files checked when rubric available.

Если какого-то обязательного evidence нет, output status остаётся pending/blocked/partial; имя файла и красивая презентация не заменяют завершённое исследование.

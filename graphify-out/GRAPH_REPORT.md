# Graph Report - ML Model Recommender  (2026-10-31)

## Corpus Check
- 67 files · ~48,671 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 564 nodes · 1124 edges · 39 communities (16 shown, 23 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.89)
- Token cost: unavailable for host-agent semantic extraction (usage metadata not exposed); AST uses no LLM. Placeholder zeros are not measured usage or zero cost.

## Graph Freshness
- Built from commit: `b8505f4f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after source changes; AST is deterministic, while semantic extraction consumes host-agent or configured API usage.

## Community Hubs (Navigation)
- Dataset Loading and CLI
- Research Tasks and Sources
- Dense Preprocessing Contracts
- System Architecture and Reproducibility
- Model Search and Benchmark
- Portable Locked CI
- Meta Learning and Evaluation
- Research Decisions and History
- Meta Dataset Schema
- Benchmark Result Schema
- Experiment Design and Risks
- Dataset Identity and Target
- Offline Network Isolation
- Requirements and Deliverables
- Feature Roles and Labels
- Registry Schema Structure
- Excluded Feature Schema
- Clinical Admission Policy
- Scaffold Packaging Inventory
- Expected Row Schema
- Dataset Family Schema
- OpenML Identifier Schema
- Original Source URL Schema
- Selection Reason Schema
- Source URL Schema
- Split Notes Schema
- Split Strategy Schema
- Dataset Version Schema
- Upstream Audit Shell Helper
- Project Package Identity

## God Nodes (most connected - your core abstractions)
1. `P033 Task Backlog` - 42 edges
2. `fit_transform_checked()` - 23 edges
3. `make_preprocessor()` - 21 edges
4. `characterize()` - 17 edges
5. `transform_checked()` - 16 edges
6. `run_benchmark()` - 15 edges
7. `_tune_family()` - 15 edges
8. `P033-008: Split/duplicate admission gates` - 15 edges
9. `_refit_family()` - 14 edges
10. `Research and Experiment Plan` - 14 edges

## Surprising Connections (you probably didn't know these)
- `D013: prespecified scaled Ridge alpha 1` --conceptually_related_to--> `train_recommender()`  [INFERRED]
  docs/decisions.md → src/model_recommender/recommender.py
- `D014: family LOGO and paired regret` --conceptually_related_to--> `evaluate_recommender()`  [INFERRED]
  docs/decisions.md → src/model_recommender/evaluation.py
- `Frozen experiment protocol 0.1` --conceptually_related_to--> `run_benchmark()`  [INFERRED]
  docs/experiment-protocol.md → src/model_recommender/runner.py
- `P033-005: Protocol and candidate parity` --references--> `BenchmarkProtocol`  [EXTRACTED]
  docs/TASK_BACKLOG.md → src/model_recommender/runner.py
- `Historical project audit` --references--> `load_dataset()`  [EXTRACTED]
  docs/PROJECT_AUDIT.md → src/model_recommender/datasets.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Five reviewed pilot sources share bounded source admission** — docs_data_dictionary_source_admission, docs_data_dictionary_credit_g, docs_data_dictionary_ionosphere, docs_data_dictionary_spambase, docs_data_dictionary_adult, docs_data_dictionary_tic_tac_toe [EXTRACTED 1.00]
- **Three Primary Research Questions** — docs_experiment_plan_rq1_unseen_selection, docs_experiment_plan_rq2_descriptor_associations, docs_experiment_plan_rq3_zero_shot_transfer [EXTRACTED 1.00]

## Communities (39 total, 23 thin omitted)

### Community 0 - "Dataset Loading and CLI"
Cohesion: 0.052795031055900624
Nodes (41): main(), main(), main(), _missing(), _overlap(), main(), main(), main() (+33 more)

### Community 1 - "Research Tasks and Sources"
Cohesion: 0.07990867579908675
Nodes (73): adult: retrospective income source card, credit-g: static credit-risk source card, Pilot data dictionary, ionosphere: processed radar-return source card, Dataset-specific UCI CC BY 4.0 permission evidence, Run-log and meta schemas provisional, Pinned source, family and clinical roles, Source admission does not clear benchmark readiness (+65 more)

### Community 2 - "Dense Preprocessing Contracts"
Cohesion: 0.0936026936026936
Nodes (28): DensePreprocessor, ensure_dense_matrix_fits(), FeatureRoles, fit_transform_checked(), infer_feature_roles(), make_preprocessor(), MatrixTooLargeError, transform_checked() (+20 more)

### Community 3 - "System Architecture and Reproducibility"
Cohesion: 0.06968641114982578
Nodes (37): Clinical transfer (planned later), Repository Architecture, Full benchmark JSON per dataset, Held-out dataset-family evaluation, HistGradientBoosting pipeline, Meta-dataset: one row per dataset, MLP pipeline, Pinned OpenML registry (+29 more)

### Community 4 - "Model Search and Benchmark"
Cohesion: 0.1337126600284495
Nodes (20): build_estimator(), candidates_for_family(), gbdt_candidates(), mlp_candidates(), ModelCandidate, needs_numeric_scaling(), _sample_with_baseline(), estimate_dense_bytes() (+12 more)

### Community 5 - "Portable Locked CI"
Cohesion: 0.0625
Nodes (31): Two consecutive clean Windows/Ubuntu CI attempts, concurrency, cancel-in-progress, group, run, jobs, test, os (+23 more)

### Community 6 - "Meta Learning and Evaluation"
Cohesion: 0.08870967741935484
Nodes (8): recommendation_regret(), make_meta_estimator(), train_recommender(), TrainedRecommender, make_frame(), test_leave_one_family_out_evaluation(), test_regret(), test_train_and_recommend_gap_regressor()

### Community 7 - "Research Decisions and History"
Cohesion: 0.0873015873015873
Nodes (26): Implementation Update 2026-09-24, Historical packaging validation: 35 tests and synthetic smoke, D011: strict admission and identity, D012: general-only fence and allowlist, D013: prespecified scaled Ridge alpha 1, D014: family LOGO and paired regret, D015: matching inference descriptor sampler, D016: feature schema and missingness handling (+18 more)

### Community 8 - "Meta Dataset Schema"
Cohesion: 0.07407407407407407
Nodes (26): enum, additionalProperties, type, type, type, type, type, type (+18 more)

### Community 9 - "Benchmark Result Schema"
Cohesion: 0.08695652173913043
Nodes (22): additionalProperties, type, required, type, type, const, properties, aggregate (+14 more)

### Community 10 - "Experiment Design and Risks"
Cohesion: 0.14619883040935672
Nodes (19): Clinical Zero-Shot Protocol, Compact Meta-Feature Schema v2, Research and Experiment Plan, Family-Cluster Paired Regret Bootstrap, Frozen Binary Protocol 0.1, Full Protocol: 366 Fits per Dataset, Matching Development Descriptor Sampling, Paired Fold-Local Nested Search (+11 more)

### Community 11 - "Dataset Identity and Target"
Cohesion: 0.15384615384615385
Nodes (13): type, type, type, type, type, properties, clinical, license (+5 more)

### Community 13 - "Requirements and Deliverables"
Cohesion: 0.19696969696969696
Nodes (12): 21-Section Academic Report, Machine-Readable Artifact Evidence Chain, Final Deliverables Specification, 12-Slide Research Presentation, Requirements and Traceability, FR-003: Source and License Evidence, FR-018: Explicit Full-Result Admission, FR-030: Labelled Unseen Inference (+4 more)

### Community 14 - "Feature Roles and Labels"
Cohesion: 0.2
Nodes (10): items, type, items, type, type, items, type, categorical_features (+2 more)

### Community 15 - "Registry Schema Structure"
Cohesion: 0.2857142857142857
Nodes (6): additionalProperties, description, required, $schema, title, type

### Community 16 - "Excluded Feature Schema"
Cohesion: 0.6666666666666666
Nodes (3): items, type, excluded_features

## Knowledge Gaps
- **46 isolated node(s):** `ml-p033-model-recommender`, `Family-Cluster Paired Regret Bootstrap`, `Q01: University Rubric Unknown`, `Matching Development Descriptor Sampling`, `FR-018: Explicit Full-Result Admission` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 200 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Portable reproducibility guide` connect `System Architecture and Reproducibility` to `Portable Locked CI`, `Research Decisions and History`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `fit_transform_checked()` (e.g. with `.fit_scaler()` and `.fit_structure()`) actually correct?**
  _`fit_transform_checked()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ml-p033-model-recommender`, `Family-Cluster Paired Regret Bootstrap`, `Q01: University Rubric Unknown` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Dataset Loading and CLI` be split into smaller, more focused modules?**
  _Cohesion score 0.052795031055900624 - nodes in this community are weakly interconnected._
- **Why does `Frozen experiment protocol 0.1` connect `System Architecture and Reproducibility` to `Research Tasks and Sources`, `Experiment Design and Risks`, `Model Search and Benchmark`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Should `Research Tasks and Sources` be split into smaller, more focused modules?**
  _Cohesion score 0.07990867579908675 - nodes in this community are weakly interconnected._
- **Why does `Historical project audit` connect `Research Decisions and History` to `Dataset Loading and CLI`, `System Architecture and Reproducibility`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._

## Incremental update and extraction audit

- Source commit: `b8505f4f0d7945baebe3d9e897b48df09d3268b9`; previous snapshot: `b316b5d`. Graph-only publication commits do not change this source baseline.
- Re-extracted 3 code/JSON inputs and 5 documents; all 5 changed documents were read to the last line and all 22 document coverage receipts match disk.
- Current task evidence: P033-001 through P033-004 DONE within their cards; P033-005 READY and unstarted; P033-023 DECISION. Source admission is not benchmark readiness.
- Code/doc nodes describe the source at build time; roadmap or accepted design is not implemented behavior. Historical audit statements remain dated historical evidence.
- AST yielded no symbols for the new metadata JSON; its source evidence is represented by the reviewed dictionary nodes. Previous no-symbol inputs are retained in coverage.json.
- Graph is undirected. Direction and parallel relationships may collapse in navigation; extraction-audit.json retains raw source relationships and health.json records diagnostics.
- Integrity gate: {"dangling_endpoint_edges": 164, "self_loop_edges": 0, "directed_same_endpoint_collapsed_edges": 49, "undirected_same_endpoint_collapsed_edges": 56}.
- Raw unresolved AST endpoints include package/import/attribute targets; they remain visible in the audit rather than being silently removed. The final exported graph has no dangling links.
- graphify-out/ is a complete published snapshot at the user's request, including cache/manifest and machine-local pointers. Only graph output changes in this refresh; project dependencies/protocol and scientific results are unchanged. See https://docs.graphify.com/guides/team-workflows.

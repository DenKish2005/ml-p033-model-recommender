# Graph Report - ML Model Recommender  (2026-10-31)

## Corpus Check
- Corpus is ~41,149 words - fits in a single context window. You may not need a graph.

## Summary
- 492 nodes · 885 edges · 38 communities (16 shown, 22 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.89)
- Token cost: unavailable for host-agent semantic extraction (usage metadata not exposed); AST uses no LLM. Placeholder zeros are not measured usage or zero cost.

## Graph Freshness
- Built from commit: `b316b5d0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Research Roadmap and Gates
- Dataset Loading and CLI
- Nested Benchmark and Preprocessing
- Meta Learning and Evaluation
- Research Decisions and Evidence
- Portable Locked CI
- Meta Dataset Schema
- System Architecture and Scope
- Benchmark Result Schema
- Offline Tests and Features
- Dataset Loader Regression Tests
- Dataset Identity and Target
- Feature Roles and Labels
- Registry Schema Structure
- Data Dictionary Contracts
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
1. `characterize()` - 18 edges
2. `run_benchmark()` - 16 edges
3. `read_registry()` - 15 edges
4. `_tune_family()` - 15 edges
5. `Research and Experiment Plan` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Pilot data dictionary` --conceptually_related_to--> `read_registry()`  [INFERRED]
  docs/data_dictionary.md → src/model_recommender/datasets.py
- `D014: family LOGO and paired regret` --conceptually_related_to--> `evaluate_recommender()`  [INFERRED]
  docs/decisions.md → src/model_recommender/evaluation.py
- `D013: prespecified scaled Ridge alpha 1` --conceptually_related_to--> `train_recommender()`  [INFERRED]
  docs/decisions.md → src/model_recommender/recommender.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three Primary Research Questions** — docs_experiment_plan_rq1_unseen_selection, docs_experiment_plan_rq2_descriptor_associations, docs_experiment_plan_rq3_zero_shot_transfer [EXTRACTED 1.00]
- **P033-002 Environment Acceptance** — docs_task_backlog_p033_002, docs_requirements_nfr_007_locked_portability, docs_requirements_nfr_018_offline_testability, docs_test_and_acceptance_plan_t08 [EXTRACTED 1.00]

## Communities (38 total, 22 thin omitted)

### Community 0 - "Research Roadmap and Gates"
Cohesion: 0.05
Nodes (64): Implementation Update 2026-09-24, Historical packaging validation: 35 tests and synthetic smoke, Clinical Zero-Shot Protocol, Compact Meta-Feature Schema v2, Research and Experiment Plan, Family-Cluster Paired Regret Bootstrap, Frozen Binary Protocol 0.1, Full Protocol: 366 Fits per Dataset (+56 more)

### Community 1 - "Dataset Loading and CLI"
Cohesion: 0.09
Nodes (24): Existing Engineering Foundation, main(), main(), _missing(), _overlap(), main(), main(), main() (+16 more)

### Community 2 - "Nested Benchmark and Preprocessing"
Cohesion: 0.09
Nodes (26): build_estimator(), candidates_for_family(), gbdt_candidates(), mlp_candidates(), ModelCandidate, needs_numeric_scaling(), _sample_with_baseline(), DensePreprocessor (+18 more)

### Community 3 - "Meta Learning and Evaluation"
Cohesion: 0.07
Nodes (17): D013: prespecified scaled Ridge alpha 1, main(), recommendation_regret(), benchmark_result_to_row(), build_meta_dataset(), meta_feature_columns(), make_meta_estimator(), train_recommender() (+9 more)

### Community 4 - "Research Decisions and Evidence"
Cohesion: 0.06
Nodes (40): D011: strict admission and identity, D012: general-only fence and allowlist, D014: family LOGO and paired regret, D015: matching inference descriptor sampler, D016: feature schema and missingness handling, D017: source-specific clinical split, D018: family bootstrap uncertainty, D019: cohort grouping without silent dedup (+32 more)

### Community 5 - "Portable Locked CI"
Cohesion: 0.06
Nodes (30): concurrency, cancel-in-progress, group, run, jobs, test, os, name (+22 more)

### Community 6 - "Meta Dataset Schema"
Cohesion: 0.07
Nodes (26): enum, additionalProperties, type, type, type, type, type, type (+18 more)

### Community 7 - "System Architecture and Scope"
Cohesion: 0.14
Nodes (21): Clinical transfer (planned later), Repository Architecture, Full benchmark JSON per dataset, Held-out dataset-family evaluation, HistGradientBoosting pipeline, Meta-dataset: one row per dataset, MLP pipeline, Pinned OpenML registry (+13 more)

### Community 8 - "Benchmark Result Schema"
Cohesion: 0.09
Nodes (22): additionalProperties, type, required, type, type, const, properties, aggregate (+14 more)

### Community 9 - "Offline Tests and Features"
Cohesion: 0.13
Nodes (5): offline_sockets(), test_empty_and_infinite_features(), test_invalid_targets(), test_misaligned_target(), test_default_suite_blocks_network()

### Community 10 - "Dataset Loader Regression Tests"
Cohesion: 0.16
Nodes (9): source(), spec(), test_load_preserves_missingness_and_encodes_positive_class(), fetch(), test_pilot_registry(), test_registry_rejects_duplicate_entries(), test_reject_invalid_data(), test_reject_invalid_spec() (+1 more)

### Community 11 - "Dataset Identity and Target"
Cohesion: 0.15
Nodes (13): type, type, type, type, type, properties, clinical, license (+5 more)

### Community 12 - "Feature Roles and Labels"
Cohesion: 0.20
Nodes (10): items, type, items, type, type, items, type, categorical_features (+2 more)

### Community 13 - "Registry Schema Structure"
Cohesion: 0.29
Nodes (6): additionalProperties, description, required, $schema, title, type

### Community 14 - "Data Dictionary Contracts"
Cohesion: 0.67
Nodes (3): Pilot data dictionary, Run-log and meta schemas provisional, Pinned source, family and clinical roles

### Community 15 - "Excluded Feature Schema"
Cohesion: 0.67
Nodes (3): items, type, excluded_features

## Knowledge Gaps
- **32 isolated node(s):** `ml-p033-model-recommender`, `Implementation Update 2026-09-24`, `Packaged Scaffold Manifest`, `Full protocol: 360 inner fits plus 6 refits per dataset`, `Pilot five datasets then expand nonclinical corpus` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 176 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Portable reproducibility guide` connect `Research Decisions and Evidence` to `Research Roadmap and Gates`, `System Architecture and Scope`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `run_benchmark()` (e.g. with `Frozen experiment protocol 0.1` and `LoadedDataset`) actually correct?**
  _`run_benchmark()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Why does `Historical project audit` connect `Research Decisions and Evidence` to `Research Roadmap and Gates`, `Dataset Loading and CLI`, `System Architecture and Scope`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
## Extraction limitations and audit

- All 22 semantic source documents were read through their last line; coverage was checked against disk.
- Two AST inputs yielded no symbols: `pyproject.toml` and `src/model_recommender/__init__.py`.
- Code/doc nodes describe the source at build time; roadmap or accepted design is not implemented behavior.
- Graph is undirected by default. Relation direction and multiple same-endpoint relationships may be collapsed in navigation; `extraction-audit.json` preserves the full extraction.
- graphify-out/ was initially generated as untracked output and is now published as a complete versioned snapshot at the user's request. Machine-local pointer/cache provenance and snapshot limitations are described in README.md; no source files or locked project dependencies were changed. See https://docs.graphify.com/guides/team-workflows.
- Integrity gate: {"dangling_endpoint_edges": 155, "directed_same_endpoint_collapsed_edges": 36, "undirected_same_endpoint_collapsed_edges": 39}.
- The 155 unresolved raw AST endpoints include external/package/import targets; the builder represents external references and the final graph JSON has no dangling links. These raw findings remain in health.json.

# Benchmark result admission (P033-006)

The [runtime validator](../src/model_recommender/result_validation.py) checks
existing runner v1 evidence. Research admission requires canonical full protocol
0.1, independently of the `research_valid`, `status` and `protocol.name` claims.
It verifies every signature field, source identifiers/types, both families,
canonical sampled parameters/order (including baseline), complete folds/trials,
inner-BA selection with exact ties by candidate order, preprocessing matrix sizes,
refit/scoring evidence, success flags/errors and finite bounded scores.

Trial means, paired outer gaps, aggregate means/gap/winner/near-tie and raw
outer-training descriptor means must agree. Arithmetic uses absolute tolerance
`1e-12`, relative tolerance zero: sufficient for double-precision aggregation of
the recorded scores, not for rounded result tables. Signature/parameters/counts
are exact; booleans are never numbers. MLP JSON arrays and Python tuples have the
same parameter meaning. Exact ties use recomputed, unrounded inner means.

The ten existing v1 descriptors are required and their recorded aggregation is
checked; extra numeric descriptors remain possible under v1. This is not the
predictor allowlist or clinical-training fence of P033-007.

## Selection and report

`select_research_results(paths)` in [meta_dataset.py](../src/model_recommender/meta_dataset.py)
returns `ResultSelection.accepted` payloads and `.report`. Every supplied input,
including repeated paths, receives a path, outcome, stable code and readable reason.
Paths are sorted lexically; there is no score, mtime or input-order preference.
Unreadable files, malformed/duplicate-key/non-finite JSON, noncanonical protocols
and incomplete/failed artifacts are rejected individually. Original files are
preserved; neither scores nor flags are repaired. Empty selection still returns a
report with zero accepted results.

Duplicate policy is conservative: **reject every same-mode project claim sharing
a dataset name or OpenML ID, across all versions**. This covers copies, aliases,
repeated paths, different scores and failed/corrupt full claims with readable
identifiers. Invalid full claims cannot be hidden to select a favourable successful
retry. Each duplicate entry retains its original validation reason when applicable.
Smoke claims do not compete with full claims of the same source. Operators must
resolve conflicting input collections explicitly, retaining the original attempts;
the tool does not choose a preferred artifact.

This policy uses only identifiers already recorded by the runner: project,
dataset name, OpenML ID/version, family/clinical metadata and protocol. It cannot
detect relabelled IDs, shared cohorts, semantic duplicates or symmetry equivalents.
It does not verify registry membership or invent missing checksum/git/environment
fingerprints. Source review/split/cohort gates remain P033-008/009; complete
provenance and recovery remain P033-011. Admission validates recorded evidence,
not the truth of raw partitions or independently reproduced fits.

`build_meta_dataset(paths, report_path=...)` uses the same research selection.
Its DataFrame carries `attrs['admission_report']`; the optional JSON report is
written even when all inputs are rejected. In that case `NoAcceptedResults`
contains `.report` and the builder raises instead of creating an empty table.
No inputs produces the same explicit zero-count error/report. A report cannot
overwrite an input artifact.

## Compatibility

Older minimal aggregate-only fixtures/artifacts no longer qualify as research
inputs. Preserve originals and their historical interpretation; adding success
flags is insufficient. Complete synthetic fixtures live only under the `test:`
namespace in [tests/benchmark_artifacts.py](../tests/benchmark_artifacts.py).
They are engineering evidence, not research results. The scientific settings,
candidate sampling, frozen protocol, dependencies and lock remain unchanged.

See [P033-006](TASK_BACKLOG.md#p033-006--strict-result-admission),
[protocol 0.1](experiment-protocol.md) and [D011](decisions.md#d011--strict-admission-identity-and-provenance).

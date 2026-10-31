import json
from copy import deepcopy

import pytest
from benchmark_artifacts import complete_result

from model_recommender.meta_dataset import (
    NoAcceptedResults,
    build_meta_dataset,
    select_research_results,
)


def write_result(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_mixed_selection_exact_identities_report_and_builder(tmp_path):
    full = write_result(tmp_path / "full.json", complete_result())
    smoke = write_result(tmp_path / "smoke.json", complete_result(smoke=True))
    excluded_payload = complete_result("test:excluded", 900002)
    excluded_payload.update(status="excluded", research_valid=False, aggregate=None)
    excluded = write_result(tmp_path / "excluded.json", excluded_payload)
    spoofed_payload = complete_result("test:spoof", 900003, smoke=True)
    spoofed_payload["protocol"]["name"] = "full"
    spoofed_payload["research_valid"] = True
    spoofed = write_result(tmp_path / "spoof.json", spoofed_payload)
    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"project":', encoding="utf-8")
    missing = tmp_path / "missing.json"
    paths = [smoke, malformed, excluded, full, spoofed, missing]
    selected = select_research_results(paths)
    assert [item["dataset"]["name"] for item in selected.accepted] == ["test:admission"]
    report = selected.report
    assert (report["input_count"], report["accepted_count"], report["rejected_count"]) == (6, 1, 5)
    entries = {entry["path"]: entry for entry in report["inputs"]}
    assert entries[str(full)]["code"] == "accepted"
    assert entries[str(smoke)]["reason"].startswith("protocol.name:")
    assert entries[str(excluded)]["reason"].startswith("status:")
    assert "outer_seeds" in entries[str(spoofed)]["reason"]
    assert entries[str(malformed)]["code"] == "malformed_json"
    assert entries[str(missing)]["code"] == "unreadable_input"
    assert select_research_results(list(reversed(paths))).report == report
    report_path = tmp_path / "reports" / "admission.json"
    frame = build_meta_dataset(paths, report_path=report_path)
    assert frame["dataset"].tolist() == ["test:admission"]
    assert frame["mean_balanced_accuracy_mlp"].tolist() == [0.73]
    assert frame["performance_gap_mlp_minus_gbdt"].tolist() == pytest.approx([0.03])
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    assert frame.attrs["admission_report"] == report


@pytest.mark.parametrize("kind", ["copy", "alias", "name", "version", "failed", "corrupt"])
def test_duplicate_claims_reject_all_without_score_or_order_selection(tmp_path, kind):
    original = complete_result()
    other = deepcopy(original)
    if kind == "alias":
        other["dataset"]["name"] = "test:alias"
    elif kind == "name":
        other["dataset"]["openml_id"] = 900099
    elif kind == "version":
        other["dataset"]["version"] = 2
    elif kind == "failed":
        other.update(status="excluded", research_valid=False, aggregate=None)
    elif kind == "corrupt":
        other["aggregate"]["mean_balanced_accuracy_mlp"] = 0.99
    a = write_result(tmp_path / "a.json", original)
    b = write_result(tmp_path / "b.json", other)
    selection = select_research_results([b, a])
    assert selection.accepted == []
    assert selection.report["rejected_count"] == 2
    assert [entry["code"] for entry in selection.report["inputs"]] == ["duplicate_identity"] * 2
    assert all(
        str(a) in entry["reason"] and str(b) in entry["reason"]
        for entry in selection.report["inputs"]
    )
    assert select_research_results([a, b]).report == selection.report
    if kind in ("failed", "corrupt"):
        assert "validation_reason" in selection.report["inputs"][1]


def test_repeated_path_is_reported_twice_and_cannot_duplicate_rows(tmp_path):
    path = write_result(tmp_path / "full.json", complete_result())
    selection = select_research_results([path, path])
    assert selection.report["input_count"] == 2
    assert selection.report["accepted_count"] == 0
    assert all(entry["code"] == "duplicate_identity" for entry in selection.report["inputs"])


@pytest.mark.parametrize(
    "content",
    ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e999}', "[]", "null", '"text"'],
)
def test_strict_json_diagnostics(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    report = select_research_results([path]).report
    assert report["accepted_count"] == 0
    assert report["inputs"][0]["code"] == (
        "invalid_result" if content in ("[]", "null", '"text"') else "malformed_json"
    )


@pytest.mark.parametrize("empty", [True, False])
def test_empty_or_all_rejected_preserves_report_before_error(tmp_path, empty):
    paths = [] if empty else [write_result(tmp_path / "smoke.json", complete_result(smoke=True))]
    report_path = tmp_path / "report.json"
    with pytest.raises(NoAcceptedResults) as exc:
        build_meta_dataset(paths, report_path=report_path)
    assert exc.value.report == json.loads(report_path.read_text(encoding="utf-8"))
    assert exc.value.report["input_count"] == (0 if empty else 1)
    assert exc.value.report["accepted_count"] == 0


def test_report_must_not_overwrite_original(tmp_path):
    path = write_result(tmp_path / "full.json", complete_result())
    original = path.read_bytes()
    with pytest.raises(ValueError, match="overwrite"):
        build_meta_dataset([path], report_path=path)
    assert path.read_bytes() == original

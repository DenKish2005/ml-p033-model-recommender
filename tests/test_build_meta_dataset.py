import json
import runpy
import sys
from pathlib import Path

import pandas as pd
import pytest
from benchmark_artifacts import complete_result

from model_recommender.meta_dataset import (
    NoAcceptedResults,
    benchmark_result_to_row,
    build_development_meta_dataset,
    build_meta_dataset,
    meta_feature_columns,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_meta_dataset.py"


def invoke(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), *map(str, args)])
    runpy.run_path(str(SCRIPT), run_name="__main__")


def write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_builder_script_mixed_folder_csv_and_report(monkeypatch, tmp_path, capsys):
    inputs = tmp_path / "input with spaces"
    inputs.mkdir()
    write(inputs / "full.json", complete_result())
    write(inputs / "smoke.json", complete_result(smoke=True))
    (inputs / "broken.json").write_text("{", encoding="utf-8")
    output = tmp_path / "out" / "research.csv"
    report = tmp_path / "reports" / "admissions.json"
    invoke(monkeypatch, "--results-dir", inputs, "--output", output, "--report", report)
    frame = pd.read_csv(output)
    assert frame["dataset"].tolist() == ["test:admission"]
    assert frame["performance_gap_mlp_minus_gbdt"].tolist() == pytest.approx([0.03])
    ledger = json.loads(report.read_text(encoding="utf-8"))
    assert (ledger["input_count"], ledger["accepted_count"], ledger["rejected_count"]) == (3, 1, 2)
    assert "rejected 2/3" in capsys.readouterr().out


def test_development_api_is_validated_smoke_only_and_visibly_marked(tmp_path):
    full = write(tmp_path / "full.json", complete_result())
    smoke = write(tmp_path / "smoke.json", complete_result(smoke=True))
    for frame in (
        build_development_meta_dataset([full, smoke]),
        build_meta_dataset([full, smoke], require_research_valid=False),
    ):
        assert frame["dataset"].tolist() == ["test:admission"]
        assert frame["development_only"].tolist() == [True]
        assert frame["result_mode"].tolist() == ["smoke"]
        assert frame.attrs["admission_report"]["mode"] == "smoke"
        assert frame.attrs["admission_report"]["rejected_count"] == 1
        with pytest.raises(ValueError, match="numeric"):
            meta_feature_columns(frame)
    with pytest.raises(ValueError, match="protocol.name"):
        benchmark_result_to_row(complete_result(), require_research_valid=False)
    bad = complete_result(smoke=True)
    bad["outer_splits"][0]["families"]["DNN"]["refit_seconds"] = None
    with pytest.raises(ValueError, match="refit_seconds"):
        benchmark_result_to_row(bad, require_research_valid=False)
    with pytest.raises(NoAcceptedResults):
        build_development_meta_dataset([full])
    for flag in (0, 1, None):
        with pytest.raises(ValueError, match="boolean"):
            benchmark_result_to_row(bad, require_research_valid=flag)
        with pytest.raises(ValueError, match="boolean"):
            build_meta_dataset([smoke], require_research_valid=flag)


def test_development_script_does_not_mix_full_or_overwrite_primary(monkeypatch, tmp_path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    write(inputs / "full.json", complete_result())
    write(inputs / "smoke.json", complete_result(smoke=True))
    primary = tmp_path / "meta_dataset.csv"
    primary.write_text("preserve primary", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, "--results-dir", inputs, "--allow-smoke", "--output", primary)
    assert exc.value.code == 2
    assert primary.read_text(encoding="utf-8") == "preserve primary"
    output = tmp_path / "dev" / "meta_dataset.development.csv"
    invoke(monkeypatch, "--results-dir", inputs, "--allow-smoke", "--output", output)
    frame = pd.read_csv(output)
    assert frame["result_mode"].tolist() == ["smoke"]
    assert frame["development_only"].tolist() == [True]
    report = json.loads(output.with_suffix(".admission.json").read_text(encoding="utf-8"))
    assert report["development_only"] is True
    assert report["accepted_count"] == report["rejected_count"] == 1


@pytest.mark.parametrize("empty", [True, False])
def test_script_all_rejected_reports_nonzero_without_creating_csv(monkeypatch, tmp_path, empty):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    if not empty:
        write(inputs / "smoke.json", complete_result(smoke=True))
    output = tmp_path / "out.csv"
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, "--results-dir", inputs, "--output", output)
    assert exc.value.code == 2
    assert not output.exists()
    report = json.loads(output.with_suffix(".admission.json").read_text(encoding="utf-8"))
    assert report["input_count"] == (0 if empty else 1)
    assert report["accepted_count"] == 0


def test_script_output_report_and_input_collisions(monkeypatch, tmp_path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    path = write(inputs / "full.json", complete_result())
    original = path.read_bytes()
    for output, report in (
        (path, tmp_path / "report.json"),
        (tmp_path / "out.csv", inputs / "report.json"),
        (tmp_path / "same", tmp_path / "same"),
    ):
        with pytest.raises(SystemExit) as exc:
            invoke(monkeypatch, "--results-dir", inputs, "--output", output, "--report", report)
        assert exc.value.code == 2
    assert path.read_bytes() == original


def test_default_development_paths_are_separate(monkeypatch, tmp_path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    write(inputs / "smoke.json", complete_result(smoke=True))
    monkeypatch.chdir(tmp_path)
    invoke(monkeypatch, "--results-dir", inputs, "--allow-smoke")
    assert (tmp_path / "results/development/meta_dataset.development.csv").exists()
    assert not (tmp_path / "results/meta_dataset.csv").exists()

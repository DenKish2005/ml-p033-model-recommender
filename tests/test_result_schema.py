"""Static schema/runtime parity without adding a JSON Schema runtime dependency."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest
from benchmark_artifacts import complete_result

from model_recommender.meta_dataset import benchmark_result_to_row
from model_recommender.model_families import candidates_for_family
from model_recommender.runner import BenchmarkProtocol

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("mode", ["full", "smoke"])
def test_schema_canonical_signature_candidate_mapping_and_complete_shapes(mode):
    schema = json.loads((ROOT / "schemas/model_run.schema.json").read_text(encoding="utf-8"))
    defs = schema["$defs"]
    protocol = BenchmarkProtocol.full() if mode == "full" else BenchmarkProtocol.smoke()
    signature = defs[f"{mode}_protocol"]
    assert signature["additionalProperties"] is False
    assert set(signature["required"]) == set(asdict(protocol))
    expected = json.loads(json.dumps(asdict(protocol)))
    assert {k: v["const"] for k, v in signature["properties"].items()} == expected
    success = defs[f"{mode}_success"]["properties"]
    assert success["research_valid"]["const"] is (mode == "full")
    splits = success["outer_splits"]
    assert splits["minItems"] == splits["maxItems"] == len(protocol.outer_seeds)
    assert [p["properties"]["outer_seed"]["const"] for p in splits["prefixItems"]] == list(
        protocol.outer_seeds
    )
    artifact = complete_result(smoke=mode == "smoke")
    assert set(splits["items"]["required"]) == set(artifact["outer_splits"][0])
    for family in ("GBDT", "DNN"):
        shape = defs[f"{mode}_{family}"]
        family_artifact = artifact["outer_splits"][0]["families"][family]
        assert set(shape["required"]) == set(family_artifact)
        trials = shape["properties"]["trials"]
        assert trials["minItems"] == trials["maxItems"] == protocol.candidate_count
        assert set(trials["items"]["required"]) == set(family_artifact["trials"][0])
        folds = trials["items"]["properties"]["folds"]
        assert folds["minItems"] == folds["maxItems"] == protocol.inner_folds
        assert [p["properties"]["fold"]["const"] for p in folds["prefixItems"]] == list(
            range(protocol.inner_folds)
        )
        expected_candidates = candidates_for_family(family, count=protocol.candidate_count)
        for prefix, candidate in zip(trials["prefixItems"], expected_candidates, strict=True):
            assert prefix["properties"]["candidate_order"]["const"] == candidate.order
            assert prefix["properties"]["params"]["const"] == json.loads(
                json.dumps(candidate.params)
            )
        assert set(defs["fold"]["required"]) == set(family_artifact["trials"][0]["folds"][0])
        assert set(defs["final_preprocessing"]["required"]) == set(
            family_artifact["final_preprocessing"]
        )


def test_schema_local_references_and_research_row_contract():
    for name in ("model_run", "meta_dataset"):
        schema = json.loads((ROOT / f"schemas/{name}.schema.json").read_text(encoding="utf-8"))

        def walk(value, document):
            if isinstance(value, dict):
                if "$ref" in value:
                    assert value["$ref"].startswith("#/$defs/")
                    assert value["$ref"].split("/")[-1] in document["$defs"]
                for item in value.values():
                    walk(item, document)
            elif isinstance(value, list):
                for item in value:
                    walk(item, document)

        walk(schema, schema)
    assert set(schema["required"]) == set(benchmark_result_to_row(complete_result()))
    assert schema["properties"]["development_only"] == {"const": False}
    assert schema["properties"]["result_mode"] == {"const": "full"}
    assert schema["properties"]["mean_balanced_accuracy_mlp"]["maximum"] == 1
    assert schema["properties"]["performance_gap_mlp_minus_gbdt"]["minimum"] == -1

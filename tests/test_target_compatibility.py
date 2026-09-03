from __future__ import annotations

import json
from importlib.resources import files


def test_exact_candidate_target_lane_is_packaged() -> None:
    path = files("orbitfabric_fprime_adapter").joinpath(
        "compatibility/fprime-v4.2.2-fpp-3.2.0.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["status"] == "historical_evidence_candidate"
    assert payload["fprime"] == {
        "version": "v4.2.2",
        "commit": "8a62e455a90b6d4f498c332d45d65a2a819988d8",
    }
    assert payload["fpp"] == {
        "version": "3.2.0",
        "commit": "93f484b7521a8e8894cba25b26e633cc87d8e37a",
    }
    assert payload["evidence"]["canonical_source_acceptance"] == "pending"
    assert payload["claims"] == {
        "exact_pair_only": True,
        "version_range": False,
        "forward_compatibility": False,
        "backward_compatibility": False,
    }

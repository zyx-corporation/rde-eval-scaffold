from scripts.compare_annotations import compare_annotations


def test_compare_annotations_basic_agreement() -> None:
    reference = [
        {
            "id": "sample-1",
            "human_annotation": "Suspicious Drift",
            "risk_flags": ["claim_strength_inflation"],
            "criticality": "medium",
        }
    ]

    candidate = [
        {
            "id": "sample-1",
            "llm_annotation": "Suspicious Drift",
            "risk_flags": ["claim_strength_inflation"],
            "criticality": "medium",
        }
    ]

    result = compare_annotations(reference, candidate)

    assert result["comparable"] == 1
    assert result["label_agreement"] == 1.0
    assert result["criticality_agreement"] == 1.0
    assert result["risk_flag_exact_agreement"] == 1.0
    assert result["risk_flag_precision"] == 1.0
    assert result["risk_flag_recall"] == 1.0
    assert result["risk_flag_f1"] == 1.0
    assert result["disagreements"] == []


def test_compare_annotations_detects_disagreement() -> None:
    reference = [
        {
            "id": "sample-1",
            "human_annotation": "Suspicious Drift",
            "risk_flags": ["claim_strength_inflation"],
            "criticality": "medium",
        }
    ]

    candidate = [
        {
            "id": "sample-1",
            "llm_annotation": "Critical Distortion",
            "risk_flags": ["context_drift"],
            "criticality": "high",
        }
    ]

    result = compare_annotations(reference, candidate)

    assert result["label_agreement"] == 0.0
    assert result["criticality_agreement"] == 0.0
    assert result["risk_flag_exact_agreement"] == 0.0
    assert len(result["disagreements"]) == 1


def test_compare_annotations_missing_records() -> None:
    reference = [
        {
            "id": "sample-1",
            "human_annotation": "Preserved",
            "risk_flags": [],
            "criticality": "low",
        }
    ]

    candidate = [
        {
            "id": "sample-2",
            "llm_annotation": "Preserved",
            "risk_flags": [],
            "criticality": "low",
        }
    ]

    result = compare_annotations(reference, candidate)

    assert result["comparable"] == 0
    assert result["missing_candidate"] == ["sample-1"]
    assert result["missing_reference"] == ["sample-2"]

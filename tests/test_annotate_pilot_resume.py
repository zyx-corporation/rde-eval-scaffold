from pathlib import Path

from scripts.annotate_pilot import load_annotated_ids


def test_resume_reads_only_selected_output_file(tmp_path: Path) -> None:
    annotation_dir = tmp_path / "annotations"
    annotation_dir.mkdir()

    selected_output = annotation_dir / "annotations.jsonl"
    selected_output.write_text('{"id":"pilot-sum-001"}\n', encoding='utf-8')

    sibling_output = annotation_dir / "pilot_30_deepseek.jsonl"
    sibling_output.write_text('{"id":"pilot-sum-999"}\n', encoding='utf-8')

    ids = load_annotated_ids(selected_output)

    assert "pilot-sum-001" in ids
    assert "pilot-sum-999" not in ids

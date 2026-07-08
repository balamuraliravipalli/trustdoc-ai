from pathlib import Path


def test_system_prompt_has_grounding_rules():
    rag_file = Path(__file__).resolve().parents[1] / "app" / "services" / "rag.py"
    text = rag_file.read_text(encoding="utf-8")
    assert "ONLY" in text
    assert "uploaded documents" in text
    assert "untrusted evidence" in text
    assert "Never invent citations" in text

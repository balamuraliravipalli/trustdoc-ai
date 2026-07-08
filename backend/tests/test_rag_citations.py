from app.services.rag import extract_cited_indices, is_refusal_answer, REFUSAL


def test_extract_cited_indices():
    assert extract_cited_indices('Remote work is allowed [1]. MFA is required [2].') == {1, 2}


def test_refusal_detection():
    assert is_refusal_answer(REFUSAL)

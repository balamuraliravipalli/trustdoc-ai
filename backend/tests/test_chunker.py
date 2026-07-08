from app.services.chunker import chunk_pages


def test_chunk_pages_preserves_page_numbers():
    pages = [{"page": 2, "text": " ".join(["word"] * 50)}]
    chunks = chunk_pages(pages, max_words=20, overlap_words=5)
    assert len(chunks) >= 3
    assert all(c.page == 2 for c in chunks)


def test_overlap_smaller_than_max():
    pages = [{"page": 1, "text": "hello world"}]
    try:
        chunk_pages(pages, max_words=10, overlap_words=10)
    except ValueError as exc:
        assert "overlap_words" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

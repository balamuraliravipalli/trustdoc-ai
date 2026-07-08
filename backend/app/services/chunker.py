import re
from dataclasses import dataclass


@dataclass
class ChunkInput:
    text: str
    page: int
    chunk_index: int


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_pages(pages: list[dict], max_words: int = 350, overlap_words: int = 60) -> list[ChunkInput]:
    """Chunk each PDF page with overlap while preserving page metadata."""
    if overlap_words >= max_words:
        raise ValueError("overlap_words must be smaller than max_words")

    chunks: list[ChunkInput] = []
    global_index = 0

    for page_obj in pages:
        page_num = int(page_obj["page"])
        words = clean_text(page_obj["text"]).split()
        if not words:
            continue

        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_text = " ".join(words[start:end]).strip()
            if chunk_text:
                chunks.append(ChunkInput(text=chunk_text, page=page_num, chunk_index=global_index))
                global_index += 1
            if end == len(words):
                break
            start = max(0, end - overlap_words)

    return chunks


def estimate_tokens(text: str) -> int:
    # Lightweight approximation: one token is roughly 0.75 words for English-like text.
    return max(1, int(len(text.split()) / 0.75))

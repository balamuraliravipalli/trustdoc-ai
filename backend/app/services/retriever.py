import re
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import Chunk
from app.services.openai_client import OpenAIService
from app.services.vector_store import VectorStore

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "to", "of", "in", "for", "on", "with", "what", "how",
    "does", "do", "are", "be", "can", "from", "that", "this", "it", "as", "by", "at", "if", "should",
    "must", "policy", "requirement", "requirements", "employees", "employee", "document", "documents",
}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if t not in STOPWORDS and len(t) > 1]


class HybridRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.openai = OpenAIService()
        self.vector_store = VectorStore()

    def keyword_search(
        self,
        question: str,
        limit: int = 20,
        document_type: str | None = None,
        document_id: str | None = None,
    ) -> list[dict]:
        terms = tokenize(question)
        if not terms:
            return []

        query = self.db.query(Chunk)
        if document_type:
            query = query.filter(func.lower(Chunk.document_type) == document_type.lower())
        if document_id:
            query = query.filter(Chunk.document_id == document_id)

        scored = []
        for chunk in query.all():
            text_lower = chunk.text.lower()
            raw_score = sum(text_lower.count(term) for term in terms)
            if raw_score > 0:
                normalized = raw_score / max(1, len(chunk.text.split()))
                scored.append({
                    "chunk_id": chunk.id,
                    "score": float(normalized),
                    "source": "keyword",
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        for rank, item in enumerate(scored[:limit], start=1):
            item["rank"] = rank
        return scored[:limit]

    def reciprocal_rank_fusion(self, dense_hits: list[dict], keyword_hits: list[dict], k: int = 60) -> list[dict]:
        combined: dict[str, dict] = {}
        for hit in dense_hits + keyword_hits:
            chunk_id = hit.get("chunk_id")
            if not chunk_id:
                continue
            if chunk_id not in combined:
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "rrf_score": 0.0,
                    "dense_score": 0.0,
                    "keyword_score": 0.0,
                    "sources": set(),
                }
            combined[chunk_id]["rrf_score"] += 1.0 / (k + int(hit.get("rank", 999)))
            if hit.get("source") == "dense":
                combined[chunk_id]["dense_score"] = max(combined[chunk_id]["dense_score"], float(hit.get("score", 0)))
            if hit.get("source") == "keyword":
                combined[chunk_id]["keyword_score"] = max(combined[chunk_id]["keyword_score"], float(hit.get("score", 0)))
            combined[chunk_id]["sources"].add(hit.get("source", "unknown"))

        results = list(combined.values())
        for item in results:
            item["sources"] = sorted(item["sources"])
        results.sort(key=lambda x: (x["keyword_score"] > 0, x["rrf_score"], x["dense_score"]), reverse=True)
        return results

    def retrieve(
        self,
        question: str,
        top_k: int,
        document_type: str | None = None,
        document_id: str | None = None,
    ) -> tuple[list[dict], dict]:
        query_vector = self.openai.embed_texts([question])[0]
        search_limit = max(top_k * 4, 12)
        dense_hits = self.vector_store.search(
            query_vector=query_vector,
            limit=search_limit,
            document_type=document_type,
            document_id=document_id,
        )
        keyword_hits = self.keyword_search(
            question=question,
            limit=search_limit,
            document_type=document_type,
            document_id=document_id,
        )
        fused = self.reciprocal_rank_fusion(dense_hits, keyword_hits)
        top = fused[:top_k]

        chunk_ids = [item["chunk_id"] for item in top]
        chunks = {c.id: c for c in self.db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()} if chunk_ids else {}

        hydrated = []
        for rank, item in enumerate(top, start=1):
            chunk = chunks.get(item["chunk_id"])
            if not chunk:
                continue
            hydrated.append({
                "rank": rank,
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "file": chunk.filename,
                "document_type": chunk.document_type,
                "page": chunk.page,
                "text": chunk.text,
                "score": float(item["rrf_score"]),
                "dense_score": float(item["dense_score"]),
                "keyword_score": float(item["keyword_score"]),
                "sources": item["sources"],
            })

        debug = {
            "dense_hits": len(dense_hits),
            "keyword_hits": len(keyword_hits),
            "fused_hits": len(fused),
            "returned": len(hydrated),
            "top_dense_score": max([h.get("score", 0) for h in dense_hits], default=0),
            "top_keyword_score": max([h.get("score", 0) for h in keyword_hits], default=0),
            "filter_document_type": document_type or None,
        }
        return hydrated, debug

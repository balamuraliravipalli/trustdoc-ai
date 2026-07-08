from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from app.core.config import get_settings


class VectorStore:
    def __init__(self):
        self.settings = get_settings()
        self.client = QdrantClient(url=self.settings.qdrant_url)
        self.collection = self.settings.qdrant_collection

    def ensure_collection(self) -> None:
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qm.VectorParams(
                    size=self.settings.embedding_dimension,
                    distance=qm.Distance.COSINE,
                ),
            )

    def upsert_chunks(self, points: list[dict]) -> None:
        self.ensure_collection()
        qdrant_points = [
            qm.PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"],
            )
            for p in points
        ]
        if qdrant_points:
            self.client.upsert(collection_name=self.collection, points=qdrant_points, wait=True)

    def delete_document(self, document_id: str) -> None:
        self.ensure_collection()
        self.client.delete(
            collection_name=self.collection,
            points_selector=qm.FilterSelector(
                filter=qm.Filter(
                    must=[qm.FieldCondition(key="document_id", match=qm.MatchValue(value=document_id))]
                )
            ),
            wait=True,
        )

    def search(
        self,
        query_vector: list[float],
        limit: int,
        document_type: str | None = None,
        document_id: str | None = None,
    ) -> list[dict]:
        self.ensure_collection()
        must = []
        if document_type:
            must.append(qm.FieldCondition(key="document_type_normalized", match=qm.MatchValue(value=document_type.lower())))
        if document_id:
            must.append(qm.FieldCondition(key="document_id", match=qm.MatchValue(value=document_id)))
        query_filter = qm.Filter(must=must) if must else None

        try:
            result = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            )
            points = result.points
        except Exception:
            points = self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            )

        hits = []
        for rank, p in enumerate(points, start=1):
            payload = p.payload or {}
            hits.append({
                "chunk_id": payload.get("chunk_id"),
                "score": float(getattr(p, "score", 0.0)),
                "rank": rank,
                "source": "dense",
                "payload": payload,
            })
        return hits

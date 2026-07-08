# Architecture

TrustDoc AI uses a modular RAG pipeline:

1. PDF upload through FastAPI
2. Page extraction using PyMuPDF
3. Chunking with metadata: file name, page, document type, chunk index
4. Embedding generation through OpenAI
5. Vector indexing in Qdrant
6. Hybrid retrieval combining dense vector search and keyword scoring
7. Evidence-grounded answer generation
8. Citation pruning to display only used citations
9. Logging for analytics and evaluation

Important design decisions:

- Keep vector payloads tied to SQL metadata by chunk ID.
- Use document-type filters as metadata filters, not text search filters.
- Treat retrieved text as untrusted evidence, not instructions.
- Refuse unsupported answers instead of guessing.
- Record evaluation metrics for reliability, not only demo outputs.

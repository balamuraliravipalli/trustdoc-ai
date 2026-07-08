from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)
    document_type: Mapped[str] = mapped_column(String(100), default="general", index=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)
    document_type: Mapped[str] = mapped_column(String(100), default="general", index=True)
    page: Mapped[int] = mapped_column(Integer, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped[Document] = relationship(back_populates="chunks")


class QuestionLog(Base):
    __tablename__ = "question_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(20))
    latency_ms: Mapped[int] = mapped_column(Integer)
    retrieval_debug_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    question: Mapped[str] = mapped_column(Text)
    expected_file_contains: Mapped[str] = mapped_column(String(255), default="")
    expected_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_answer_contains: Mapped[str] = mapped_column(Text, default="")
    answer: Mapped[str] = mapped_column(Text)
    citation_hit: Mapped[int] = mapped_column(Integer, default=0)
    answer_contains_hit: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[str] = mapped_column(String(20))
    latency_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

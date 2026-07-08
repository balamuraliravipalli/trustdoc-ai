import json
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.security import require_api_key, get_current_user, CurrentUser
from app.db.models import Chunk, Document, QuestionLog
from app.db.session import get_db
from app.schemas import AnalyticsSummary

router = APIRouter(prefix="/api/analytics", tags=["analytics"], dependencies=[Depends(require_api_key)])


@router.get("/summary", response_model=AnalyticsSummary)
def summary(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_chunks = db.query(func.count(Chunk.id)).scalar() or 0
    total_questions = db.query(func.count(QuestionLog.id)).scalar() or 0
    avg_latency = int(db.query(func.avg(QuestionLog.latency_ms)).scalar() or 0)

    confidence_counts = {"high": 0, "medium": 0, "low": 0}
    rows = db.query(QuestionLog.confidence, func.count(QuestionLog.id)).group_by(QuestionLog.confidence).all()
    for confidence, count in rows:
        confidence_counts[confidence] = count

    latest = db.query(QuestionLog).order_by(QuestionLog.created_at.desc()).limit(8).all()
    latest_questions = []
    for q in latest:
        try:
            citations = json.loads(q.citations_json)
        except Exception:
            citations = []
        latest_questions.append({
            "question": q.question,
            "confidence": q.confidence,
            "latency_ms": q.latency_ms,
            "citation_count": len(citations),
            "created_at": q.created_at.isoformat(),
        })

    return AnalyticsSummary(
        documents=total_documents,
        chunks=total_chunks,
        questions=total_questions,
        avg_latency_ms=avg_latency,
        confidence_counts=confidence_counts,
        latest_questions=latest_questions,
    )

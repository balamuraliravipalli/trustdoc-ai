from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import require_api_key
from app.db.session import get_db
from app.schemas import AskRequest, AskResponse
from app.services.rag import RAGService

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(require_api_key)])


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    return RAGService(db).answer_question(request)

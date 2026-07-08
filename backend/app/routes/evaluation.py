from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import require_api_key
from app.db.session import get_db
from app.schemas import EvaluationRunRequest, EvaluationRunResponse
from app.services.evaluation import EvaluationService

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"], dependencies=[Depends(require_api_key)])


@router.post("/run", response_model=EvaluationRunResponse)
def run_evaluation(request: EvaluationRunRequest, db: Session = Depends(get_db)):
    return EvaluationService(db).run(request)

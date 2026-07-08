import uuid
from sqlalchemy.orm import Session
from app.db.models import EvaluationResult
from app.schemas import EvaluationRunRequest, EvaluationRunResponse, EvaluationCaseResult, AskRequest
from app.services.rag import RAGService, REFUSAL


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.rag = RAGService(db)

    def run(self, request: EvaluationRunRequest) -> EvaluationRunResponse:
        run_id = str(uuid.uuid4())
        results: list[EvaluationCaseResult] = []

        for case in request.cases:
            response = self.rag.answer_question(AskRequest(question=case.question))
            answer_lower = response.answer.lower()

            citation_hit = True
            if case.expected_file_contains:
                citation_hit = any(
                    case.expected_file_contains.lower() in citation.file.lower()
                    for citation in response.citations
                )
            if citation_hit and case.expected_page is not None:
                citation_hit = any(citation.page == case.expected_page for citation in response.citations)

            answer_contains_hit = True
            if case.expected_answer_contains:
                answer_contains_hit = case.expected_answer_contains.lower() in answer_lower

            refusal_hit = None
            if case.should_refuse:
                refusal_hit = REFUSAL.lower() in answer_lower and not response.citations

            db_result = EvaluationResult(
                id=str(uuid.uuid4()),
                run_id=run_id,
                question=case.question,
                expected_file_contains=case.expected_file_contains,
                expected_page=case.expected_page,
                expected_answer_contains=case.expected_answer_contains,
                answer=response.answer,
                citation_hit=1 if citation_hit else 0,
                answer_contains_hit=1 if answer_contains_hit else 0,
                confidence=response.confidence,
                latency_ms=response.latency_ms,
            )
            self.db.add(db_result)

            results.append(EvaluationCaseResult(
                question=case.question,
                answer=response.answer,
                citation_hit=citation_hit,
                answer_contains_hit=answer_contains_hit,
                refusal_hit=refusal_hit,
                confidence=response.confidence,
                latency_ms=response.latency_ms,
            ))

        self.db.commit()
        total = len(results) or 1
        citation_accuracy = sum(1 for r in results if r.citation_hit) / total
        answer_accuracy = sum(1 for r in results if r.answer_contains_hit) / total
        refusal_results = [r for r in results if r.refusal_hit is not None]
        refusal_accuracy = None
        if refusal_results:
            refusal_accuracy = sum(1 for r in refusal_results if r.refusal_hit) / len(refusal_results)
        avg_latency = int(sum(r.latency_ms for r in results) / total)

        return EvaluationRunResponse(
            run_id=run_id,
            total_cases=len(results),
            citation_accuracy=round(citation_accuracy, 3),
            answer_contains_accuracy=round(answer_accuracy, 3),
            refusal_accuracy=round(refusal_accuracy, 3) if refusal_accuracy is not None else None,
            average_latency_ms=avg_latency,
            results=results,
        )

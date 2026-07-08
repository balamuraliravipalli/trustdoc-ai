from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
    auth_enabled: bool


class DocumentOut(BaseModel):
    id: str
    filename: str
    document_type: str
    page_count: int
    chunk_count: int
    created_at: str


class ChunkOut(BaseModel):
    id: str
    page: int
    chunk_index: int
    token_estimate: int
    text_preview: str


class Citation(BaseModel):
    index: int
    chunk_id: str
    document_id: str
    file: str
    page: int
    score: float
    text_preview: str


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    document_type: str | None = None
    document_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=12)


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: str
    latency_ms: int
    retrieval_debug: dict


class EvaluationCase(BaseModel):
    question: str
    expected_file_contains: str = ""
    expected_page: int | None = None
    expected_answer_contains: str = ""
    should_refuse: bool = False


class EvaluationRunRequest(BaseModel):
    cases: list[EvaluationCase]


class EvaluationCaseResult(BaseModel):
    question: str
    answer: str
    citation_hit: bool
    answer_contains_hit: bool
    refusal_hit: bool | None = None
    confidence: str
    latency_ms: int


class EvaluationRunResponse(BaseModel):
    run_id: str
    total_cases: int
    citation_accuracy: float
    answer_contains_accuracy: float
    refusal_accuracy: float | None
    average_latency_ms: int
    results: list[EvaluationCaseResult]


class AnalyticsSummary(BaseModel):
    documents: int
    chunks: int
    questions: int
    avg_latency_ms: int
    confidence_counts: dict
    latest_questions: list[dict]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import init_db
from app.routes import analytics, auth, chat, documents, evaluation, health

settings = get_settings()

app = FastAPI(
    title="TrustDoc AI",
    description="Evidence-grounded advanced RAG assistant with citations and evaluation.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(evaluation.router)

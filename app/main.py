from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.api.ingest import router as ingest_router
from app.api.query import router as query_router
from app.api.document import router as document_router

@asynccontextmanager
async def lifespan(app :FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="Documment Intelligence API",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(document_router)
@app.get("/health")
async def health():
    return {"status":"ok"}
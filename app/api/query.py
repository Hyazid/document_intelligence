from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_session
from app.services.retriever import retrieve
from app.services.generator import generate_stream
from app.services.tracer import get_langfuse
from app.schemas.document import QueryRequest

router = APIRouter()

@router.post("/query")
async def query(body: QueryRequest, db: AsyncSession = Depends(get_session)):
    

    # Create top-level trace for this query
    

    chunks = await retrieve(body.question, db, top_k=body.top_k)

    if not chunks:
        
        return {"answer": "No relevant context found.", "chunks_used": []}

    
    context = "\n\n".join(c["content"] for c in chunks)

    prompt = f"""Use the context below to answer the question.
If the answer isn't in the context, say "I don't know."

Context:
{context}

Question: {body.question}
Answer:"""

    async def stream():
        async for token in generate_stream(prompt):
            yield f"data: {token}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/retrieve")
async def retrieve_chunks(body: QueryRequest, db: AsyncSession = Depends(get_session)):
    chunks = await retrieve(body.question, db, top_k=body.top_k)
    return {"chunks": chunks}
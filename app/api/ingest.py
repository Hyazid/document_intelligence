import traceback

from fastapi import APIRouter , UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import Depends
import uuid
import pymupdf


from app.database import get_session
from app.services.chunker import chunk_text
from app.services.embedder import embed
from app.schemas.document import  IngestResponse
router =APIRouter()
@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...), db: AsyncSession = Depends(get_session)):
    try:
        raw = await file.read()

        if file.content_type == "application/pdf":
            doc = pymupdf.open(stream=raw, filetype="pdf")
            content = "\n".join(page.get_text() for page in doc)
        else:
            content = raw.decode("utf-8")

        chunks = chunk_text(content)
        embeddings = await embed(chunks)

        doc_id = uuid.uuid4()

        await db.execute(
            text("INSERT INTO documents (id, filename) VALUES (:id, :fn)"),
            {"id": str(doc_id), "fn": file.filename}
        )

        rows = [
            {"doc_id": str(doc_id), "content": chunk, "emb": str(emb), "idx": i}
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]

        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            await db.execute(
                text("""
                    INSERT INTO chunks (document_id, content, embedding, chunk_index)
                    VALUES (:doc_id, :content, CAST(:emb AS vector), :idx)
                """),
                {
                    "doc_id": str(doc_id),
                    "content": chunk,
                    "emb": str(emb),   # "[0.1, 0.2, ...]" string
                    "idx": i
                }
            )

        await db.commit()

        return IngestResponse(
            document_id=doc_id,
            filename=file.filename,
            chunks=len(chunks),
        )

    except Exception as e:
        await db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
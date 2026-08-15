from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_session
from app.schemas.document import DocumentInfo
router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", response_model=list[DocumentInfo])
async def list_documents(db:AsyncSession=Depends(get_session)):
    result = await db.execute(
        text("""SELECT d.id, d.filename, d.created_at,COUNT(c.id) AS chunck_count FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id, d.filename, d.created_at
            ORDER BY d.created_at DESC """)
    )
    rows = result.fetchall()
    return [DocumentInfo(id=row.id, filename=row.filename, created_at=row.created_at, chunk_count=row.chunck_count) for row in rows]

@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id:str, db:AsyncSession=Depends(get_session)):
    result = await db.execute(
        text("SELECT id FROM documents WHERE id = :id"),{"id": document_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Document not found")
    await db.execute(
        text("DELETE FROM documents WHERE id=:id"),{"id": document_id}
    )
    await db.commit()
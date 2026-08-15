from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

###ingest
class IngestResponse(BaseModel):
    """Returned after a successful document upload and processing."""
    document_id: UUID
    filename: str
    chunks: int
    message: str = "Document ingested successfully"
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask the model.")
    top_k: int = Field(default=5, ge=1, le=20, description="The number of top relevant chunks to retrieve.")

class ChunkResult(BaseModel):
    content:str
    score:float
class QueryResponse(BaseModel):
    question: str
    answer: str
    chunks_used:list[ChunkResult]

#document information
class DocumentInfo(BaseModel):
    id:UUID
    filename:str
    created_at:datetime
    chunks_count:int
    
    model_config = {"from_attributes": True}

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer,ForeignKey, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass
class Document(Base):
    __tablename__ ="documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename= Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, created_at={self.created_at})>"
class Chunk(Base):
    __tablename__="chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    #relationship back to  parent document
    document = relationship("Document", back_populates="chunks")
    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index}, created_at={self.created_at})>"
    
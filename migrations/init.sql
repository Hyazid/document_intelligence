CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- provides uuid_generate_v4()

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),   -- DEFAULT was missing
    filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(768),
    chunk_index INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast vector search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks USING hnsw (embedding vector_cosine_ops);

-- Full-text search index
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING gin(tsv);
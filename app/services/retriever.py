from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.embedder import embed

async def retrieve(query: str, db: AsyncSession, top_k: int = 5) -> list[dict]:
    q_emb = (await embed([query]))[0]
    emb_str = str(q_emb)

    # Vector search — use $1 style to avoid named param conflicts with pgvector
    vec_result = await db.execute(
        text("""
            SELECT content, 1 - (embedding <=> CAST(:emb AS vector)) AS score
            FROM chunks
            ORDER BY embedding <=> CAST(:emb AS vector)
            LIMIT :k
        """),
        {"emb": emb_str, "k": top_k}
    )
    vec_rows = vec_result.fetchall()

    # Keyword search
    kw_result = await db.execute(
        text("""
            SELECT content, ts_rank(tsv, plainto_tsquery('english', :q)) AS score
            FROM chunks
            WHERE tsv @@ plainto_tsquery('english', :q)
            ORDER BY score DESC
            LIMIT :k
        """),
        {"q": query, "k": top_k}
    )
    kw_rows = kw_result.fetchall()

    # Reciprocal Rank Fusion
    rrf_scores: dict[str, float] = {}

    for rank, row in enumerate(vec_rows):
        rrf_scores[row.content] = rrf_scores.get(row.content, 0) + 1 / (rank + 60)

    for rank, row in enumerate(kw_rows):
        rrf_scores[row.content] = rrf_scores.get(row.content, 0) + 1 / (rank + 60)

    merged = [
        {"content": content, "score": score}
        for content, score in rrf_scores.items()
    ]

    return sorted(merged, key=lambda x: x["score"], reverse=True)[:top_k]
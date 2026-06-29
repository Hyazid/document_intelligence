#embedding model is a system that translate humans language to numerical vectores or list
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(base_url=settings.lm_studio_url, api_key=settings.lm_studio_api_key)
async def embed(text:list[str])-> list[list[float]]:
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    return [item.embedding for item in response.data]
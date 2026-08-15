from openai import AsyncOpenAI
from app.config import settings
from app.services.tracer import get_langfuse
import json, time
client = AsyncOpenAI(base_url=settings.lm_studio_url, api_key=settings.lm_studio_api_key)

async def generate_stream(prompt:str):
    
    
    stream  = await client.chat.completions.create(
        model = settings.llm_model,
        messages = [
            {"role":"system", "content": "You are a helpful assistant. . Answer only based on the provided context."},
            {"role":"user", "content": prompt}
        ],
        temperature = settings.llm_temperature,
        max_tokens = settings.llm_max_tokens,
        stream = True
    )
    
    async for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        # delta.content can be None on first/last chunk
        if delta and delta.content is not None:
            
            yield delta.content
    

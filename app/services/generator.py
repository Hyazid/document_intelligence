from openai import AsyncOpenAI
from app.config import settings
import json
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
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
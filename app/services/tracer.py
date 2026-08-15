from app.config import settings

class NoOpLangfuse:
    """Dummy tracer used when Langfuse is not configured."""
    def trace(self, **kwargs): return NoOpSpan()
    def generation(self, **kwargs): return NoOpSpan()
    def flush(self): pass

class NoOpSpan:
    def span(self, **kwargs): return NoOpSpan()
    def update(self, **kwargs): pass
    def end(self, **kwargs): pass

def get_langfuse():
    if not settings.langfuse_public_key:
        return NoOpLangfuse()

    from langfuse import Langfuse
    return Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )

# Single instance
langfuse = get_langfuse()
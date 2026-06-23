from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import ApplicationError

class EmbeddingService:
    def __init__(self):
        if not settings.openai_api_key:
            raise ApplicationError("OPENAI_API_KEY - x", status_code=500)
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_modeL
        self.dimensions = settings.embedding_dimensions
    
    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text][0])

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            dimensions=self.dimensions,
        )

        return [item.embedding for item in response.data]


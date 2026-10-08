from typing import Any

from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStore


class RAGService:
    """Retrieve relevant document context for user queries."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve_context(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve the most relevant document chunks for a query."""

        query_embedding = self.embedding_service.generate_embedding(
            query
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            limit=limit,
        )

        context: list[dict[str, Any]] = []

        for result in results:
            if result.payload is None:
                continue

            context.append(
                {
                    "text": result.payload.get("text", ""),
                    "filename": result.payload.get("filename", ""),
                    "score": result.score,
                }
            )

        return context
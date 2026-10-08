from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class VectorStore:
    """Store and search document embeddings using Qdrant."""

    def __init__(self) -> None:
        self.client = QdrantClient(
            url="http://localhost:6333"
        )
        self.collection_name = "documents"

    def create_collection(self) -> None:
        """Create the Qdrant collection if it does not exist."""

        collections = self.client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if self.collection_name not in existing_collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    def add_documents(
        self,
        embeddings: list[list[float]],
        chunks: list[str],
        filename: str,
    ) -> None:
        """Store document chunks and their embeddings in Qdrant."""

        points: list[PointStruct] = []

        for embedding, chunk in zip(embeddings, chunks):
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "filename": filename,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[Any]:
        """Search for the most relevant document chunks."""

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
        )

        return results.points
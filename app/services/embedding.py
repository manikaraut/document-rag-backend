from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Create embeddings for text using a Sentence Transformer model."""

    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""

        embedding = self.model.encode(text)

        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple text chunks."""

        embeddings = self.model.encode(texts)

        return embeddings.tolist()
    # Test the embedding service

if __name__ == "__main__":
    service = EmbeddingService()

    text = "Python is a programming language used for data analysis."

    embedding = service.generate_embedding(text)

    print("Embedding created successfully.")
    print("Number of dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])
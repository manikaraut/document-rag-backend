from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStore


embedding_service = EmbeddingService()
vector_store = VectorStore()

vector_store.create_collection()

text_chunks = [
    "Python is a programming language.",
    "FastAPI is a modern web framework for building APIs.",
    "Machine learning uses data to make predictions.",
]

embeddings = embedding_service.generate_embeddings(text_chunks)

vector_store.add_documents(
    embeddings=embeddings,
    chunks=text_chunks,
    filename="test.txt",
)

query = "What is FastAPI?"

query_embedding = embedding_service.generate_embedding(query)

results = vector_store.search(
    query_embedding=query_embedding,
    limit=2,
)

for result in results:
    print("Score:", result.score)
    print("Text:", result.payload["text"])
    print()
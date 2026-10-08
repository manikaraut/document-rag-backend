from app.services.embedding import EmbeddingService
from app.services.rag import RAGService
from app.services.vector_store import VectorStore


embedding_service = EmbeddingService()
vector_store = VectorStore()

vector_store.create_collection()

text_chunks = [
    "Python is a programming language used for software development.",
    "FastAPI is a modern Python framework for building REST APIs.",
    "Machine learning allows computers to learn patterns from data.",
]

embeddings = embedding_service.generate_embeddings(text_chunks)

vector_store.add_documents(
    embeddings=embeddings,
    chunks=text_chunks,
    filename="test.txt",
)

rag_service = RAGService(
    embedding_service=embedding_service,
    vector_store=vector_store,
)

query = "What framework can I use to build a REST API?"

results = rag_service.retrieve_context(
    query=query,
    limit=2,
)

for result in results:
    print("Score:", result["score"])
    print("Filename:", result["filename"])
    print("Text:", result["text"])
    print()
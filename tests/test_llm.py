from app.services.llm import LLMService


llm = LLMService()

response = llm.generate(
    "What is FastAPI? Give a short definition."
)

print(response)
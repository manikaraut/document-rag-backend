from typing import Any

from fastapi import APIRouter

from app.database.connection import SessionLocal
from app.database.models import InterviewBooking
from app.services.booking import BookingService
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService
from app.services.rag import RAGService
from app.services.redis_memory import RedisMemory
from app.services.vector_store import VectorStore


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


embedding_service = EmbeddingService()

vector_store = VectorStore()
vector_store.create_collection()

rag_service = RAGService(
    embedding_service=embedding_service,
    vector_store=vector_store,
)

redis_memory = RedisMemory()

llm_service = LLMService()

booking_service = BookingService(
    llm_service=llm_service,
    redis_memory=redis_memory,
)


@router.post("")
async def chat(
    session_id: str,
    message: str,
) -> dict[str, Any]:

    history = redis_memory.get_messages(session_id)

    booking_active = redis_memory.is_booking_active(session_id)

    booking_state = redis_memory.get_booking_state(session_id)

    booking_info = booking_service.extract_booking_info(message)

    # ------------------------------------------------
    # START BOOKING
    # ------------------------------------------------

    if booking_info.get("is_booking_request") and not booking_active:

        booking_active = True

        redis_memory.set_booking_active(session_id)

        booking_state = {}

        redis_memory.save_booking_state(
            session_id,
            booking_state,
        )

        redis_memory.set_booking_field(
            session_id,
            "name",
        )

        response = "What is your full name?"

        redis_memory.save_message(
            session_id,
            "user",
            message,
        )

        redis_memory.save_message(
            session_id,
            "assistant",
            response,
        )

        return {
            "session_id": session_id,
            "message": message,
            "response": response,
            "booking_status": "collecting_information",
            "booking": {},
        }

    # ------------------------------------------------
    # CONTINUE BOOKING
    # ------------------------------------------------

    if booking_active:

        current_field = redis_memory.get_booking_field(
            session_id
        )

        # Store answer in the correct field
        if current_field == "name":

            booking_state["name"] = message.strip()

            next_field = "email"

        elif current_field == "email":

            email = booking_info.get("email")

            if email:
                booking_state["email"] = str(email)
            else:
                booking_state["email"] = message.strip()

            next_field = "date"

        elif current_field == "date":

            booking_state["date"] = message.strip()

            next_field = "time"

        elif current_field == "time":

            booking_state["time"] = message.strip()

            next_field = ""

        else:
            next_field = "name"

        redis_memory.save_booking_state(
            session_id,
            booking_state,
        )

        # ------------------------------------------------
        # Ask next question
        # ------------------------------------------------

        if next_field:

            redis_memory.set_booking_field(
                session_id,
                next_field,
            )

            questions = {
                "name": "What is your full name?",
                "email": "What is your email address?",
                "date": "What date would you like to schedule the interview?",
                "time": "What time would you like to schedule the interview?",
            }

            response = questions[next_field]

            redis_memory.save_message(
                session_id,
                "user",
                message,
            )

            redis_memory.save_message(
                session_id,
                "assistant",
                response,
            )

            return {
                "session_id": session_id,
                "message": message,
                "response": response,
                "booking_status": "collecting_information",
                "booking": booking_state,
            }

        # ------------------------------------------------
        # Validate email
        # ------------------------------------------------

        if not booking_service.validate_email(
            booking_state["email"]
        ):

            response = "Please provide a valid email address."

            redis_memory.set_booking_field(
                session_id,
                "email",
            )

            return {
                "session_id": session_id,
                "message": message,
                "response": response,
                "booking_status": "invalid_email",
                "booking": booking_state,
            }

        # ------------------------------------------------
        # Save booking
        # ------------------------------------------------

        db = SessionLocal()

        try:
            booking = InterviewBooking(
                name=booking_state["name"],
                email=booking_state["email"],
                date=booking_state["date"],
                time=booking_state["time"],
            )

            db.add(booking)
            db.commit()
            db.refresh(booking)

        finally:
            db.close()

        # Clear Redis booking state
        redis_memory.clear_booking_state(session_id)
        redis_memory.clear_booking_active(session_id)
        redis_memory.clear_booking_field(session_id)

        response = (
            "Your interview has been booked successfully. "
            f"Name: {booking.name}, "
            f"Email: {booking.email}, "
            f"Date: {booking.date}, "
            f"Time: {booking.time}."
        )

        redis_memory.save_message(
            session_id,
            "user",
            message,
        )

        redis_memory.save_message(
            session_id,
            "assistant",
            response,
        )

        return {
            "session_id": session_id,
            "message": message,
            "response": response,
            "booking_status": "confirmed",
            "booking": {
                "id": booking.id,
                "name": booking.name,
                "email": booking.email,
                "date": booking.date,
                "time": booking.time,
            },
        }

    # ------------------------------------------------
    # NORMAL RAG
    # ------------------------------------------------

    context = rag_service.retrieve_context(
        query=message,
        limit=5,
    )

    history_text = "\n".join(
        f'{item["role"]}: {item["content"]}'
        for item in history
    )

    context_text = "\n\n".join(
        item["text"]
        for item in context
    )

    prompt = f"""
You are a helpful assistant answering questions
using the provided document context.

Conversation history:
{history_text}

Document context:
{context_text}

Current question:
{message}

Instructions:
- Answer using the document context when relevant.
- Use the conversation history to understand follow-up questions.
- Do not invent information.
- If the answer cannot be found in the documents,
  say that the information is not available.
- Give a clear and concise answer.
"""

    assistant_response = llm_service.generate(prompt)

    redis_memory.save_message(
        session_id,
        "user",
        message,
    )

    redis_memory.save_message(
        session_id,
        "assistant",
        assistant_response,
    )

    return {
        "session_id": session_id,
        "message": message,
        "history": history,
        "retrieved_context": context,
        "response": assistant_response,
    }
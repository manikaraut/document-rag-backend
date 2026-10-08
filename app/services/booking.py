import json
import re
from typing import Any

from app.database.connection import SessionLocal
from app.database.models import InterviewBooking
from app.services.llm import LLMService
from app.services.redis_memory import RedisMemory


class BookingService:
    """Handle interview booking using the LLM and Redis."""

    def __init__(
        self,
        llm_service: LLMService,
        redis_memory: RedisMemory,
    ) -> None:
        self.llm_service = llm_service
        self.redis_memory = redis_memory

    def extract_booking_info(
        self,
        message: str,
    ) -> dict[str, Any]:
        """Extract booking information from a user message."""

        prompt = f"""
Extract interview booking information from the user's message.

Return ONLY valid JSON with these fields:

{{
    "is_booking_request": true or false,
    "name": null,
    "email": null,
    "date": null,
    "time": null
}}

Rules:
- Set is_booking_request to true if the user wants to book or schedule an interview.
- Extract only information that is clearly provided.
- If information is missing, use null.
- Do not invent information.
- Return JSON only.

User message:
{message}
"""

        response = self.llm_service.generate(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "is_booking_request": False,
                "name": None,
                "email": None,
                "date": None,
                "time": None,
            }

    def validate_email(self, email: str) -> bool:
        """Validate an email address."""

        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        return bool(re.match(pattern, email))

    def save_booking(
        self,
        state: dict[str, str],
    ) -> InterviewBooking:
        """Save a completed interview booking to the database."""

        db = SessionLocal()

        try:
            booking = InterviewBooking(
                name=state["name"],
                email=state["email"],
                date=state["date"],
                time=state["time"],
            )

            db.add(booking)
            db.commit()
            db.refresh(booking)

            return booking

        finally:
            db.close()
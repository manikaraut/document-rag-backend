import json

import redis


class RedisMemory:
    """Manage conversational memory using Redis."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
    ) -> None:
        self.client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        message = {
            "role": role,
            "content": content,
        }

        self.client.rpush(
            f"chat:{session_id}",
            json.dumps(message),
        )

    def get_messages(
        self,
        session_id: str,
    ) -> list[dict[str, str]]:
        messages = self.client.lrange(
            f"chat:{session_id}",
            0,
            -1,
        )

        return [
            json.loads(message)
            for message in messages
        ]

    def clear_messages(
        self,
        session_id: str,
    ) -> None:
        self.client.delete(
            f"chat:{session_id}"
        )

    def save_booking_state(
        self,
        session_id: str,
        state: dict[str, str],
    ) -> None:
        self.client.set(
            f"booking:{session_id}",
            json.dumps(state),
        )

    def get_booking_state(
        self,
        session_id: str,
    ) -> dict[str, str]:
        data = self.client.get(
            f"booking:{session_id}"
        )

        if not data:
            return {}

        return json.loads(data)

    def clear_booking_state(
        self,
        session_id: str,
    ) -> None:
        self.client.delete(
            f"booking:{session_id}"
        )

    def set_booking_active(
        self,
        session_id: str,
    ) -> None:
        self.client.set(
            f"booking_active:{session_id}",
            "true",
        )

    def is_booking_active(
        self,
        session_id: str,
    ) -> bool:
        return bool(
            self.client.get(
                f"booking_active:{session_id}"
            )
        )

    def clear_booking_active(
        self,
        session_id: str,
    ) -> None:
        self.client.delete(
            f"booking_active:{session_id}"
        )

    def set_booking_field(
        self,
        session_id: str,
        field: str,
    ) -> None:
        self.client.set(
            f"booking_field:{session_id}",
            field,
        )

    def get_booking_field(
        self,
        session_id: str,
    ) -> str:
        field = self.client.get(
            f"booking_field:{session_id}"
        )

        return field or ""

    def clear_booking_field(
        self,
        session_id: str,
    ) -> None:
        self.client.delete(
            f"booking_field:{session_id}"
        )
from app.database.connection import Base, engine
from app.database.models import Document, InterviewBooking


def init_database() -> None:
    """Create all database tables."""

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
    print("Database tables created successfully.")
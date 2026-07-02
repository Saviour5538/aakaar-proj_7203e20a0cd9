import uuid
from datetime import datetime
from database.models import Base, engine, SessionLocal, User, Document, Chunk, Conversation, Message

def seed_database():
    session = SessionLocal()
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        user1 = User(
            id=str(uuid.uuid4()),
            email="alice@example.com",
            password_hash="hashed_password_1",
            role="admin",
            created_at=datetime(2023, 10, 1, 12, 0, 0)
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="bob@example.com",
            password_hash="hashed_password_2",
            role="user",
            created_at=datetime(2023, 10, 2, 12, 0, 0)
        )

        session.add_all([user1, user2])
        session.commit()
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Error seeding database: {e}")
    finally:
        session.close()
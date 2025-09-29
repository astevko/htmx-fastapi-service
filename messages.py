"""
Message storage and retrieval using PostgreSQL with SQLAlchemy
"""

import logging
from datetime import datetime, timezone
from typing import List

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Message, MessageDB

logger = logging.getLogger(__name__)


def store_message(text: str, timestamp: datetime = None) -> None:
    """Store a message in PostgreSQL"""
    db = SessionLocal()
    try:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        message = MessageDB(text=text, timestamp=timestamp)
        db.add(message)
        db.commit()
        logger.debug(f"Stored message: {text[:50]}...")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store message: {e}")
        raise
    finally:
        db.close()


def get_all_messages(descending: bool = True) -> List[Message]:
    """Retrieve all messages from PostgreSQL as Message objects"""
    db = SessionLocal()
    try:
        order_func = desc if descending else asc

        db_messages = db.query(MessageDB).order_by(order_func(MessageDB.timestamp)).all()

        # Convert SQLAlchemy objects to Pydantic Message objects
        messages = [Message(text=msg.text, timestamp=msg.timestamp) for msg in db_messages]

        logger.debug(f"Retrieved {len(messages)} messages")
        return messages

    except Exception as e:
        logger.error(f"Failed to retrieve messages: {e}")
        raise
    finally:
        db.close()


def get_message_count() -> int:
    """Get total number of messages"""
    db = SessionLocal()
    try:
        count = db.query(MessageDB).count()
        return count
    except Exception as e:
        logger.error(f"Failed to get message count: {e}")
        raise
    finally:
        db.close()


def get_messages_by_date_range(start_date: datetime, end_date: datetime) -> List[Message]:
    """Get messages within a date range"""
    db = SessionLocal()
    try:
        db_messages = (
            db.query(MessageDB)
            .filter(MessageDB.timestamp >= start_date, MessageDB.timestamp <= end_date)
            .order_by(desc(MessageDB.timestamp))
            .all()
        )

        messages = [Message(text=msg.text, timestamp=msg.timestamp) for msg in db_messages]
        return messages

    except Exception as e:
        logger.error(f"Failed to get messages by date range: {e}")
        raise
    finally:
        db.close()


def search_messages(search_term: str) -> List[Message]:
    """Search messages by text content"""
    db = SessionLocal()
    try:
        db_messages = (
            db.query(MessageDB)
            .filter(MessageDB.text.ilike(f"%{search_term}%"))
            .order_by(desc(MessageDB.timestamp))
            .all()
        )

        messages = [Message(text=msg.text, timestamp=msg.timestamp) for msg in db_messages]
        return messages

    except Exception as e:
        logger.error(f"Failed to search messages: {e}")
        raise
    finally:
        db.close()

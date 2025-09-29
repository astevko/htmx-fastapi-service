"""
Comprehensive tests for database functionality with psycopg3
"""

import logging
import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import messages

# Import the modules we want to test
from database import (
    DATABASE_URL,
    Base,
    SessionLocal,
    check_driver,
    engine,
    get_db,
    init_database,
    test_connection,
)
from models import Message, MessageDB

# Set up test environment
os.environ["DATABASE_URL"] = "sqlite:///:memory:"  # Use in-memory SQLite for testing

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestDatabase:
    """Test class for database functionality"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, monkeypatch):
        """Setup and teardown for each test with isolated database"""
        # Create a fresh in-memory SQLite database for each test
        test_engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        # Create session factory
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        # Patch the database module to use our test database
        monkeypatch.setattr("database.engine", test_engine)
        monkeypatch.setattr("database.SessionLocal", TestSessionLocal)

        # Also patch the messages module to use the test database
        monkeypatch.setattr("messages.SessionLocal", TestSessionLocal)

        # Create all tables using the test engine
        Base.metadata.create_all(bind=test_engine)

        yield

        # Cleanup
        test_engine.dispose()

    def test_database_connection(self):
        """Test basic database connection"""
        result = test_connection()
        assert result is True
        logger.info("Database connection test passed")

    def test_database_initialization(self):
        """Test database initialization"""
        # Import the patched engine from database module
        from database import engine  # noqa: F811

        # Tables should already be created by the fixture
        with engine.connect() as conn:
            # Check if messages table exists
            result = conn.execute(
                text(
                    """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='messages'
            """
                )
            ).fetchone()
            assert result is not None
            logger.info("Messages table created successfully")

    def test_driver_detection(self):
        """Test driver detection (will be sqlite for testing)"""
        driver = check_driver()
        assert driver is not None
        logger.info(f"Driver detected: {driver}")

    def test_session_factory(self):
        """Test session factory creation and cleanup"""
        from database import SessionLocal  # noqa: F811

        db = SessionLocal()
        try:
            assert db is not None
            # Test basic query
            result = db.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1
        finally:
            db.close()
        logger.info("Session factory test passed")

    def test_get_db_dependency(self):
        """Test the get_db dependency function"""
        db_gen = get_db()
        db = next(db_gen)
        try:
            assert db is not None
            # Test basic query
            result = db.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1
        finally:
            db.close()
        logger.info("get_db dependency test passed")

    def test_message_model_creation(self):
        """Test MessageDB model creation"""
        from database import SessionLocal  # noqa: F811

        db = SessionLocal()
        try:
            # Create a test message
            test_message = MessageDB(text="Test message", timestamp=datetime.now(timezone.utc))
            db.add(test_message)
            db.commit()

            # Verify it was created
            result = db.query(MessageDB).first()
            assert result is not None
            assert result.text == "Test message"
            assert isinstance(result.timestamp, datetime)

        finally:
            db.close()
        logger.info("MessageDB model creation test passed")

    def test_messages_store_and_retrieve(self):
        """Test storing and retrieving messages"""
        from messages import get_all_messages, store_message  # noqa: F811

        # Store a test message
        test_text = "Test message for store/retrieve"
        test_timestamp = datetime.now(timezone.utc)
        store_message(test_text, test_timestamp)

        # Retrieve messages
        messages_list = get_all_messages()
        assert len(messages_list) == 1

        message = messages_list[0]
        assert message.text == test_text
        assert isinstance(message, Message)  # Should be Pydantic model
        assert isinstance(message.timestamp, datetime)

        logger.info("Messages store/retrieve test passed")

    def test_messages_without_timestamp(self):
        """Test storing message without timestamp"""
        from messages import get_all_messages, store_message  # noqa: F811

        # Store message without timestamp
        store_message("Message without timestamp")

        # Retrieve and verify
        messages_list = get_all_messages()
        assert len(messages_list) == 1

        message = messages_list[0]
        assert message.text == "Message without timestamp"
        assert isinstance(message.timestamp, datetime)

        # Check that timestamp is recent (convert to naive for comparison)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        message_time = message.timestamp.replace(tzinfo=None) if message.timestamp.tzinfo else message.timestamp
        time_diff = abs((now - message_time).total_seconds())
        assert time_diff < 60  # Should be within 1 minute

        logger.info("Messages without timestamp test passed")

    def test_multiple_messages_ordering(self):
        """Test storing multiple messages and ordering"""
        from messages import get_all_messages, store_message

        # Store multiple messages with different timestamps
        base_time = datetime.now(timezone.utc)
        messages_data = [
            ("First message", base_time - timedelta(minutes=2)),
            ("Second message", base_time - timedelta(minutes=1)),
            ("Third message", base_time),
        ]

        for msg_txt, timestamp in messages_data:
            store_message(msg_txt, timestamp)

        # Retrieve messages (should be in descending order by default)
        messages_list = get_all_messages()
        assert len(messages_list) == 3

        # Verify ordering (newest first)
        assert messages_list[0].text == "Third message"
        assert messages_list[1].text == "Second message"
        assert messages_list[2].text == "First message"

        logger.info("Multiple messages ordering test passed")

    def test_messages_ascending_order(self):
        """Test retrieving messages in ascending order"""
        from messages import get_all_messages, store_message

        # Store multiple messages
        base_time = datetime.now(timezone.utc)
        messages_data = [
            ("First", base_time - timedelta(minutes=2)),
            ("Second", base_time - timedelta(minutes=1)),
            ("Third", base_time),
        ]

        for msg_txt, timestamp in messages_data:
            store_message(msg_txt, timestamp)

        # Retrieve in ascending order
        messages_list = get_all_messages(descending=False)
        assert len(messages_list) == 3

        # Verify ordering (oldest first)
        assert messages_list[0].text == "First"
        assert messages_list[1].text == "Second"
        assert messages_list[2].text == "Third"

        logger.info("Messages ascending order test passed")

    def test_message_count(self):
        """Test getting message count"""
        from messages import get_message_count, store_message

        # Initially should be 0
        count = get_message_count()
        assert count == 0

        # Add some messages
        store_message("Message 1")
        store_message("Message 2")
        store_message("Message 3")

        # Count should be 3
        count = get_message_count()
        assert count == 3

        logger.info("Message count test passed")

    def test_search_messages(self):
        """Test searching messages by text content"""
        from messages import search_messages, store_message

        # Add test messages
        store_message("Hello world")
        store_message("Goodbye world")
        store_message("Hello there")
        store_message("Not found")

        # Search for "hello"
        results = search_messages("hello")
        assert len(results) == 2
        assert all("hello" in result.text.lower() for result in results)

        # Search for "world"
        results = search_messages("world")
        assert len(results) == 2
        assert all("world" in result.text.lower() for result in results)

        # Search for non-existent text
        results = search_messages("xyz")
        assert len(results) == 0

        logger.info("Search messages test passed")

    def test_messages_by_date_range(self):
        """Test getting messages within a date range"""
        from messages import get_messages_by_date_range, store_message

        base_time = datetime.now(timezone.utc)

        # Add messages at different times
        store_message("Before range", base_time - timedelta(hours=2))
        store_message("In range 1", base_time - timedelta(minutes=30))
        store_message("In range 2", base_time + timedelta(minutes=30))
        store_message("After range", base_time + timedelta(hours=2))

        # Get messages within range
        start_time = base_time - timedelta(hours=1)
        end_time = base_time + timedelta(hours=1)

        results = get_messages_by_date_range(start_time.replace(tzinfo=None), end_time.replace(tzinfo=None))

        assert len(results) == 2
        assert all("range" in result.text.lower() for result in results)

        logger.info("Messages by date range test passed")

    def test_pydantic_message_validation(self):
        """Test that messages are properly validated as Pydantic models"""
        from messages import get_all_messages, store_message

        # Store a message
        store_message("Pydantic validation test")

        # Retrieve messages
        messages_list = get_all_messages()
        assert len(messages_list) == 1

        message = messages_list[0]

        # Verify it's a Message object with proper attributes
        assert isinstance(message, Message)
        assert hasattr(message, "text")
        assert hasattr(message, "timestamp")
        assert message.text == "Pydantic validation test"
        assert isinstance(message.timestamp, datetime)

        # Test Pydantic serialization
        message_dict = message.model_dump()
        assert message_dict["text"] == "Pydantic validation test"
        assert "timestamp" in message_dict

        logger.info("Pydantic message validation test passed")

    def test_database_error_handling(self):
        """Test database error handling"""
        from messages import store_message

        # Test with valid data (should work fine)
        try:
            store_message("Valid message")
            assert True
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            assert False, "Should not raise exception for valid message"

        logger.info("Database error handling test passed")

    def test_concurrent_access_simulation(self):
        """Test simulating concurrent access patterns"""
        from messages import get_all_messages, store_message

        # Simulate multiple rapid operations
        for i in range(10):
            store_message(f"Concurrent message {i}")

        # Verify all messages were stored
        messages_list = get_all_messages()
        assert len(messages_list) == 10

        # Verify message content
        for i, message in enumerate(reversed(messages_list)):  # Reverse because newest first
            assert message.text == f"Concurrent message {i}"

        logger.info("Concurrent access simulation test passed")


if __name__ == "__main__":
    # Run tests directly
    import sys

    pytest.main([__file__, "-v", "--tb=short"])

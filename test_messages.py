"""
HTMX-FastAPI Service - Message Tests

Author: Andrew Stevko
Company: Stevko Cyber Services
License: GPL-3.0 (see LICENSE file for details)
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import messages

# Import the modules we want to test
from models import Base, Message, MessageDB


class TestMessages:
    """Test class for messages functionality"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, monkeypatch):
        """Setup and teardown for each test with isolated database"""
        # Create a temporary in-memory SQLite database for testing
        # (SQLite is compatible with SQLAlchemy and easier for testing)
        test_engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        # Create all tables
        Base.metadata.create_all(bind=test_engine)

        # Create session factory
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        # Patch the database module to use our test database
        monkeypatch.setattr("database.SessionLocal", TestSessionLocal)
        monkeypatch.setattr("database.engine", test_engine)

        # Also patch the messages module to use the test database
        monkeypatch.setattr("messages.SessionLocal", TestSessionLocal)

        yield

        # Cleanup: close the engine
        test_engine.dispose()

    def test_store_message_with_timestamp(self):
        """Test storing a message with a specific timestamp"""
        timestamp = datetime(2024, 12, 1, 14, 30, 22, tzinfo=timezone.utc)
        message_text = "Test message with timestamp"

        # Store the message
        messages.store_message(message_text, timestamp)

        # Retrieve and verify
        all_messages = messages.get_all_messages()
        assert len(all_messages) == 1

        message = all_messages[0]
        assert message.text == message_text
        # Convert to naive datetime for comparison (PostgreSQL stores as naive)
        expected_timestamp = timestamp.replace(tzinfo=None)
        assert message.timestamp == expected_timestamp

    def test_store_message_without_timestamp(self):
        """Test storing a message without timestamp (should use current time)"""
        message_text = "Test message without timestamp"

        # Store the message
        messages.store_message(message_text)

        # Retrieve and verify
        all_messages = messages.get_all_messages()
        assert len(all_messages) == 1

        message = all_messages[0]
        assert message.text == message_text
        assert isinstance(message.timestamp, datetime)

        # Check that timestamp is recent (within the last minute)
        now = datetime.now(timezone.utc)
        # Convert message timestamp to UTC for comparison
        message_time = (
            message.timestamp.replace(tzinfo=timezone.utc) if message.timestamp.tzinfo is None else message.timestamp
        )
        time_diff = abs((now - message_time).total_seconds())
        assert time_diff < 60  # Should be within 1 minute

    def test_store_multiple_messages(self):
        """Test storing multiple messages"""
        messages_data = [
            ("First message", datetime(2024, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
            ("Second message", datetime(2024, 12, 1, 11, 0, 0, tzinfo=timezone.utc)),
            ("Third message", datetime(2024, 12, 1, 12, 0, 0, tzinfo=timezone.utc)),
        ]

        # Store messages
        for text, timestamp in messages_data:
            messages.store_message(text, timestamp)

        # Retrieve and verify
        all_messages = messages.get_all_messages()
        assert len(all_messages) == 3

        # Messages should be in descending order (newest first)
        for i, message in enumerate(all_messages):
            expected_text, expected_timestamp = messages_data[2 - i]  # Reverse order
            assert message.text == expected_text
            assert message.timestamp == expected_timestamp.replace(tzinfo=None)

    def test_get_messages_ascending_order(self):
        """Test retrieving messages in ascending order"""
        messages_data = [
            ("First", datetime(2024, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
            ("Second", datetime(2024, 12, 1, 11, 0, 0, tzinfo=timezone.utc)),
            ("Third", datetime(2024, 12, 1, 12, 0, 0, tzinfo=timezone.utc)),
        ]

        # Store messages
        for text, timestamp in messages_data:
            messages.store_message(text, timestamp)

        # Retrieve in ascending order
        all_messages = messages.get_all_messages(descending=False)
        assert len(all_messages) == 3

        # Messages should be in ascending order (oldest first)
        for i, message in enumerate(all_messages):
            expected_text, expected_timestamp = messages_data[i]
            assert message.text == expected_text
            assert message.timestamp == expected_timestamp.replace(tzinfo=None)

    def test_empty_messages_list(self):
        """Test retrieving messages when none exist"""
        all_messages = messages.get_all_messages()
        assert len(all_messages) == 0
        assert isinstance(all_messages, list)

    def test_message_pydantic_validation(self):
        """Test that get_all_messages returns proper Message objects"""
        message_text = "Test Pydantic validation"
        timestamp = datetime(2024, 12, 1, 14, 30, 22, tzinfo=timezone.utc)

        # Store message
        messages.store_message(message_text, timestamp)

        # Retrieve messages
        all_messages = messages.get_all_messages()
        assert len(all_messages) == 1

        message = all_messages[0]

        # Verify it's a Message object with proper attributes
        assert isinstance(message, Message)
        assert hasattr(message, "text")
        assert hasattr(message, "timestamp")
        assert message.text == message_text
        assert message.timestamp == timestamp.replace(tzinfo=None)

        # Test Pydantic serialization
        message_dict = message.model_dump()
        assert message_dict["text"] == message_text
        assert "timestamp" in message_dict

    def test_get_message_count(self):
        """Test getting message count"""
        # Initially should be 0
        count = messages.get_message_count()
        assert count == 0

        # Add some messages
        messages.store_message("Message 1")
        messages.store_message("Message 2")
        messages.store_message("Message 3")

        # Count should be 3
        count = messages.get_message_count()
        assert count == 3

    def test_search_messages(self):
        """Test searching messages by text content"""
        # Add test messages
        messages.store_message("Hello world")
        messages.store_message("Goodbye world")
        messages.store_message("Hello there")
        messages.store_message("Not found")

        # Search for "hello"
        results = messages.search_messages("hello")
        assert len(results) == 2
        assert all("hello" in result.text.lower() for result in results)

        # Search for "world"
        results = messages.search_messages("world")
        assert len(results) == 2
        assert all("world" in result.text.lower() for result in results)

        # Search for non-existent text
        results = messages.search_messages("xyz")
        assert len(results) == 0

    def test_get_messages_by_date_range(self):
        """Test getting messages within a date range"""
        base_time = datetime(2024, 12, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Add messages at different times
        messages.store_message("Before range", base_time - timedelta(hours=2))
        messages.store_message("In range 1", base_time - timedelta(minutes=30))
        messages.store_message("In range 2", base_time + timedelta(minutes=30))
        messages.store_message("After range", base_time + timedelta(hours=2))

        # Get messages within range
        start_time = base_time - timedelta(hours=1)
        end_time = base_time + timedelta(hours=1)

        results = messages.get_messages_by_date_range(start_time.replace(tzinfo=None), end_time.replace(tzinfo=None))

        assert len(results) == 2
        assert all("range" in result.text.lower() for result in results)

    def test_timestamp_precision(self):
        """Test that timestamps maintain reasonable precision"""
        # Store message with precise timestamp
        precise_time = datetime(2024, 12, 1, 14, 30, 22, 123456, tzinfo=timezone.utc)
        messages.store_message("Precise timestamp test", precise_time)

        # Retrieve and check precision
        all_messages = messages.get_all_messages()
        assert len(all_messages) == 1

        stored_time = all_messages[0].timestamp
        expected_time = precise_time.replace(tzinfo=None)

        # Check that the time is preserved (microsecond precision may be reduced)
        time_diff = abs((stored_time - expected_time).total_seconds())
        assert time_diff < 1  # Should be within 1 second

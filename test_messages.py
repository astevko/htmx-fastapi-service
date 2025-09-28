import pytest
import duckdb
from datetime import datetime, timezone, timedelta
from messages import store_message, get_all_messages, clear_messages
from models import Message


class TestMessagesComponent:
    """Test suite for the messages component using DuckDB"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, monkeypatch):
        """Setup and teardown for each test with isolated database"""
        # Use in-memory database for testing
        test_conn = duckdb.connect(':memory:')
        
        # Create sequence for auto-incrementing ID
        test_conn.execute("CREATE SEQUENCE IF NOT EXISTS id_sequence START 1;")
        
        # Create messages table with auto-incrementing ID
        test_conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER DEFAULT nextval('id_sequence'),
            text VARCHAR NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
        """)
        
        # Patch the messages module to use our test database
        monkeypatch.setattr('messages.conn', test_conn)
        
        yield
        
        # Cleanup: close the connection
        test_conn.close()
    
    def test_store_message_with_timestamp(self):
        """Test storing a message with a specific timestamp"""
        test_text = "Test message with timestamp"
        test_timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        store_message(test_text, test_timestamp)
        
        messages = get_all_messages()
        assert len(messages) == 1
        assert messages[0].text == test_text
        # DuckDB converts UTC to local time, so we need to account for that
        stored_timestamp = messages[0].timestamp
        # DuckDB converts to local time (PST = UTC-8)
        expected_local = test_timestamp.replace(tzinfo=None) - timedelta(hours=8)
        assert stored_timestamp == expected_local
    
    def test_store_message_without_timestamp(self):
        """Test storing a message without timestamp (should use DuckDB's now())"""
        test_text = "Test message without timestamp"
        
        store_message(test_text)
        
        messages = get_all_messages()
        assert len(messages) == 1
        assert messages[0].text == test_text
        
        # Check that a timestamp was stored (should be recent)
        stored_timestamp = messages[0].timestamp
        assert isinstance(stored_timestamp, datetime)
        # Verify it's within the last hour (reasonable check for DuckDB's now())
        now = datetime.now()
        assert stored_timestamp <= now
        assert stored_timestamp >= now - timedelta(hours=1)
    
    def test_get_all_messages_descending_order(self):
        """Test retrieving messages in descending order (newest first)"""
        # Store messages with different timestamps
        base_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        
        store_message("First message", base_time)
        store_message("Second message", base_time + timedelta(minutes=5))
        store_message("Third message", base_time + timedelta(minutes=10))
        
        messages = get_all_messages(descending=True)
        
        assert len(messages) == 3
        assert messages[0].text == "Third message"  # Newest first
        assert messages[1].text == "Second message"
        assert messages[2].text == "First message"  # Oldest last
    
    def test_get_all_messages_ascending_order(self):
        """Test retrieving messages in ascending order (oldest first)"""
        # Store messages with different timestamps
        base_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        
        store_message("First message", base_time)
        store_message("Second message", base_time + timedelta(minutes=5))
        store_message("Third message", base_time + timedelta(minutes=10))
        
        messages = get_all_messages(descending=False)
        
        assert len(messages) == 3
        assert messages[0].text == "First message"  # Oldest first
        assert messages[1].text == "Second message"
        assert messages[2].text == "Third message"  # Newest last
    
    def test_get_all_messages_empty_database(self):
        """Test retrieving messages from empty database"""
        messages = get_all_messages()
        assert messages == []
    
    def test_clear_messages(self):
        """Test clearing all messages from database"""
        # Store some messages
        store_message("Message 1")
        store_message("Message 2")
        store_message("Message 3")
        
        # Verify messages exist
        messages = get_all_messages()
        assert len(messages) == 3
        
        # Clear all messages
        clear_messages()
        
        # Verify messages are gone
        messages = get_all_messages()
        assert messages == []
    
    def test_store_multiple_messages(self):
        """Test storing multiple messages and verifying they persist"""
        messages_data = [
            ("Hello world", datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)),
            ("HTMX is awesome", datetime(2024, 1, 15, 10, 5, 0, tzinfo=timezone.utc)),
            ("FastAPI rocks", datetime(2024, 1, 15, 10, 10, 0, tzinfo=timezone.utc)),
        ]
        
        # Store all messages
        for text, timestamp in messages_data:
            store_message(text, timestamp)
        
        # Retrieve and verify
        messages = get_all_messages(descending=True)
        assert len(messages) == 3
        
        # Check content and order
        for i, (expected_text, expected_timestamp) in enumerate(messages_data[::-1]):
            assert messages[i].text == expected_text
            # DuckDB converts to local time (PST = UTC-8)
            expected_local = expected_timestamp.replace(tzinfo=None) - timedelta(hours=8)
            assert messages[i].timestamp == expected_local
    
    def test_message_with_special_characters(self):
        """Test storing messages with special characters and unicode"""
        special_messages = [
            "Message with émojis 🚀",
            "Message with quotes \"double\" and 'single'",
            "Message with <HTML> & XML entities",
            "Message with newlines\nand\ttabs",
            "Message with unicode: 你好世界",
        ]
        
        for text in special_messages:
            store_message(text)
        
        messages = get_all_messages()
        assert len(messages) == len(special_messages)
        
        # Verify all messages are stored correctly
        stored_texts = [msg.text for msg in messages]
        for text in special_messages:
            assert text in stored_texts
    
    def test_message_with_empty_text(self):
        """Test storing empty message text"""
        store_message("")
        
        messages = get_all_messages()
        assert len(messages) == 1
        assert messages[0].text == ""
    
    def test_large_message_text(self):
        """Test storing large message text"""
        large_text = "A" * 1000  # 1000 character message
        
        store_message(large_text)
        
        messages = get_all_messages()
        assert len(messages) == 1
        assert messages[0].text == large_text
        assert len(messages[0].text) == 1000
    
    def test_timestamp_precision(self):
        """Test timestamp precision with microseconds"""
        precise_timestamp = datetime(2024, 1, 15, 12, 30, 45, 123456, tzinfo=timezone.utc)
        
        store_message("Precise timestamp test", precise_timestamp)
        
        messages = get_all_messages()
        assert len(messages) == 1
        stored_timestamp = messages[0].timestamp
        
        # Check that timestamp precision is preserved (DuckDB converts to local time)
        expected_local = precise_timestamp.replace(tzinfo=None) - timedelta(hours=8)
        assert stored_timestamp == expected_local
        assert stored_timestamp.microsecond == 123456
    
    def test_concurrent_message_operations(self):
        """Test that multiple rapid message operations work correctly"""
        # Simulate rapid message storage
        for i in range(50):
            store_message(f"Rapid message {i}")
        
        messages = get_all_messages()
        assert len(messages) == 50
        
        # Verify all messages are present
        message_texts = [msg.text for msg in messages]
        for i in range(50):
            assert f"Rapid message {i}" in message_texts
    
    def test_message_pydantic_validation(self):
        """Test that returned messages are proper Pydantic Message objects"""
        store_message("Test message for Pydantic validation")
        
        messages = get_all_messages()
        assert len(messages) == 1
        
        # Verify it's a Message object
        message = messages[0]
        assert isinstance(message, Message)
        
        # Verify it has the expected attributes
        assert hasattr(message, 'text')
        assert hasattr(message, 'timestamp')
        
        # Verify the values
        assert message.text == "Test message for Pydantic validation"
        assert isinstance(message.timestamp, datetime)
        
        # Test that we can serialize/deserialize (Pydantic validation)
        message_dict = message.model_dump()
        assert message_dict['text'] == "Test message for Pydantic validation"
        assert isinstance(message_dict['timestamp'], datetime)
        
        # Test recreation from dict
        recreated_message = Message(**message_dict)
        assert recreated_message.text == message.text
        assert recreated_message.timestamp == message.timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

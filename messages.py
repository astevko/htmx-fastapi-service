import duckdb
from datetime import datetime
from models import Message

# Initialize DuckDB connection and create table if not exists
conn = duckdb.connect(database='messages.duckdb', read_only=False)

# Create sequence for auto-incrementing ID
conn.execute("CREATE SEQUENCE IF NOT EXISTS id_sequence START 1;")

# Create messages table with auto-incrementing ID
conn.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER DEFAULT nextval('id_sequence'),
    text VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL
)
""")

def store_message(text: str, timestamp: datetime = None):
    """Store a message in DuckDB"""
    if timestamp is None:
        # Use DuckDB's now() function for timestamp, let auto-increment handle ID
        conn.execute(
            "INSERT INTO messages (text, timestamp) VALUES (?, now())",
            [text]
        )
    else:
        # Use provided timestamp, let auto-increment handle ID
        conn.execute(
            "INSERT INTO messages (text, timestamp) VALUES (?, ?)",
            [text, timestamp]
        )

def get_all_messages(descending: bool = True) -> list[Message]:
    """Retrieve all messages from DuckDB as Message objects, newest first by default"""
    order = "DESC" if descending else "ASC"
    result = conn.execute(
        f"SELECT text, timestamp FROM messages ORDER BY timestamp {order}"
    ).fetchall()
    
    # Convert raw database results to Message objects for type safety and validation
    return [Message(text=text, timestamp=timestamp) for text, timestamp in result]

def clear_messages():
    """Delete all messages (for testing/demo purposes)"""
    conn.execute("DELETE FROM messages")

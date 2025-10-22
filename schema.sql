-- Database schema for Omi transcript processing system

-- Table to store conversation messages (user and AI)
-- Create this first since transcripts references it
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_type VARCHAR(10) NOT NULL CHECK (message_type IN ('user', 'ai')),
    message_text TEXT NOT NULL,
    tool_executions TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store transcript segments from Omi device
CREATE TABLE IF NOT EXISTS transcripts (
    id SERIAL PRIMARY KEY,
    segment_id VARCHAR(255) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    speaker VARCHAR(50),
    speaker_id INTEGER,
    is_user BOOLEAN DEFAULT FALSE,
    start_time FLOAT,
    end_time FLOAT,
    session_id VARCHAR(255),
    message_id INTEGER,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transcripts_processed ON transcripts(processed);
CREATE INDEX IF NOT EXISTS idx_transcripts_session_id ON transcripts(session_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_message_id ON transcripts(message_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_received_at ON transcripts(received_at);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type);


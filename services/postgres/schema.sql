-- Enable RUM extension for full-text search
CREATE EXTENSION IF NOT EXISTS rum;

-- Enable pg_trgm for spelling suggestions (extra credit)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-------------------------------------------------------------------------------
-- USERS
-------------------------------------------------------------------------------
CREATE TABLE users (
    id_users    BIGSERIAL PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast username lookup (used in login)
CREATE INDEX idx_users_username ON users(username);

-------------------------------------------------------------------------------
-- CREDENTIALS
-- Stored separately from users for security (separation of concerns)
-------------------------------------------------------------------------------
CREATE TABLE credentials (
    id_credentials  BIGSERIAL PRIMARY KEY,
    id_users        BIGINT NOT NULL UNIQUE REFERENCES users(id_users) ON DELETE CASCADE,
    password        TEXT NOT NULL   -- stores hashed password, never plaintext
);

-- Index for fast credential lookup by user
CREATE INDEX idx_credentials_id_users ON credentials(id_users);

-------------------------------------------------------------------------------
-- MESSAGES (tweets)
-------------------------------------------------------------------------------
CREATE TABLE messages (
    id_messages BIGSERIAL PRIMARY KEY,
    id_users    BIGINT NOT NULL REFERENCES users(id_users) ON DELETE CASCADE,
    message     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast chronological listing (homepage query)
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- Index for fast user lookup (show user's messages)
CREATE INDEX idx_messages_id_users ON messages(id_users);

-- RUM index for full-text search with ranking support
-- RUM supports ts_rank natively, unlike GIN
CREATE INDEX idx_messages_rum ON messages
    USING rum(to_tsvector('english', message));

-- pg_trgm index for spelling suggestions (extra credit)
CREATE INDEX idx_messages_trgm ON messages
    USING gin(message gin_trgm_ops);


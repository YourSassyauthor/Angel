CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT PRIMARY KEY REFERENCES guilds(guild_id) ON DELETE CASCADE,

    prefix TEXT NOT NULL DEFAULT '!',
    moderation_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    logging_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    ai_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    trust_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    anti_raid_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS members (
    guild_id BIGINT NOT NULL REFERENCES guilds(guild_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,

    username TEXT,
    display_name TEXT,

    trust_score INTEGER NOT NULL DEFAULT 100,
    goodwill_score INTEGER NOT NULL DEFAULT 100,

    warnings INTEGER NOT NULL DEFAULT 0,

    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS warnings (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,

    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (guild_id, user_id)
        REFERENCES members(guild_id, user_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS moderation_actions (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    moderator_id BIGINT,

    action TEXT NOT NULL,
    reason TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS blacklisted_words (
    guild_id BIGINT NOT NULL REFERENCES guilds(guild_id) ON DELETE CASCADE,

    word TEXT NOT NULL,
    severity INTEGER NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (guild_id, word)
);

CREATE TABLE IF NOT EXISTS join_events (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    account_created_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    account_age_days INTEGER,
    suspicious BOOLEAN NOT NULL DEFAULT FALSE,

    risk_score INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS raid_events (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    join_count INTEGER NOT NULL DEFAULT 0,
    severity INTEGER NOT NULL DEFAULT 0,

    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT,

    event_type TEXT NOT NULL,
    details JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_members_user
    ON members(user_id);

CREATE INDEX IF NOT EXISTS idx_warnings_guild_user
    ON warnings(guild_id, user_id);

CREATE INDEX IF NOT EXISTS idx_moderation_guild
    ON moderation_actions(guild_id);

CREATE INDEX IF NOT EXISTS idx_join_events_guild
    ON join_events(guild_id);

CREATE INDEX IF NOT EXISTS idx_join_events_user
    ON join_events(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_guild
    ON audit_logs(guild_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created
    ON audit_logs(created_at);

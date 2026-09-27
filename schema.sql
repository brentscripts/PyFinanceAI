-- Lookup / structural tables first, so the FK columns on transactions below
-- have something to point at. SQLite doesn't require creation order to
-- satisfy foreign keys, but keeping it in dependency order is easier to read.

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT,
    institution TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS households (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL REFERENCES households(id),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    parent_category_id INTEGER REFERENCES categories(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS category_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    match_type TEXT NOT NULL DEFAULT 'contains',
    source TEXT NOT NULL DEFAULT 'manual',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- account_id / category_id are additive, nullable FKs appended at the END
-- of the existing column list. Existing INSERTs name their columns
-- explicitly (see database/db.py, webapp/app.py), so these default to NULL
-- and don't break anything. They stay unused until Auth/Categorization
-- Engine build the logic that populates them.
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    post_date TEXT,
    description TEXT NOT NULL,
    original_description TEXT,
    category TEXT,
    amount REAL NOT NULL,
    type TEXT,
    account TEXT,
    source TEXT NOT NULL,
    tags TEXT,
    memo TEXT,
    account_id INTEGER REFERENCES accounts(id),
    category_id INTEGER REFERENCES categories(id)
);

-- Records what actually decided each transaction's category, distinct from
-- category_rules (which describes the pattern itself). A manual correction
-- is a new row, not an overwrite, so the earlier guess stays as a training
-- signal (c-log) instead of being lost. Also how c-dspy's LLM guesses are
-- distinguished from rule matches, and how a swapped provider's accuracy
-- can be compared against a previous one.
CREATE TABLE IF NOT EXISTS categorization_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    method TEXT NOT NULL,              -- 'manual' | 'rule' | 'llm'
    rule_id INTEGER REFERENCES category_rules(id),
    provider TEXT,                     -- e.g. 'grok', 'ollama' — set only when method='llm'
    model TEXT,
    confidence REAL,
    -- Groups every categorization decision made during one run (e.g. one
    -- CSV import, or one nightly LLM sweep over uncategorized transactions)
    -- so a run can be inspected, compared, or rolled back as a unit.
    batch_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_categorization_events_transaction
    ON categorization_events(transaction_id);
CREATE INDEX IF NOT EXISTS idx_categorization_events_batch
    ON categorization_events(batch_id);

-- Cached DSPy-generated natural-language summaries (n-insights), so the
-- dashboard doesn't call an LLM on every page load. Regenerate on a
-- schedule or on-demand; history of past summaries is kept rather than
-- overwritten.
CREATE TABLE IF NOT EXISTS insight_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,                -- e.g. 'monthly_summary'
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    provider TEXT,
    model TEXT,
    content TEXT NOT NULL,
    batch_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_insight_snapshots_period
    ON insight_snapshots(kind, period_start, period_end);

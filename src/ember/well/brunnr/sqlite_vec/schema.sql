-- sqlite_vec Brunnr — on-disk schema (version 1).
--
-- Tables mirror the Gungnir reference shape (see
-- docs/adapters/GUNGNIR_WELL_REFERENCE.md §3) so a future export from
-- one and import into the other stays bytewise compatible.
--
-- {embedding_dim} is substituted at apply time from BrunnrConfig.
-- This file is loaded as a resource by adapter.py.

CREATE TABLE IF NOT EXISTS schema_version (
    version    INTEGER PRIMARY KEY,
    applied_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO schema_version(version) VALUES (1);

CREATE TABLE IF NOT EXISTS documents (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source       TEXT    NOT NULL,
    title        TEXT,
    content_type TEXT,
    hash         TEXT    UNIQUE,
    metadata     TEXT    NOT NULL DEFAULT '{{}}',
    ingested_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source);

CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text        TEXT    NOT NULL,
    char_start  INTEGER,
    char_end    INTEGER,
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_document_idx ON chunks(document_id);

-- Vector store: one row per chunk, embedding as float[{embedding_dim}].
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_vectors USING vec0(
    chunk_id  INTEGER PRIMARY KEY,
    embedding float[{embedding_dim}]
);

-- Full-text search over chunk text. Synchronised by triggers below.
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
    text,
    content='chunks',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS chunks_ai_fts AFTER INSERT ON chunks BEGIN
    INSERT INTO chunk_fts(rowid, text) VALUES (NEW.id, NEW.text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad_fts AFTER DELETE ON chunks BEGIN
    INSERT INTO chunk_fts(chunk_fts, rowid, text) VALUES ('delete', OLD.id, OLD.text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au_fts AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunk_fts(chunk_fts, rowid, text) VALUES ('delete', OLD.id, OLD.text);
    INSERT INTO chunk_fts(rowid, text) VALUES (NEW.id, NEW.text);
END;

-- Episodes — one row per remembered conversation turn.
CREATE TABLE IF NOT EXISTS episodes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_input    TEXT    NOT NULL,
    ember_reply       TEXT    NOT NULL,
    cited_chunk_ids   TEXT    NOT NULL DEFAULT '[]',
    funi_model        TEXT    NOT NULL DEFAULT '',
    well_disconnected INTEGER NOT NULL DEFAULT 0,
    started_at        TEXT,
    completed_at      TEXT
);

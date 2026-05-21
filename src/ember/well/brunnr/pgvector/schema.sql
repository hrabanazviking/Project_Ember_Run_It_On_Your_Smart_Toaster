-- pgvector Brunnr — Postgres schema (version 1).
--
-- Mirrors the Gungnir reference shape exactly so an operator's existing
-- Gungnir tables can serve as the Well without modification (see
-- docs/adapters/GUNGNIR_WELL_REFERENCE.md §3 and ADR 0010 §2.2). When
-- the adapter probes and finds these tables already present with the
-- expected embedding dimension, it skips this DDL entirely.
--
-- {embedding_dim} is substituted at apply time from BrunnrConfig.
-- {schema} is substituted at apply time from PgVectorConfig.schema.
-- This file is loaded as a package resource by adapter.py.
--
-- The adapter executes each statement individually so {schema} can be
-- quoted with format_ident and the parameter binding stays portable
-- across schema names.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS {schema}.schema_version (
    version    integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO {schema}.schema_version(version) VALUES (1)
    ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS {schema}.documents (
    id           bigserial PRIMARY KEY,
    source       text NOT NULL,
    title        text,
    content_type text,
    hash         text UNIQUE,
    metadata     jsonb NOT NULL DEFAULT '{}'::jsonb,
    ingested_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS documents_source_idx
    ON {schema}.documents(source);

CREATE TABLE IF NOT EXISTS {schema}.chunks (
    id          bigserial PRIMARY KEY,
    document_id bigint NOT NULL REFERENCES {schema}.documents(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    text        text NOT NULL,
    embedding   vector({embedding_dim}),
    tsv         tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    char_start  integer,
    char_end    integer,
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON {schema}.chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_tsv_gin
    ON {schema}.chunks USING gin (tsv);

-- Episodes — Ember-side conversation log (Gungnir does not have this).
-- ADR 0010 §2.3: if the adapter probes onto an existing Gungnir,
-- documents+chunks are reused but episodes is still created here.
CREATE TABLE IF NOT EXISTS {schema}.episodes (
    id                bigserial PRIMARY KEY,
    operator_input    text NOT NULL,
    ember_reply       text NOT NULL,
    cited_chunk_ids   jsonb NOT NULL DEFAULT '[]'::jsonb,
    funi_model        text NOT NULL DEFAULT '',
    well_disconnected boolean NOT NULL DEFAULT false,
    started_at        timestamptz,
    completed_at      timestamptz
);

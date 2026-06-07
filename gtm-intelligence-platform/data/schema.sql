CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    industry TEXT,
    headcount INT,
    revenue_range TEXT,
    funding_total NUMERIC,
    funding_round TEXT,
    funding_date DATE,
    tech_stack JSONB DEFAULT '[]',
    icp_score INT DEFAULT 0,
    last_researched_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    stage TEXT NOT NULL DEFAULT 'discovery',
    amount NUMERIC DEFAULT 0,
    owner TEXT,
    probability INT DEFAULT 10,
    deal_health_score INT,
    meddic_scores JSONB DEFAULT '{}',
    meddic_gaps JSONB DEFAULT '[]',
    nba_text TEXT,
    last_scored_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    signal_type TEXT NOT NULL,
    source TEXT,
    title TEXT,
    description TEXT,
    weight DECIMAL(3,1) DEFAULT 1.0,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    icp_score INT,
    signal_summary JSONB DEFAULT '{}',
    competitive_intel JSONB DEFAULT '{}',
    recommended_angle TEXT,
    email_draft TEXT,
    file_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE account_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    embedding VECTOR(1536),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE deal_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    embedding VECTOR(1536),
    content TEXT,
    outcome TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transcripts_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    call_id TEXT,
    company TEXT,
    date TIMESTAMPTZ,
    duration_seconds INT,
    participants JSONB DEFAULT '[]',
    full_transcript JSONB DEFAULT '[]',
    meddpicc_analysis JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE similar_deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id) ON DELETE SET NULL,
    company TEXT,
    outcome TEXT,
    acv NUMERIC,
    days_to_close INT,
    meddic_profile JSONB DEFAULT '{}',
    winning_patterns JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_deals_account ON deals(account_id);
CREATE INDEX idx_deals_health ON deals(deal_health_score);
CREATE INDEX idx_signals_account ON signals(account_id);
CREATE INDEX idx_signals_type ON signals(signal_type);
CREATE INDEX idx_briefs_account ON briefs(account_id);
CREATE INDEX idx_account_embeddings ON account_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
CREATE INDEX idx_deal_embeddings ON deal_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
CREATE INDEX idx_transcripts_deal ON transcripts_store(deal_id);
CREATE INDEX idx_similar_deals_deal ON similar_deals(deal_id);

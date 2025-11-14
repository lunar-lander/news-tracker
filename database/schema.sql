-- India News Tracker Database Schema
-- PostgreSQL with TimescaleDB extension

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- RSS SOURCES
-- ============================================================================

CREATE TABLE rss_sources (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  url TEXT NOT NULL UNIQUE,
  category VARCHAR(100),  -- national, regional, language
  language VARCHAR(50),
  region VARCHAR(100),  -- state or region
  priority VARCHAR(20),  -- high, medium, low
  refresh_interval INTEGER DEFAULT 300,  -- seconds
  enabled BOOLEAN DEFAULT true,
  last_fetched_at TIMESTAMP,
  last_success_at TIMESTAMP,
  consecutive_failures INTEGER DEFAULT 0,
  meta_data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rss_sources_enabled ON rss_sources(enabled);
CREATE INDEX idx_rss_sources_priority ON rss_sources(priority);

-- ============================================================================
-- RSS ENTRIES
-- ============================================================================

CREATE TABLE rss_entries (
  id SERIAL PRIMARY KEY,
  source_id INTEGER REFERENCES rss_sources(id) ON DELETE CASCADE,
  guid TEXT UNIQUE NOT NULL,  -- RSS GUID
  title TEXT NOT NULL,
  description TEXT,
  link TEXT NOT NULL,
  published_at TIMESTAMP NOT NULL,
  author VARCHAR(255),
  raw_data JSONB,  -- Original RSS item
  content_hash VARCHAR(64),  -- For deduplication
  processing_status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rss_entries_published ON rss_entries(published_at DESC);
CREATE INDEX idx_rss_entries_status ON rss_entries(processing_status);
CREATE INDEX idx_rss_entries_source ON rss_entries(source_id);
CREATE INDEX idx_rss_entries_hash ON rss_entries(content_hash);

-- ============================================================================
-- ARTICLES (Scraped Content)
-- ============================================================================

CREATE TABLE articles (
  id SERIAL PRIMARY KEY,
  rss_entry_id INTEGER REFERENCES rss_entries(id) ON DELETE CASCADE,
  full_text TEXT,
  extracted_text TEXT,  -- Clean text for LLM
  word_count INTEGER,
  language VARCHAR(50),
  scraped_at TIMESTAMP,
  scraping_method VARCHAR(100),
  scraping_success BOOLEAN,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_articles_entry ON articles(rss_entry_id);
CREATE INDEX idx_articles_language ON articles(language);
CREATE INDEX idx_articles_scraped ON articles(scraped_at DESC);

-- ============================================================================
-- CLASSIFICATIONS (LLM Output)
-- ============================================================================

CREATE TABLE classifications (
  id SERIAL PRIMARY KEY,
  article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
  llm_provider VARCHAR(50),
  llm_model VARCHAR(100),
  classified_at TIMESTAMP DEFAULT NOW(),

  -- Primary classifications
  tags VARCHAR(100)[],  -- Array of tags
  tag_confidences JSONB,  -- {"murder": 0.95, "state_up": 0.89}

  -- Extracted metadata
  summary TEXT,
  severity VARCHAR(20),  -- low, medium, high, critical
  incident_date DATE,
  state VARCHAR(100),
  city VARCHAR(100),
  district VARCHAR(100),
  location_confidence FLOAT,

  -- Entities
  persons VARCHAR(255)[],
  organizations VARCHAR(255)[],

  -- LLM response
  raw_llm_response JSONB,
  llm_tokens_used INTEGER,
  llm_cost_usd DECIMAL(10, 6),

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_classifications_article ON classifications(article_id);
CREATE INDEX idx_classifications_tags ON classifications USING GIN(tags);
CREATE INDEX idx_classifications_date ON classifications(incident_date DESC);
CREATE INDEX idx_classifications_severity ON classifications(severity);
CREATE INDEX idx_classifications_state ON classifications(state);

-- ============================================================================
-- NEWS EVENTS (Denormalized View for Fast Queries)
-- ============================================================================

CREATE TABLE news_events (
  id SERIAL PRIMARY KEY,
  rss_entry_id INTEGER REFERENCES rss_entries(id) ON DELETE CASCADE,
  article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
  classification_id INTEGER REFERENCES classifications(id) ON DELETE CASCADE,

  -- Denormalized for fast queries
  headline TEXT NOT NULL,
  summary TEXT,
  source_name VARCHAR(255),
  source_url TEXT,
  published_at TIMESTAMP NOT NULL,
  incident_date DATE,

  -- Categories
  primary_tag VARCHAR(100),
  all_tags VARCHAR(100)[],
  severity VARCHAR(20),

  -- Location
  state VARCHAR(100),
  city VARCHAR(100),
  region VARCHAR(100),

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_events_published ON news_events(published_at DESC);
CREATE INDEX idx_news_events_incident ON news_events(incident_date DESC);
CREATE INDEX idx_news_events_primary_tag ON news_events(primary_tag);
CREATE INDEX idx_news_events_tags ON news_events USING GIN(all_tags);
CREATE INDEX idx_news_events_state ON news_events(state);
CREATE INDEX idx_news_events_severity ON news_events(severity);
CREATE INDEX idx_news_events_headline ON news_events USING GIN(to_tsvector('english', headline));

-- Convert news_events to TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('news_events', 'published_at', if_not_exists => TRUE);

-- ============================================================================
-- PROCESSING LOGS
-- ============================================================================

CREATE TABLE processing_logs (
  id SERIAL PRIMARY KEY,
  job_type VARCHAR(50) NOT NULL,  -- rss_fetch, scrape, classify
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  status VARCHAR(20),  -- running, completed, failed
  items_processed INTEGER DEFAULT 0,
  items_failed INTEGER DEFAULT 0,
  error_message TEXT,
  meta_data JSONB
);

CREATE INDEX idx_processing_logs_type ON processing_logs(job_type);
CREATE INDEX idx_processing_logs_started ON processing_logs(started_at DESC);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for rss_sources
CREATE TRIGGER update_rss_sources_updated_at
    BEFORE UPDATE ON rss_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA (Optional - will be loaded from config/rss-sources.yaml)
-- ============================================================================

-- You can add some test data here if needed for development
-- INSERT INTO rss_sources (name, url, category, language, region, priority, enabled)
-- VALUES ('Test Source', 'https://example.com/rss', 'national', 'english', 'national', 'high', true);

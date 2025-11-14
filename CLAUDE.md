# India News Tracker - Comprehensive Requirements Document

## 1. Project Overview

**Project Name:** India News Tracker

**Tagline:** Building Data-Driven Social Consciousness Through Time-Series News Analysis

**Purpose:** To aggregate, categorize, and visualize serious news incidents across India over time, enabling citizens to track trends in crime, corruption, discrimination, and other critical social issues through an interactive, data-driven platform.

## 2. Problem Statement

Modern news consumption is ephemeral - people read about events and forget them shortly after. This creates:
- **Memory Loss:** Important incidents fade from public consciousness
- **Pattern Blindness:** Difficulty in recognizing systemic issues and trends
- **Data Fragmentation:** No centralized view of incident volumes across regions and categories
- **Accountability Gap:** Hard to track if issues are improving or worsening over time

**Solution:** A time-series based news tracking system that preserves memory, reveals patterns, and builds data-driven social consciousness.

## 3. Core Features

### 3.1 RSS Feed Aggregation
- Comprehensive list of RSS feeds from major and regional Indian news sources
- Support for national outlets (Times of India, The Hindu, Indian Express, NDTV, etc.)
- Regional news sources covering all states and major cities
- Automatic feed discovery and validation
- Feed health monitoring and dead link detection
- Configurable feed refresh intervals

### 3.2 RSS Listener & Storage System
- Real-time RSS feed monitoring
- Deduplication logic to avoid storing duplicate news items
- Raw RSS data preservation (title, description, link, publication date, source)
- Efficient storage with indexing for fast retrieval
- Historical data retention policies
- Backup and archival strategies

### 3.3 Content Processing Pipeline
- **Fetch Stage:** Download full article text from source URLs
- **Text Extraction:** Parse HTML and extract clean article content
- **LLM Classification:** Use configurable LLM to analyze and tag content
- **Storage:** Save extracted text and classifications

### 3.4 LLM-Based News Classification

#### Categories/Tags to Track:
**Crime & Violence:**
- Murder
- Rape & Sexual Assault
- Robbery & Theft
- Kidnapping
- Assault & Battery
- Domestic Violence
- Organized Crime

**Governance & Corruption:**
- Political Corruption
- Bribery & Kickbacks
- Scams & Fraud
- Embezzlement
- Misuse of Power
- Electoral Malpractice

**Social Issues:**
- Discrimination (Caste, Religion, Gender, etc.)
- Hate Crimes
- Communal Violence
- Religious Tension
- Gender-based Violence
- Child Abuse

**Accidents & Disasters:**
- Traffic Accidents
- Industrial Accidents
- Building Collapses
- Fire Incidents
- Natural Disasters
- Rail/Air Accidents

**Justice & Legal:**
- Court Verdicts
- Arrests & Investigations
- Legal Reforms
- Police Action
- Judicial Misconduct

**Regional/State-specific:**
- Tag by State/Union Territory
- Tag by City/District
- Rural vs Urban classification

**Categories to EXCLUDE:**
- Entertainment & Celebrity News
- Sports (unless related to corruption/crime)
- Technology Product Launches
- General Business News
- Film Reviews
- Lifestyle Content

#### LLM Classification Requirements:
- Extract multiple tags per article (multi-label classification)
- Assign confidence scores to each tag
- Extract key entities (persons, places, organizations)
- Generate brief summary (1-2 sentences)
- Identify severity level (low, medium, high, critical)
- Extract temporal information (when the incident occurred)
- Identify victim/perpetrator information (where ethically appropriate)

### 3.5 React Dashboard

#### Homepage Layout:
- **Grid-based Dashboard:** Tiles of various sizes representing different news categories
- **Tile Sizing Logic:** Automatically determined by:
  - Volume of recent incidents (more incidents = larger tile)
  - Severity of incidents
  - Trending topics (increasing frequency over time)
  - User preferences and favorites

#### Time-Series Visualizations:
- **Interactive Charts:** Each tile contains a time-series visualization
- **Configurable Timeframes:** Day, Week, Month, Quarter, Year, All-time
- **Chart Types:**
  - Line graphs for trends over time
  - Bar charts for comparing volumes across regions
  - Heatmaps for geographic distribution
  - Stacked area charts for multi-category trends

#### Interactive Features:
- **Clickable Nodes:** Each data point on time-series is clickable
- **Sidebar Details:** Clicking opens a sidebar showing:
  - Headlines for that time period (with multilingual support for display)
  - Direct links to source articles
  - Summary statistics
  - Related incidents
  - Tags and classifications
- **Filtering:** Filter by date range, region, severity, tags
- **Search:** Basic headline search

#### Additional Dashboard Features:
- **Comparative Analytics:** Compare incident volumes across states/regions
- **Correlation Insights:** Identify potential correlations between categories

## 4. Configuration Management

### 4.1 Configurable Components

#### LLM Configuration:
```yaml
llm:
  provider: "openai" | "anthropic" | "cohere" | "google" | "local"
  model: "gpt-4" | "claude-3-opus" | "command-r-plus" | "gemini-pro" | "llama-3"
  api_key: "${LLM_API_KEY}"
  max_tokens: 2048
  temperature: 0.3
  classification_prompt_template: "path/to/prompt.txt"
  retry_policy:
    max_retries: 3
    backoff_factor: 2
  rate_limits:
    requests_per_minute: 60
    concurrent_requests: 10
```

#### RSS Feed Configuration:
```yaml
rss_feeds:
  - name: "Times of India"
    url: "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"
    category: "national"
    language: "english"
    refresh_interval: 300  # seconds
    enabled: true
    priority: "high"

  - name: "The Hindu"
    url: "https://www.thehindu.com/news/national/feeder/default.rss"
    category: "national"
    language: "english"
    refresh_interval: 300
    enabled: true
    priority: "high"

  # Add 50+ more feeds covering:
  # - Regional newspapers (Dainik Bhaskar, Amar Ujala, etc.)
  # - Language-specific outlets (Hindi, Tamil, Bengali, etc.)
  # - State-specific news portals
```

#### Tags Configuration:
```yaml
tags:
  enabled_categories:
    - murder
    - rape
    - corruption
    - discrimination
    - accidents
    # ... full list

  category_definitions:
    murder:
      keywords: ["murder", "killed", "homicide", "death", "body found"]
      severity_weights:
        mass_casualty: 10
        single_victim: 5

    corruption:
      keywords: ["corruption", "bribe", "scam", "fraud", "embezzlement"]
      severity_weights:
        political_high_level: 10
        bureaucratic: 7
        petty: 3

  exclusion_keywords:
    - "movie review"
    - "cricket match"
    - "celebrity wedding"
    - "tech product launch"
    # ... comprehensive list
```

#### Filter Configuration:
```yaml
filters:
  min_confidence_score: 0.7  # Only store classifications with >70% confidence
  min_article_length: 100    # Words
  max_article_age: 90        # Days (for processing)

  region_filters:
    enabled_states:
      - "All"  # Or specific states
    enabled_cities:
      - "All"  # Or specific cities

  severity_threshold: "low"  # low, medium, high, critical

  deduplication:
    enabled: true
    similarity_threshold: 0.85  # 85% similarity = duplicate
    timewindow: 86400  # 24 hours
```

#### Dashboard Configuration:
```yaml
dashboard:
  default_timeframe: "30d"  # days
  tile_sizing_algorithm: "volume_weighted"  # or "equal", "severity_weighted"

  visualizations:
    default_chart_type: "line"
    color_scheme: "vibrant_on_black"  # vibrant colors on pure black background
    animation_enabled: true

  theme:
    background_color: "#000000"  # Pure black, not grey
    text_color: "#FFFFFF"
    accent_colors:
      primary: "#FF6B6B"
      secondary: "#4ECDC4"
      success: "#95E1D3"
      warning: "#FFD93D"
      danger: "#F38181"

  features:
    enable_search: true
    enable_i18n_headlines: true  # Display multilingual headlines

  performance:
    data_points_limit: 1000  # per chart
    lazy_loading: true
    cache_duration: 300  # seconds
```

### 4.2 Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/newstrack

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Application
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=info

# Cron Jobs (configured in system crontab or Makefile)
# RSS_FETCH_CRON="*/5 * * * *"  # Every 5 minutes
# CONTENT_PROCESS_CRON="*/10 * * * *"  # Every 10 minutes

# Security
JWT_SECRET=...
ENCRYPTION_KEY=...
```

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Frontend (React + Chart.js)                   │
│  - Dashboard UI (Pure Black Theme)                           │
│  - Time-series Visualizations                                │
│  - Interactive Filtering                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                Backend API (Python/FastAPI)                  │
│  - API Endpoints                                             │
│  - Data Aggregation & Analytics                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │
                ┌──────▼──────┐
                │   Database  │
                │(PostgreSQL) │
                │ +TimescaleDB│
                └─────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Cron Jobs (System Crontab)                  │
│                                                              │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ RSS Fetcher   │  │   Content    │  │     LLM      │    │
│  │ (Every 5min)  │  │   Scraper    │  │  Classifier  │    │
│  │               │  │  (Every 10m) │  │  (Every 10m) │    │
│  └───────────────┘  └──────────────┘  └──────────────┘    │
│         │                   │                  │            │
│         └───────────────────┴──────────────────┘            │
│                             │                               │
│                             ▼                               │
│                      PostgreSQL DB                          │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Components

#### Frontend (React):
- **Framework:** React 18+ with TypeScript
- **State Management:** Zustand or Context API
- **Visualization:** Chart.js with react-chartjs-2
- **UI Components:** Tailwind CSS for styling (pure black theme)
- **Routing:** React Router
- **API Client:** Axios or Fetch API
- **Theme:** Pure black (#000000) background with vibrant chart colors

#### Backend API:
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **API Style:** REST
- **ORM:** SQLAlchemy 2.0+
- **Validation:** Pydantic (built into FastAPI)
- **ASGI Server:** Uvicorn

#### Background Jobs (Cron):
- **Scheduler:** System crontab or `make cron-*` commands
- **RSS Parser:** feedparser (Python library)
- **Web Scraper:** BeautifulSoup4 + requests or playwright
- **LLM Integration:** Direct API clients (openai, anthropic-sdk, etc.)
- **Language Detection:** langdetect or lingua (for multilingual content)

#### Data Storage:
- **Primary Database:** PostgreSQL 15+
  - Stores news articles, classifications, metadata
  - Time-series optimizations with TimescaleDB extension
  - Async connection pool with asyncpg

#### LLM Integration:
- **Multi-provider Support:** OpenAI, Anthropic, Google, Cohere, local models
- **Prompt Management:** Version-controlled prompts in config/prompts/
- **Fallback Strategy:** If primary LLM fails, use backup provider
- **Cost Optimization:** Cache LLM responses in database, batch processing

### 5.3 Data Flow

1. **RSS Ingestion (Cron: Every 5 minutes):**
   - Python script fetches all enabled RSS feeds from config
   - Parses RSS entries using feedparser
   - Deduplicates entries against existing database (by GUID/link hash)
   - Stores new entries in `rss_entries` table with status='pending'
   - Logs fetch statistics

2. **Content Processing (Cron: Every 10 minutes):**
   - Python script queries for entries with status='pending'
   - Fetches full article HTML from source URLs (batch processing)
   - Extracts clean text using BeautifulSoup or readability
   - Detects language using langdetect
   - Stores extracted text in `articles` table
   - Updates status to 'scraped' or 'failed'

3. **LLM Classification (Cron: Every 10 minutes):**
   - Python script queries for scraped articles without classification
   - Batch processes articles through configured LLM
   - Constructs prompt with article text and tag definitions
   - Calls LLM API (with retry logic)
   - Parses LLM response for tags, confidence, summary, location
   - Stores classifications in `classifications` table
   - Creates denormalized record in `news_events` table
   - Updates status to 'completed'

4. **API & Frontend:**
   - Frontend requests aggregated data via FastAPI endpoints
   - API queries database with filters and time ranges
   - Data transformed into Chart.js-compatible format
   - Frontend renders interactive dashboard with pure black theme

## 6. Data Models

### 6.1 Database Schema

#### `rss_sources` Table:
```sql
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
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `rss_entries` Table:
```sql
CREATE TABLE rss_entries (
  id SERIAL PRIMARY KEY,
  source_id INTEGER REFERENCES rss_sources(id),
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
```

#### `articles` Table:
```sql
CREATE TABLE articles (
  id SERIAL PRIMARY KEY,
  rss_entry_id INTEGER REFERENCES rss_entries(id),
  full_text TEXT,
  extracted_text TEXT,  -- Clean text for LLM
  word_count INTEGER,
  language VARCHAR(50),
  scraped_at TIMESTAMP,
  scraping_method VARCHAR(100),
  scraping_success BOOLEAN,
  error_message TEXT,
  html_stored_at TEXT,  -- S3 path if stored
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_articles_entry ON articles(rss_entry_id);
```

#### `classifications` Table:
```sql
CREATE TABLE classifications (
  id SERIAL PRIMARY KEY,
  article_id INTEGER REFERENCES articles(id),
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
CREATE INDEX idx_classifications_date ON classifications(incident_date);
CREATE INDEX idx_classifications_severity ON classifications(severity);
```

#### `news_events` Table (Aggregated View):
```sql
CREATE TABLE news_events (
  id SERIAL PRIMARY KEY,
  rss_entry_id INTEGER REFERENCES rss_entries(id),
  article_id INTEGER REFERENCES articles(id),
  classification_id INTEGER REFERENCES classifications(id),

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
CREATE INDEX idx_news_events_headline ON news_events USING GIN(to_tsvector('english', headline));
```

### 6.2 Time-Series Optimization

Use **TimescaleDB** extension for PostgreSQL:

```sql
-- Convert news_events to hypertable for time-series optimization
SELECT create_hypertable('news_events', 'published_at');

-- Create continuous aggregates for common queries
CREATE MATERIALIZED VIEW news_events_daily
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 day', published_at) AS day,
  primary_tag,
  state,
  severity,
  COUNT(*) as event_count,
  ARRAY_AGG(DISTINCT all_tags) as all_tags_aggregated
FROM news_events
GROUP BY day, primary_tag, state, severity;

-- Refresh policy
SELECT add_continuous_aggregate_policy('news_events_daily',
  start_offset => INTERVAL '1 month',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');
```

## 7. API Design

### 7.1 REST Endpoints

#### News Events:

```
GET /api/v1/events
Query Parameters:
  - start_date: ISO date string
  - end_date: ISO date string
  - tags: comma-separated tag list
  - state: state name
  - city: city name
  - severity: low|medium|high|critical
  - limit: integer (default 100, max 1000)
  - offset: integer (default 0)
  - sort: published_at|incident_date (default published_at)
  - order: asc|desc (default desc)

Response:
{
  "data": [
    {
      "id": 123,
      "headline": "...",
      "summary": "...",
      "sourceUrl": "...",
      "publishedAt": "2025-01-15T10:30:00Z",
      "incidentDate": "2025-01-14",
      "tags": ["corruption", "state_karnataka"],
      "severity": "high",
      "state": "Karnataka",
      "city": "Bangalore"
    }
  ],
  "pagination": {
    "total": 5432,
    "limit": 100,
    "offset": 0,
    "hasMore": true
  }
}
```

```
GET /api/v1/events/:id
Response:
{
  "id": 123,
  "headline": "...",
  "summary": "...",
  "fullText": "...",
  "sourceUrl": "...",
  "sourceName": "The Hindu",
  "publishedAt": "2025-01-15T10:30:00Z",
  "incidentDate": "2025-01-14",
  "tags": ["corruption", "state_karnataka"],
  "severity": "high",
  "state": "Karnataka",
  "city": "Bangalore",
  "entities": {
    "persons": ["John Doe", "Jane Smith"],
    "organizations": ["XYZ Corporation"]
  },
  "classification": {
    "confidence": 0.95,
    "llmModel": "gpt-4",
    "classifiedAt": "2025-01-15T11:00:00Z"
  }
}
```

#### Analytics:

```
GET /api/v1/analytics/timeseries
Query Parameters:
  - start_date, end_date: required
  - granularity: day|week|month (default day)
  - tag: specific tag (optional)
  - tags: multiple tags (optional)
  - state: filter by state
  - group_by: tag|state|severity

Response:
{
  "timeseries": [
    {
      "timestamp": "2025-01-01T00:00:00Z",
      "count": 45,
      "breakdown": {
        "murder": 12,
        "corruption": 20,
        "accidents": 13
      }
    },
    ...
  ],
  "summary": {
    "total": 1234,
    "average": 41,
    "peak": {
      "count": 89,
      "date": "2025-01-10T00:00:00Z"
    }
  }
}
```

```
GET /api/v1/analytics/geographic
Query Parameters:
  - start_date, end_date: required
  - tag: filter by tag
  - granularity: state|city

Response:
{
  "geographic": [
    {
      "state": "Uttar Pradesh",
      "count": 234,
      "breakdown": {
        "murder": 50,
        "corruption": 100,
        "accidents": 84
      }
    },
    ...
  ]
}
```

```
GET /api/v1/analytics/trending
Query Parameters:
  - timeframe: 24h|7d|30d (default 24h)
  - limit: integer (default 10)

Response:
{
  "trending": [
    {
      "tag": "corruption",
      "currentCount": 45,
      "previousCount": 20,
      "percentageChange": 125,
      "trend": "up"
    },
    ...
  ]
}
```

#### Configuration:

```
GET /api/v1/config/tags
Response:
{
  "tags": [
    {
      "id": "murder",
      "label": "Murder",
      "category": "crime",
      "color": "#ff0000",
      "enabled": true
    },
    ...
  ]
}
```

```
GET /api/v1/config/sources
Response:
{
  "sources": [
    {
      "id": 1,
      "name": "Times of India",
      "category": "national",
      "language": "english",
      "enabled": true,
      "lastFetched": "2025-01-15T12:00:00Z",
      "health": "healthy"
    },
    ...
  ]
}
```

#### Search:

```
GET /api/v1/search
Query Parameters:
  - q: search query (required, searches headlines only)
  - start_date, end_date: optional
  - tags: filter by tags
  - state: filter by state
  - limit, offset: pagination

Response:
{
  "results": [
    {
      "id": 123,
      "headline": "...",
      "summary": "...",
      "publishedAt": "...",
      "tags": ["corruption", "state_karnataka"],
      "state": "Karnataka"
    },
    ...
  ],
  "total": 234
}
```

## 8. User Interface Requirements

### 8.1 Design Theme: Pure Black Mode
- **Background:** Pure black (#000000), not grey
- **Text:** White (#FFFFFF) for maximum contrast
- **Charts:** Vibrant, saturated colors for easy readability on black
- **Purpose:** Make data visualizations pop and be highly readable

### 8.2 Dashboard Layout

#### Header:
- Logo and site title
- Date range selector (preset ranges + custom)
- Basic search bar (headline search)
- Settings icon (filter preferences)

#### Main Grid:
- Responsive grid layout (CSS Grid or Masonry)
- Tiles sized by volume/importance algorithm
- Each tile shows:
  - Category name and icon (vibrant colored)
  - Current count for selected period
  - Mini Chart.js time-series (line chart)
  - Trend indicator (up/down/stable) with colored arrow
  - Click to expand

#### Sidebar (when tile or data point clicked):
- Slides in from right
- Pure black background
- Shows detailed Chart.js time-series chart with vibrant colors
- List of headlines for selected time point (multilingual display)
- Direct links to source articles (opens in new tab)
- Filters specific to this category
- Related categories/correlations

### 8.3 Detailed Views

#### Category Detail Page:
- Large Chart.js time-series visualization (vibrant colors on black)
- Chart type selector (line, bar, area)
- Filtering panel (date, region, severity)
- Headlines list with scroll (multilingual headlines displayed)
- Geographic distribution bar chart by state
- Related tags cloud

#### Geographic View:
- Simple bar/column chart showing incident volumes by state
- Click state to filter dashboard
- Color-coded bars (vibrant colors)
- Time-series comparison between selected states

#### Search Results:
- Simple list of matching headlines
- Basic filters (date, tags, state)
- Paginated results

#### Analytics Page:
- Cross-category trend comparisons
- Simple correlation matrix (which tags appear together)
- Top states/cities bar charts
- Month-over-month comparisons

## 9. Analytics & Insights

### 9.1 Simple Analytics

The dashboard provides:

1. **Trends:**
   - Visual time-series showing categories increasing/decreasing over time
   - Simple trend indicators (up/down arrows with percentages)
   - Regional shifts visible through geographic charts

2. **Correlations:**
   - Basic correlation matrix showing which tags frequently appear together
   - State-specific patterns

3. **Comparative Analytics:**
   - State-by-state bar chart comparisons
   - Side-by-side time-series for multiple categories
   - Month-over-month percentage changes

## 10. Deployment & Infrastructure

### 10.1 Deployment Architecture

**Recommended Stack:**
- **Frontend:** Vercel or Netlify (static React app)
- **Backend API:** Railway, Render, or VPS (FastAPI with Uvicorn)
- **Database:** Railway Postgres, Supabase, or managed PostgreSQL
- **Cron Jobs:** Same server as backend or separate service

**Alternative (Self-hosted):**
- Docker Compose for development and production
- Single VPS with PostgreSQL, FastAPI, and React build
- Systemd for cron jobs or system crontab

### 10.2 Scalability Considerations

1. **Database:**
   - Connection pooling with SQLAlchemy
   - TimescaleDB for time-series optimization
   - Partitioning old data by month
   - Simple query optimization

2. **API:**
   - Uvicorn with multiple workers
   - CDN for React static assets
   - Basic rate limiting in FastAPI

3. **Cron Jobs:**
   - Run on separate schedule to avoid overlap
   - Process items in batches (e.g., 100 articles at a time)
   - Retry logic with exponential backoff for failed LLM calls

4. **LLM Costs:**
   - Batch processing to reduce API calls
   - Cache LLM responses in database
   - Use cheaper models (GPT-3.5-turbo, Claude Haiku)
   - Consider local LLM for high volume

### 10.3 Monitoring & Observability

- **Logs:** Python logging to file/stdout
- **Cron Monitoring:** Simple success/failure logs
- **Basic Metrics:** Track in database:
  - RSS fetch success rates
  - Content scraping success rates
  - LLM classification completion rates
  - API response times (FastAPI built-in)

## 11. Security & Privacy

### 11.1 Security Measures

1. **API Security:**
   - Basic rate limiting in FastAPI
   - CORS configuration for frontend domain
   - Input validation with Pydantic
   - SQL injection prevention (SQLAlchemy ORM)
   - Environment variables for secrets

2. **Data Security:**
   - HTTPS/TLS for API
   - Secure environment variable management
   - Database connection encryption

## 12. Testing Strategy

### 12.1 Basic Testing

1. **Unit Tests (Python/pytest):**
   - LLM response parsing functions
   - Text extraction utilities
   - Classification logic
   - API endpoint logic

2. **Integration Tests:**
   - RSS fetching end-to-end
   - Content scraping workflow
   - Database operations

3. **Manual Testing:**
   - Dashboard UI interactions
   - Chart rendering
   - Filter functionality

### 12.2 Data Quality

- Manual RSS feed validity checks
- Spot-check LLM classifications for accuracy
- Monitor deduplication effectiveness

## 13. Development Phases

### Phase 1: MVP (Core Infrastructure)
- [ ] PostgreSQL schema setup with TimescaleDB
- [ ] Python scripts for RSS fetching (10 major sources)
- [ ] Content scraping pipeline
- [ ] LLM classification with configurable provider
- [ ] FastAPI REST endpoints
- [ ] React dashboard with Chart.js (pure black theme)
- [ ] Basic filtering and search
- [ ] YAML configuration files
- [ ] Makefile for ops

**Estimated Timeline:** 3-4 weeks

### Phase 2: Enhanced Features
- [ ] Add 50+ RSS sources (regional coverage)
- [ ] Multiple Chart.js visualization types
- [ ] Geographic bar charts by state
- [ ] Correlation matrix
- [ ] Multi-language headline display
- [ ] Performance optimizations

**Estimated Timeline:** 2-3 weeks

### Phase 3: Polish & Production
- [ ] Mobile-responsive design
- [ ] Deployment setup
- [ ] Documentation
- [ ] Basic monitoring
- [ ] Production hardening

**Estimated Timeline:** 1-2 weeks

## 14. Configuration Files Structure

```
config/
├── rss-sources.yaml          # RSS feed definitions
├── tags.yaml                 # Tag definitions and keywords
├── llm-config.yaml           # LLM provider settings
├── dashboard-config.yaml     # Dashboard layout and preferences
├── filters.yaml              # Default filters and thresholds
└── prompts/
    ├── classification.txt    # Main classification prompt
    ├── entity-extraction.txt # Entity extraction prompt
    └── summarization.txt     # Summary generation prompt
```

## 15. Makefile for Operations

The project includes a Makefile for common operations:

```makefile
.PHONY: help install setup-db dev-api dev-frontend cron-fetch cron-scrape cron-classify test clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup
install:  ## Install Python and Node dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

setup-db:  ## Setup database schema and TimescaleDB
	cd backend && python -m scripts.setup_database

migrate:  ## Run database migrations
	cd backend && alembic upgrade head

seed-feeds:  ## Seed initial RSS sources from config
	cd backend && python -m scripts.seed_rss_sources

# Development
dev-api:  ## Run FastAPI development server
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:  ## Run React development server
	cd frontend && npm run dev

dev: ## Run both API and frontend in parallel
	make -j 2 dev-api dev-frontend

# Cron Jobs
cron-fetch:  ## Fetch RSS feeds
	cd backend && python -m scripts.fetch_rss

cron-scrape:  ## Scrape article content
	cd backend && python -m scripts.scrape_content

cron-classify:  ## Classify articles with LLM
	cd backend && python -m scripts.classify_articles

cron-all:  ## Run all cron jobs sequentially
	make cron-fetch && make cron-scrape && make cron-classify

# Testing
test:  ## Run tests
	cd backend && pytest tests/
	cd frontend && npm run test

test-coverage:  ## Run tests with coverage
	cd backend && pytest --cov=app tests/

# Database
db-shell:  ## Open PostgreSQL shell
	psql $(DATABASE_URL)

db-backup:  ## Backup database
	pg_dump $(DATABASE_URL) > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Deployment
build-frontend:  ## Build frontend for production
	cd frontend && npm run build

deploy-frontend:  ## Deploy frontend to Vercel/Netlify
	cd frontend && npm run deploy

docker-build:  ## Build Docker images
	docker-compose build

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

# Utilities
clean:  ## Clean temporary files and caches
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd frontend && rm -rf node_modules/.cache

logs:  ## Tail application logs
	tail -f backend/logs/app.log

# Crontab setup (run once on server)
install-cron:  ## Install cron jobs in crontab
	@echo "*/5 * * * * cd $(PWD) && make cron-fetch >> /var/log/newstrack/cron.log 2>&1" | crontab -
	@echo "*/10 * * * * cd $(PWD) && make cron-scrape >> /var/log/newstrack/cron.log 2>&1" | crontab -
	@echo "*/10 * * * * cd $(PWD) && make cron-classify >> /var/log/newstrack/cron.log 2>&1" | crontab -
	@echo "Cron jobs installed successfully"

remove-cron:  ## Remove cron jobs from crontab
	crontab -r
```

**Usage Examples:**

```bash
# Initial setup
make install
make setup-db
make seed-feeds

# Development
make dev              # Run both API and frontend
make dev-api          # Run only API
make dev-frontend     # Run only frontend

# Run cron jobs manually
make cron-all         # Run all jobs
make cron-fetch       # Fetch RSS feeds only

# Install as system cron
make install-cron     # Install to crontab

# Testing
make test             # Run all tests
make test-coverage    # With coverage report

# Production deployment
make build-frontend
make deploy-frontend
make docker-up
```

## 16. Future Enhancements (Phase 4+)

Potential future additions:

1. **Enhanced Visualizations:**
   - India map choropleth with Chart.js geo plugin
   - Animation between time periods
   - More chart types (radar, polar)

2. **Better Language Support:**
   - Automatic translation of headlines
   - Language-specific LLM models for better classification
   - Support for more Indian languages (Tamil, Bengali, etc.)

3. **Data Insights:**
   - Basic anomaly detection (simple statistical thresholds)
   - Email digest reports

4. **API for Researchers:**
   - Public read-only API
   - Data export in CSV/JSON

## 17. Success Metrics

Simple metrics to track:

1. **Data Coverage:**
   - Number of active RSS sources
   - News items processed per day
   - Classification accuracy (spot checks)

2. **System Performance:**
   - RSS fetch success rate (target: >90%)
   - Content scraping success rate (target: >75%)
   - LLM classification completion rate (target: >85%)
   - API response time (target: <1s)

## 18. Budget Considerations

### Estimated Monthly Costs (at scale):

1. **Infrastructure:**
   - Database: $20-100 (Railway/Supabase free tier to start)
   - API hosting: $20-50 (Railway/Render free tier to start)
   - Frontend: $0 (Vercel/Netlify free tier)
   - **Total Infrastructure: $40-150/month**

2. **LLM API Costs:**
   - Assuming 500 articles/day
   - Average 800 tokens per classification
   - Using GPT-3.5-turbo: ~$3/day = $90/month
   - Using Claude Haiku: ~$2/day = $60/month
   - Using Gemini Flash: ~$1/day = $30/month
   - **Recommendation: Start with Gemini Flash or Claude Haiku**

**Total Estimated Monthly Cost: $70-240/month**

### Cost Optimization:
- Use free tiers during MVP
- Batch LLM requests
- Cache responses in database
- Consider local LLM (Llama 3) for very high volume

## 19. Open Source Considerations

This project could be open-sourced to:
- Enable community contributions
- Increase transparency
- Allow local deployments
- Foster ecosystem of related tools

**License Recommendation:** MIT or Apache 2.0

**Repository Structure:**
```
india-news-tracker/
├── backend/                  # Python/FastAPI backend
│   ├── app/                  # FastAPI application
│   │   ├── api/              # API routes
│   │   ├── models/           # SQLAlchemy models
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI entry point
│   ├── scripts/              # Cron job scripts
│   │   ├── fetch_rss.py
│   │   ├── scrape_content.py
│   │   └── classify_articles.py
│   ├── tests/                # Pytest tests
│   ├── alembic/              # Database migrations
│   └── requirements.txt
├── frontend/                 # React dashboard
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   ├── utils/            # Utilities
│   │   └── App.tsx
│   └── package.json
├── config/                   # Configuration files (YAML)
│   ├── rss-sources.yaml
│   ├── tags.yaml
│   ├── llm-config.yaml
│   └── prompts/
├── database/                 # SQL schema files
│   └── schema.sql
├── docker-compose.yml
├── Makefile                  # Operations commands
└── README.md
```

## 20. Getting Started

### Prerequisites:
- Python 3.11+
- PostgreSQL 15+ (with TimescaleDB extension)
- Node.js 18+ (for frontend)
- LLM API key (OpenAI/Anthropic/Google)

### Quick Start:
```bash
# Clone repository
git clone https://github.com/yourusername/india-news-tracker.git
cd india-news-tracker

# Install dependencies
make install

# Set up environment
cp .env.example .env
# Edit .env with your DATABASE_URL and LLM API keys

# Setup database
make setup-db

# Seed initial RSS sources
make seed-feeds

# Start development servers (in separate terminals or use make dev)
make dev-api          # FastAPI server at http://localhost:8000
make dev-frontend     # React app at http://localhost:3000
```

### First Steps:
1. Configure RSS sources in `config/rss-sources.yaml`
2. Set up LLM API key in `.env`
3. Customize tags in `config/tags.yaml`
4. Run initial RSS fetch: `make cron-fetch`
5. Scrape content: `make cron-scrape`
6. Classify articles: `make cron-classify`
7. Open dashboard: http://localhost:3000

### Install as System Cron:
```bash
make install-cron    # Installs cron jobs to system crontab
```

---

## Conclusion

This requirements document outlines a focused, practical platform for tracking and analyzing serious news incidents across India. The system is designed to:

✅ **Aggregate** news from diverse Indian RSS sources
✅ **Classify** content using configurable LLM providers
✅ **Visualize** trends through Chart.js time-series dashboards with pure black theme
✅ **Enable** data-driven social consciousness
✅ **Keep costs low** with efficient architecture and smart LLM usage
✅ **Stay simple** with cron-based processing and minimal dependencies

**Tech Stack:**
- Backend: Python + FastAPI
- Frontend: React + Chart.js (pure black #000000 theme)
- Database: PostgreSQL + TimescaleDB
- Processing: Simple cron jobs (no complex queue system)
- Ops: Makefile for all operations

The architecture is straightforward and focused on the MVP, avoiding over-engineering while keeping everything configurable for future needs.

**Next Steps:** Begin Phase 1 development with focus on core functionality.

---

**Document Version:** 2.0 (Simplified)
**Last Updated:** 2025-11-14
**Tech Stack:** Python/FastAPI, React/Chart.js, PostgreSQL
**Status:** Ready for Implementation

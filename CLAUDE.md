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
  - Headlines for that time period
  - Direct links to source articles
  - Summary statistics
  - Related incidents
  - Tags and classifications
- **Filtering:** Filter by date range, region, severity, tags
- **Search:** Full-text search across headlines and summaries
- **Bookmarking:** Save interesting patterns or incidents
- **Sharing:** Share visualizations and filtered views

#### Additional Dashboard Features:
- **Trending Now:** Real-time feed of breaking news in tracked categories
- **Comparative Analytics:** Compare incident volumes across states/regions
- **Correlation Insights:** Identify potential correlations between categories
- **Alerts:** Notify users of unusual spikes in specific categories
- **Export Data:** Download filtered datasets for further analysis

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
    color_scheme: "severity_gradient"  # or "category_based"
    animation_enabled: true

  features:
    enable_export: true
    enable_sharing: true
    enable_alerts: true
    enable_search: true

  performance:
    data_points_limit: 1000  # per chart
    lazy_loading: true
    cache_duration: 300  # seconds
```

### 4.2 Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/newstrack
REDIS_URL=redis://localhost:6379

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Application
NODE_ENV=production
PORT=3000
LOG_LEVEL=info

# Cron Jobs
RSS_FETCH_CRON="*/5 * * * *"  # Every 5 minutes
CONTENT_PROCESS_CRON="*/10 * * * *"  # Every 10 minutes

# Security
JWT_SECRET=...
ENCRYPTION_KEY=...
```

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  - Dashboard UI                                              │
│  - Time-series Visualizations                                │
│  - Interactive Filtering                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ REST/GraphQL API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend API (Node.js/Express)              │
│  - API Endpoints                                             │
│  - Authentication & Authorization                            │
│  - Data Aggregation & Analytics                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│   Database   │ │  Redis   │ │ Task Queue  │
│ (PostgreSQL) │ │  Cache   │ │  (Bull/BQ)  │
└──────────────┘ └──────────┘ └──────┬──────┘
                                      │
                       ┌──────────────┼──────────────┐
                       │              │              │
               ┌───────▼─────┐ ┌─────▼──────┐ ┌─────▼──────┐
               │ RSS Fetcher │ │  Content   │ │    LLM     │
               │   Worker    │ │  Scraper   │ │ Classifier │
               │             │ │   Worker   │ │   Worker   │
               └─────────────┘ └────────────┘ └────────────┘
```

### 5.2 Components

#### Frontend (React):
- **Framework:** React 18+ with TypeScript
- **State Management:** Redux Toolkit or Zustand
- **Visualization:** D3.js, Recharts, or Visx
- **UI Components:** Material-UI or Tailwind CSS + Shadcn/ui
- **Routing:** React Router
- **API Client:** Axios or React Query

#### Backend API:
- **Runtime:** Node.js 20+ with TypeScript
- **Framework:** Express.js or Fastify
- **API Style:** REST + GraphQL (optional)
- **Authentication:** JWT-based
- **Validation:** Zod or Joi

#### Workers & Background Jobs:
- **Task Queue:** Bull (Redis-based) or Google Cloud Tasks
- **Cron Scheduler:** node-cron or Agenda
- **RSS Parser:** rss-parser
- **Web Scraper:** Playwright or Puppeteer
- **LLM Integration:** LangChain or direct API clients

#### Data Storage:
- **Primary Database:** PostgreSQL 15+
  - Stores news articles, classifications, metadata
  - Full-text search with pg_trgm
  - Time-series optimizations with TimescaleDB extension

- **Cache:** Redis
  - API response caching
  - Session storage
  - Rate limiting
  - Real-time data aggregation

- **Object Storage:** S3-compatible (AWS S3, MinIO, etc.)
  - Store full article HTML/text
  - Store feed configuration backups
  - Store exported datasets

#### LLM Integration:
- **Multi-provider Support:** OpenAI, Anthropic, Google, Cohere, local models
- **Prompt Management:** Version-controlled prompts
- **Fallback Strategy:** If primary LLM fails, use backup provider
- **Cost Optimization:** Cache LLM responses, batch processing

### 5.3 Data Flow

1. **RSS Ingestion:**
   - Cron triggers RSS fetcher worker every 5 minutes
   - Worker fetches all configured RSS feeds
   - Deduplicates entries against existing database
   - Stores new entries in `rss_entries` table
   - Adds entries to content processing queue

2. **Content Processing:**
   - Content scraper worker picks jobs from queue
   - Fetches full article HTML from source URL
   - Extracts clean text using readability algorithms
   - Stores raw text in database
   - Adds to LLM classification queue

3. **LLM Classification:**
   - LLM classifier worker picks jobs from queue
   - Constructs prompt with article text and tag definitions
   - Calls configured LLM API
   - Parses LLM response for tags, confidence, summary
   - Stores classifications in database
   - Updates search indices

4. **API & Frontend:**
   - Frontend requests aggregated data via API
   - API queries database with filters and time ranges
   - Results cached in Redis for common queries
   - Data transformed into visualization-ready format
   - Frontend renders interactive dashboard

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

  -- Search
  search_vector tsvector,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_events_published ON news_events(published_at DESC);
CREATE INDEX idx_news_events_incident ON news_events(incident_date DESC);
CREATE INDEX idx_news_events_primary_tag ON news_events(primary_tag);
CREATE INDEX idx_news_events_tags ON news_events USING GIN(all_tags);
CREATE INDEX idx_news_events_state ON news_events(state);
CREATE INDEX idx_news_events_search ON news_events USING GIN(search_vector);

-- Full-text search trigger
CREATE TRIGGER news_events_search_update
BEFORE INSERT OR UPDATE ON news_events
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', headline, summary);
```

#### `analytics_cache` Table:
```sql
CREATE TABLE analytics_cache (
  id SERIAL PRIMARY KEY,
  cache_key VARCHAR(255) UNIQUE NOT NULL,
  query_params JSONB,
  result_data JSONB,
  computed_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  hit_count INTEGER DEFAULT 0
);

CREATE INDEX idx_analytics_cache_key ON analytics_cache(cache_key);
CREATE INDEX idx_analytics_cache_expires ON analytics_cache(expires_at);
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
  - q: search query (required)
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
      "relevanceScore": 0.95,
      "matchedTerms": ["corruption", "scam"]
    },
    ...
  ],
  "total": 234
}
```

### 7.2 WebSocket/Real-time API

```
WS /api/v1/realtime
Events:
  - new_event: Emitted when new classified event is added
  - trending_update: Emitted when trending tags change
  - alert: Emitted for unusual spikes or patterns

Client subscribes with:
{
  "action": "subscribe",
  "channels": ["new_events", "trending"],
  "filters": {
    "tags": ["corruption"],
    "states": ["Karnataka"]
  }
}
```

## 8. User Interface Requirements

### 8.1 Dashboard Layout

#### Header:
- Logo and site title
- Date range selector (preset ranges + custom)
- Global search bar
- Settings/configuration icon
- Export data button

#### Main Grid:
- Responsive grid layout (CSS Grid or Masonry)
- Tiles sized by volume/importance algorithm
- Each tile shows:
  - Category name and icon
  - Current count for selected period
  - Sparkline or mini time-series
  - Trend indicator (up/down/stable)
  - Click to expand

#### Sidebar (when tile clicked):
- Slides in from right
- Shows detailed time-series chart
- List of headlines for selected time point
- Filters specific to this category
- Related categories/correlations
- Share/export options

### 8.2 Detailed Views

#### Category Detail Page:
- Large time-series visualization
- Multiple chart types (toggle between line, bar, area)
- Filtering panel (date, region, severity)
- Headlines list with infinite scroll
- Geographic heatmap
- Related tags cloud

#### Geographic View:
- India map visualization
- Color-coded by incident volume
- Click state for state-level breakdown
- District-level drill-down
- Time-series for selected region

#### Search Results:
- Faceted search with filters
- Relevance-ranked results
- Timeline view option
- Export search results

#### Analytics Page:
- Cross-category comparisons
- Correlation matrix
- Anomaly detection highlights
- Top states/cities rankings
- Month-over-month/year-over-year comparisons

### 8.3 User Preferences

- Save favorite views/filters
- Custom dashboard layouts
- Alert preferences
- Theme (light/dark mode)
- Accessibility options

## 9. Analytics & Insights

### 9.1 Automated Insights

The system should automatically detect and highlight:

1. **Anomalies:**
   - Unusual spikes in specific categories
   - Unexpected drops in reporting
   - Geographic clusters of incidents

2. **Trends:**
   - Categories increasing/decreasing over time
   - Seasonal patterns
   - Regional shifts

3. **Correlations:**
   - Categories that tend to spike together
   - Regional patterns (e.g., corruption correlates with X in state Y)
   - Time-based correlations (e.g., accidents peak during festival season)

4. **Comparative Analytics:**
   - State-by-state comparisons
   - Urban vs rural incident rates
   - Progress tracking (are things getting better/worse?)

### 9.2 Reporting

- Weekly email digests (configurable)
- Monthly reports with insights
- Annual summaries
- Custom report builder
- PDF export for sharing

## 10. Deployment & Infrastructure

### 10.1 Deployment Architecture

**Recommended Stack:**
- **Frontend:** Vercel or Netlify (static hosting)
- **Backend API:** Railway, Render, or AWS ECS
- **Database:** Railway Postgres, AWS RDS, or Supabase
- **Redis:** Railway, Upstash, or AWS ElastiCache
- **Workers:** Separate service on Railway/Render or AWS Lambda
- **Object Storage:** AWS S3, Cloudflare R2, or Backblaze B2

**Alternative (Self-hosted):**
- Docker Compose for development
- Kubernetes for production
- All services containerized

### 10.2 Scalability Considerations

1. **Database:**
   - Read replicas for analytics queries
   - Connection pooling (PgBouncer)
   - Partitioning old data
   - Archive to cold storage after 2 years

2. **API:**
   - Horizontal scaling with load balancer
   - Response caching with Redis
   - CDN for static assets
   - Rate limiting per user/IP

3. **Workers:**
   - Separate worker pools for different tasks
   - Auto-scaling based on queue depth
   - Retry logic with exponential backoff
   - Dead letter queue for failures

4. **LLM Costs:**
   - Batch processing to reduce API calls
   - Cache LLM responses
   - Use cheaper models for re-classification
   - Consider fine-tuned models for cost reduction

### 10.3 Monitoring & Observability

- **Application Monitoring:** Sentry or New Relic
- **Logs:** Structured logging with Winston/Pino
- **Metrics:** Prometheus + Grafana
- **Uptime:** UptimeRobot or Pingdom
- **Dashboards:** Track:
  - RSS fetch success rates
  - Content scraping success rates
  - LLM classification accuracy (sample reviews)
  - API latency and error rates
  - Database query performance
  - Queue depths and processing times

## 11. Security & Privacy

### 11.1 Security Measures

1. **API Security:**
   - Rate limiting (per IP and per user)
   - API key authentication for programmatic access
   - CORS configuration
   - Input validation and sanitization
   - SQL injection prevention (parameterized queries)
   - XSS prevention

2. **Data Security:**
   - Encryption at rest (database encryption)
   - Encryption in transit (HTTPS/TLS)
   - Secure credential storage (secrets manager)
   - Regular security audits
   - Dependency vulnerability scanning

3. **Privacy:**
   - No personal user tracking without consent
   - GDPR-compliant data handling
   - Option to exclude sensitive content (e.g., victim names)
   - Anonymization options for research exports

### 11.2 Content Moderation

- Filter extremely graphic content from summaries
- Ethical handling of sensitive cases (minors, sexual violence)
- Option for users to flag inappropriate content
- Balance between transparency and dignity

## 12. Testing Strategy

### 12.1 Automated Testing

1. **Unit Tests:**
   - LLM response parsing
   - Text extraction utilities
   - Classification logic
   - API controllers

2. **Integration Tests:**
   - RSS fetching pipeline
   - Content scraping workflow
   - LLM classification end-to-end
   - API endpoints

3. **End-to-End Tests:**
   - User flows (search, filter, view)
   - Dashboard interactions
   - Data export

### 12.2 Data Quality Tests

- RSS feed validity checks
- Classification accuracy sampling (manual review)
- Deduplication effectiveness
- Geographic extraction accuracy

### 12.3 Performance Tests

- Load testing API endpoints
- Database query performance benchmarks
- Frontend rendering with large datasets
- Worker throughput testing

## 13. Development Phases

### Phase 1: MVP (Core Infrastructure)
- [ ] Basic RSS feed fetching for 10 major sources
- [ ] PostgreSQL schema and data models
- [ ] Content scraping pipeline
- [ ] LLM classification with OpenAI
- [ ] Basic REST API
- [ ] Simple React dashboard with one chart type
- [ ] Manual configuration (JSON files)

**Estimated Timeline:** 4-6 weeks

### Phase 2: Enhanced Features
- [ ] Add 50+ RSS sources (regional coverage)
- [ ] Multi-LLM provider support
- [ ] Advanced filtering and search
- [ ] Multiple visualization types
- [ ] Geographic visualizations
- [ ] Configuration UI
- [ ] Export functionality

**Estimated Timeline:** 4-6 weeks

### Phase 3: Analytics & Insights
- [ ] Automated anomaly detection
- [ ] Trend analysis
- [ ] Correlation insights
- [ ] Comparative analytics
- [ ] Email reports
- [ ] Alert system

**Estimated Timeline:** 3-4 weeks

### Phase 4: Polish & Scale
- [ ] Performance optimizations
- [ ] Advanced caching strategies
- [ ] Mobile-responsive design
- [ ] Accessibility improvements
- [ ] Documentation
- [ ] Deployment automation
- [ ] Monitoring dashboards

**Estimated Timeline:** 2-3 weeks

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

## 15. Future Enhancements

### Phase 5+ Ideas:

1. **Advanced NLP:**
   - Sentiment analysis
   - Entity relationship extraction
   - Event timeline reconstruction
   - Fact-checking integration

2. **Social Features:**
   - User accounts and profiles
   - Community annotations/corrections
   - Discussion forums for incidents
   - Crowdsourced verification

3. **Data Partnerships:**
   - Share anonymized data with researchers
   - Partner with NGOs for impact tracking
   - Government transparency integrations
   - RTI (Right to Information) correlation

4. **Mobile App:**
   - Native iOS/Android apps
   - Push notifications for alerts
   - Offline reading

5. **AI Enhancements:**
   - Predictive analytics (forecasting trends)
   - Root cause analysis
   - Policy recommendation engine
   - Automated report generation

6. **Multilingual:**
   - Support for Hindi, Tamil, Bengali, etc.
   - Automatic translation
   - Language-specific LLM models

7. **Media Analysis:**
   - Image/video analysis from news
   - Verify authenticity of media
   - Extract text from images (OCR)

8. **API for Developers:**
   - Public API for researchers
   - GraphQL endpoint
   - Webhooks for real-time data
   - SDKs in multiple languages

## 16. Success Metrics

### Key Performance Indicators (KPIs):

1. **Data Coverage:**
   - Number of active RSS sources
   - Geographic coverage (% of states/cities)
   - News items processed per day
   - Classification accuracy (measured via sampling)

2. **System Performance:**
   - RSS fetch success rate (target: >95%)
   - Content scraping success rate (target: >80%)
   - LLM classification completion rate (target: >90%)
   - Average time from publication to classification (target: <1 hour)
   - API response time (target: <500ms p95)

3. **User Engagement:**
   - Daily active users
   - Average session duration
   - Most viewed categories
   - Search queries per session
   - Data export frequency

4. **Social Impact:**
   - Media mentions
   - Research citations
   - Policy discussions influenced
   - Public awareness campaigns using the data

## 17. Budget Considerations

### Estimated Monthly Costs (at scale):

1. **Infrastructure:**
   - Database: $50-200 (Railway/Supabase)
   - API hosting: $50-150 (Railway/Render)
   - Redis: $20-50
   - Object storage: $10-30
   - CDN: $10-30
   - **Total Infrastructure: $140-460/month**

2. **LLM API Costs:**
   - Assuming 1000 articles/day
   - Average 1000 tokens per classification
   - Using GPT-4: ~$30/day = $900/month
   - Using GPT-3.5-turbo: ~$6/day = $180/month
   - Using Claude Haiku: ~$3/day = $90/month
   - **Recommendation: Start with cheaper models, optimize later**

3. **Monitoring & Tools:**
   - Sentry: $0-50
   - Monitoring: $0-50
   - **Total: $0-100/month**

**Total Estimated Monthly Cost: $320-1460/month** (depending on LLM choice)

### Cost Optimization Strategies:
- Use cheaper LLM models for initial classification
- Batch processing to reduce API calls
- Aggressive caching
- Consider self-hosted LLM for high volume (Llama 3, etc.)
- Use free tiers where possible during MVP

## 18. Open Source Considerations

This project could be open-sourced to:
- Enable community contributions
- Increase transparency
- Allow local deployments
- Foster ecosystem of related tools

**License Recommendation:** MIT or Apache 2.0

**Repository Structure:**
```
india-news-tracker/
├── backend/           # Node.js API and workers
├── frontend/          # React dashboard
├── config/            # Configuration templates
├── database/          # Schema and migrations
├── docs/              # Documentation
├── scripts/           # Deployment and utility scripts
└── README.md
```

## 19. Ethical Considerations

1. **Responsible Reporting:**
   - Avoid sensationalism
   - Respect victim privacy
   - Provide context, not just stats
   - Avoid reinforcing stereotypes

2. **Accuracy:**
   - Acknowledge LLM classification is not perfect
   - Provide confidence scores
   - Allow corrections/feedback
   - Regular manual audits

3. **Bias Mitigation:**
   - Monitor for source bias
   - Ensure geographic representation
   - Avoid over-focusing on certain types of crime
   - Regular bias audits of classifications

4. **Impact:**
   - Partner with social organizations
   - Provide actionable insights, not just data
   - Consider emotional impact on users
   - Offer resources for those affected by issues

## 20. Getting Started

### Prerequisites:
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- LLM API key (OpenAI/Anthropic/etc.)

### Quick Start:
```bash
# Clone repository
git clone https://github.com/yourusername/india-news-tracker.git
cd india-news-tracker

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
npm run db:migrate

# Seed initial RSS sources
npm run db:seed

# Start development servers
npm run dev:backend   # API server
npm run dev:frontend  # React app
npm run dev:workers   # Background workers
```

### First Steps:
1. Configure RSS sources in `config/rss-sources.yaml`
2. Set up LLM API key in `.env`
3. Customize tags in `config/tags.yaml`
4. Run initial RSS fetch: `npm run worker:fetch-rss`
5. Monitor classifications: `npm run worker:classify`
6. Open dashboard: http://localhost:3000

---

## Conclusion

This comprehensive requirements document outlines a robust, scalable, and ethically-minded platform for tracking and analyzing serious news incidents across India. The system is designed to:

✅ **Aggregate** news from diverse sources
✅ **Classify** content using configurable LLM technology
✅ **Visualize** trends through interactive time-series dashboards
✅ **Enable** data-driven social consciousness
✅ **Scale** to handle growing data volumes
✅ **Respect** privacy and ethical considerations

The modular architecture allows for incremental development, starting with an MVP and progressively adding advanced features. Every component is configurable to adapt to changing needs, sources, and technologies.

**Next Steps:** Review this document, refine requirements based on feedback, and begin Phase 1 development.

---

**Document Version:** 1.0
**Last Updated:** 2025-01-14
**Author:** Claude
**Status:** Draft - Awaiting Review

# India News Tracker

Building Data-Driven Social Consciousness Through Time-Series News Analysis

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- At least one LLM API key (Google/OpenAI/Anthropic)

### Backend Setup

1. **Clone and navigate to the project:**
   ```bash
   cd madarchod
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your LLM API key (at least GOOGLE_API_KEY)
   ```

3. **Start backend services (PostgreSQL + FastAPI):**
   ```bash
   make dev
   ```

4. **In another terminal, run the processing pipeline:**
   ```bash
   make cron-fetch      # Fetch RSS feeds
   make cron-scrape     # Scrape article content
   make cron-classify   # Classify with LLM
   ```

5. **Check the API:**
   ```bash
   curl http://localhost:8000
   curl http://localhost:8000/api/v1/events
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open dashboard:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📚 Project Structure

```
.
├── backend/                 # Python/FastAPI backend
│   ├── app/                # FastAPI application
│   │   ├── api/           # API routes
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Business logic
│   │   ├── config.py      # Configuration loader
│   │   ├── database.py    # Database connection
│   │   └── main.py        # FastAPI entry point
│   ├── scripts/           # Cron job scripts
│   │   ├── fetch_rss.py   # RSS fetcher ✅
│   │   ├── scrape_content.py  # (TODO)
│   │   └── classify_articles.py  # (TODO)
│   ├── tests/             # Tests
│   └── requirements.txt   # Python dependencies
├── config/                # Configuration (YAML)
│   ├── rss-sources.yaml   # 100+ RSS feeds ✅
│   ├── tags.yaml          # 60+ tags ✅
│   ├── llm-config.yaml    # LLM config ✅
│   ├── dashboard-config.yaml
│   ├── filters.yaml
│   └── prompts/
│       ├── classification.txt
│       └── entity-extraction.txt
├── database/              # Database schema
│   └── schema.sql         # PostgreSQL schema ✅
├── docker-compose.yml     # Docker services ✅
├── Makefile              # Ops commands ✅
└── CLAUDE.md             # Requirements doc
```

## 🛠️ Makefile Commands

### Development
```bash
make dev              # Start all services (API + DB)
make dev-db           # Start only database
make dev-api          # Start only API
make dev-down         # Stop all services
make logs             # View API logs
make logs-db          # View database logs
```

### RSS Operations
```bash
make cron-fetch       # Fetch RSS feeds (100+ sources)
make cron-scrape      # Scrape article content (TODO)
make cron-classify    # Classify with LLM (TODO)
make cron-all         # Run all cron jobs
```

### Database
```bash
make db-shell         # Open PostgreSQL shell
make db-backup        # Backup database
```

### Docker
```bash
make docker-build     # Build images
make docker-up        # Start containers
make docker-down      # Stop containers
make docker-clean     # Remove all containers/volumes
make docker-logs      # View all logs
```

### Utilities
```bash
make help             # Show all commands
make clean            # Clean temp files
make test             # Run tests
make quickstart       # Show quick start guide
```

## 🗄️ Database

The project uses **PostgreSQL 15** with **TimescaleDB** extension for time-series optimization.

### Tables
- `rss_sources` - RSS feed sources
- `rss_entries` - Fetched RSS entries
- `articles` - Scraped article content
- `classifications` - LLM classifications
- `news_events` - Denormalized view for fast queries (TimescaleDB hypertable)
- `processing_logs` - Job execution logs

### Access Database
```bash
# Via psql
make db-shell

# Via pgAdmin (optional, start with --profile dev)
docker-compose --profile dev up
# Open http://localhost:5050
# Email: admin@newstrack.local
# Password: admin
```

## 🔧 Configuration

All configuration is in YAML files under `config/`:

- **rss-sources.yaml**: 100+ Indian RSS feeds (national, regional, Hindi, regional languages)
- **tags.yaml**: 60+ classification tags with Hindi keywords and vibrant colors
- **llm-config.yaml**: Multi-provider LLM config (Google, OpenAI, Anthropic, Cohere, Local)
- **filters.yaml**: Content filtering, deduplication, quality checks
- **dashboard-config.yaml**: Pure black theme, Chart.js settings
- **prompts/**: LLM prompt templates

## 🎨 Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15 + TimescaleDB
- **RSS Parsing**: feedparser
- **Web Scraping**: BeautifulSoup4 + requests
- **LLM**: Multi-provider (Google Gemini Flash recommended)
- **Containerization**: Docker + Docker Compose

## 📊 Current Status

### ✅ Completed
- [x] Docker setup with PostgreSQL + TimescaleDB
- [x] Database schema with time-series optimization
- [x] Configuration system (YAML-based)
- [x] 100+ RSS sources (national, regional, Hindi, languages)
- [x] 60+ classification tags with keywords
- [x] RSS fetcher script (fetches and stores RSS entries)
- [x] SQLAlchemy models
- [x] Basic FastAPI app
- [x] Makefile for ops

### 🚧 In Progress / TODO
- [ ] Article content scraper
- [ ] LLM classification pipeline
- [ ] FastAPI REST endpoints
- [ ] React + Chart.js dashboard
- [ ] Frontend (pure black theme #000000)

## 🔑 Environment Variables

Required in `.env`:

```bash
# Database (already configured for Docker)
DATABASE_URL=postgresql://newstrack:newstrack_dev_password@db:5432/newstrack

# At least one LLM API key
GOOGLE_API_KEY=your_key_here          # Recommended (cheapest)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Application
ENVIRONMENT=development
PORT=8000
LOG_LEVEL=info
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Test RSS fetcher
make cron-fetch
# Check logs
make logs
# Check database
make db-shell
# SELECT COUNT(*) FROM rss_entries;
```

## 📝 Notes

- The RSS fetcher automatically seeds RSS sources from `config/rss-sources.yaml` on first run
- Deduplication is handled via `guid` (unique index) and `content_hash`
- TimescaleDB hypertable is created on `news_events` for efficient time-series queries
- All dates are stored in UTC

## 🤝 Contributing

This is a focused MVP. See `CLAUDE.md` for full requirements and roadmap.

## 📄 License

TBD (Recommend: MIT or Apache 2.0)

---

**Built with ❤️ for data-driven social consciousness**

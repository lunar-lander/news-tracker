.PHONY: help install setup-db dev-api dev-db dev-frontend dev dev-down cron-fetch cron-scrape cron-classify test clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup
install:  ## Install Python and Node dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

setup-db:  ## Setup database with Docker
	docker-compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Database is ready!"

# Development
dev-api:  ## Run FastAPI development server
	docker-compose up api

dev-db:  ## Start only the database
	docker-compose up -d db

dev-frontend:  ## Run React frontend development server
	cd frontend && npm run dev

dev:  ## Run all services (API + DB)
	docker-compose up

dev-down:  ## Stop all services
	docker-compose down

# Docker operations
docker-build:  ## Build Docker images
	docker-compose build

docker-up:  ## Start all containers
	docker-compose up -d

docker-down:  ## Stop all containers
	docker-compose down

docker-logs:  ## Tail Docker logs
	docker-compose logs -f

docker-clean:  ## Remove all containers and volumes
	docker-compose down -v

# Cron Jobs (run inside Docker or locally)
cron-fetch:  ## Fetch RSS feeds
	docker-compose exec api python -m scripts.fetch_rss

cron-scrape:  ## Scrape article content
	docker-compose exec api python -m scripts.scrape_content

cron-classify:  ## Classify articles with LLM
	docker-compose exec api python -m scripts.classify_articles

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
	docker-compose exec db psql -U newstrack -d newstrack

db-backup:  ## Backup database
	docker-compose exec db pg_dump -U newstrack newstrack > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:  ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	docker-compose exec -T db psql -U newstrack newstrack < $(FILE)

# Utilities
clean:  ## Clean temporary files and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf node_modules/.cache dist 2>/dev/null || true

logs:  ## Tail application logs
	docker-compose logs -f api

logs-db:  ## Tail database logs
	docker-compose logs -f db

# Quick start
quickstart:  ## Quick start guide
	@echo "===================================="
	@echo "India News Tracker - Quick Start"
	@echo "===================================="
	@echo ""
	@echo "1. Copy .env.example to .env and fill in your API keys:"
	@echo "   cp .env.example .env"
	@echo ""
	@echo "2. Start the database and API:"
	@echo "   make dev"
	@echo ""
	@echo "3. In another terminal, start the frontend:"
	@echo "   make dev-frontend"
	@echo ""
	@echo "4. In another terminal, run RSS processing:"
	@echo "   make cron-fetch    # Fetch RSS feeds"
	@echo "   make cron-scrape   # Scrape content"
	@echo "   make cron-classify # Classify with LLM"
	@echo ""
	@echo "5. Access the application:"
	@echo "   Frontend:   http://localhost:5173"
	@echo "   Backend:    http://localhost:8000"
	@echo "   API Docs:   http://localhost:8000/docs"
	@echo ""
	@echo "For more commands, run: make help"
	@echo ""

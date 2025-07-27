# GenSpark Board Backend - Development Makefile

.PHONY: help install test test-unit test-integration test-e2e test-all test-coverage test-performance clean lint format security dev-setup

# Default target
help:
	@echo "GenSpark Board Backend - Available Commands:"
	@echo ""
	@echo "Setup & Development:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev-setup     - Setup development environment"
	@echo "  make dev           - Start development server"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run smart test selection"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-e2e      - Run E2E tests"
	@echo "  make test-all      - Run all tests"
	@echo "  make test-coverage - Run tests with coverage"
	@echo "  make test-performance - Run performance tests"
	@echo "  make test-security - Run security scans"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean temporary files"

# Installation and setup
install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

dev-setup: install
	pre-commit install
	alembic upgrade head

# Development server
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Testing commands
test:
	@echo "🧠 Running smart test selection..."
	python scripts/test_runner.py auto

test-unit:
	@echo "🧪 Running unit tests..."
	python run_tests.py unit

test-integration:
	@echo "🔗 Running integration tests..."
	python run_tests.py integration

test-e2e:
	@echo "🌐 Running E2E tests..."
	python run_tests.py e2e

test-all:
	@echo "🚀 Running all tests..."
	python run_tests.py all

test-coverage:
	@echo "📊 Running tests with coverage..."
	python run_tests.py all --coverage
	@echo "Coverage report: htmlcov/index.html"

test-performance:
	@echo "⚡ Running performance tests..."
	python scripts/test_runner.py performance

test-security:
	@echo "🔒 Running security scans..."
	python scripts/test_runner.py unit --security

# Fast development testing
test-fast:
	@echo "⚡ Running fast tests..."
	python run_tests.py unit --fast

test-changed:
	@echo "🎯 Running tests for changed files..."
	python scripts/test_runner.py --changed-only

# Code quality
lint:
	@echo "🔍 Running code linting..."
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	@echo "✨ Formatting code..."
	black app/ tests/
	isort app/ tests/

type-check:
	@echo "🔍 Running type checks..."
	mypy app/ --ignore-missing-imports

# Database operations
db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-reset:
	alembic downgrade base
	alembic upgrade head

# Docker operations
docker-test:
	@echo "🐳 Running tests in Docker..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

docker-test-cleanup:
	docker-compose -f docker-compose.test.yml down -v

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -exec rm -rf {} +
	find . -name "*.db" -delete
	find . -name "test-results.json" -delete
	find . -name "benchmark-results.json" -delete

# Production deployment helpers
build:
	@echo "🔨 Building application..."
	docker build -t genspark-board-backend .

# CI/CD helpers
ci-test:
	@echo "🤖 Running CI test suite..."
	python scripts/test_runner.py all --security --no-coverage

ci-quick:
	@echo "⚡ Running CI quick checks..."
	python scripts/test_runner.py unit --fast

# Health checks
health-check:
	@echo "🏥 Running health checks..."
	python -c "import app.main; print('✅ Application imports successfully')"
	python -c "from app.database.session import get_db; print('✅ Database connection works')"

# Show project info
info:
	@echo "📋 Project Information:"
	@echo "  Python version: $(shell python --version)"
	@echo "  Pip packages: $(shell pip list | wc -l) installed"
	@echo "  Test files: $(shell find tests -name '*.py' | wc -l) files"
	@echo "  Source files: $(shell find app -name '*.py' | wc -l) files"
	@echo "  Last commit: $(shell git log -1 --pretty=format:'%h - %s (%cr)')"
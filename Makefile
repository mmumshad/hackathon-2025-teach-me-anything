# 🐳 Docker Management Makefile
# Easy commands to manage your Docker stack

.PHONY: help build up down logs clean restart status

# Default target
help:
	@echo "🐳 Teach Me Anything - Docker Commands"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs for all services"
	@echo "  make logs-backend - Show backend logs"
	@echo "  make logs-frontend - Show frontend logs"
	@echo "  make status    - Show service status"
	@echo "  make clean     - Clean up Docker resources"
	@echo "  make dev       - Start in development mode"
	@echo "  make prod      - Start in production mode"
	@echo ""

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker compose build

# Start all services
up:
	@echo "🚀 Starting all services..."
	docker compose up -d

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker compose down

# Restart all services
restart: down up

# Show logs
logs:
	@echo "📋 Showing logs..."
	docker compose logs -f

# Show backend logs
logs-backend:
	@echo "📋 Showing backend logs..."
	docker compose logs -f backend

# Show frontend logs
logs-frontend:
	@echo "📋 Showing frontend logs..."
	docker compose logs -f frontend

# Show service status
status:
	@echo "📊 Service Status:"
	docker compose ps

# Clean up Docker resources
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker compose down -v
	docker system prune -f

# Development mode (with rebuild)
dev:
	@echo "🛠️ Starting in development mode..."
	docker compose up --build

# Production mode
prod:
	@echo "🚀 Starting in production mode..."
	docker compose up -d

# Quick health check
health:
	@echo "🏥 Checking service health..."
	@echo "Backend:"
	@curl -s http://localhost:8000/health || echo "❌ Backend not responding"
	@echo "Frontend:"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend responding" || echo "❌ Frontend not responding"

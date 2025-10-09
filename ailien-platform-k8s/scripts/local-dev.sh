#!/bin/bash
# Ailien Platform - Local Development Setup

set -e

echo "🚀 Ailien Platform - Local Development Setup"
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "📦 Building Docker image..."
docker-compose build

echo "🔄 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    echo "📋 Container logs:"
    docker-compose logs ailien-platform
    exit 1
fi

echo ""
echo "🎉 Local development environment is ready!"
echo "📱 Application: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "  docker-compose logs -f ailien-platform  # View logs"
echo "  docker-compose down                     # Stop services"
echo "  docker-compose restart                  # Restart services"
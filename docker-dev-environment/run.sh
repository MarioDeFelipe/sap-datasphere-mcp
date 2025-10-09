#!/bin/bash

# SAP Datasphere Control Panel - Docker Development Runner
# This script helps you quickly start the development environment

echo "🐳 SAP Datasphere Control Panel - Docker Development Environment"
echo "================================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Docker Compose is available"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the development environment"
    echo "  stop      Stop the development environment"
    echo "  restart   Restart the development environment"
    echo "  logs      Show application logs"
    echo "  shell     Access the application container shell"
    echo "  clean     Stop and remove all containers and volumes"
    echo "  build     Rebuild the containers"
    echo "  status    Show container status"
    echo ""
}

# Parse command line arguments
case "${1:-start}" in
    "start")
        echo "🚀 Starting SAP Datasphere development environment..."
        docker-compose up -d --build
        echo ""
        echo "✅ Environment started successfully!"
        echo ""
        echo "🌐 Access your application:"
        echo "   Web Interface: http://localhost:8000"
        echo "   API Endpoint:  http://localhost:8000/api/hello"
        echo "   Health Check:  http://localhost:8000/health"
        echo ""
        echo "📊 View logs: ./run.sh logs"
        echo "🐚 Access shell: ./run.sh shell"
        ;;
    
    "stop")
        echo "🛑 Stopping SAP Datasphere development environment..."
        docker-compose down
        echo "✅ Environment stopped successfully!"
        ;;
    
    "restart")
        echo "🔄 Restarting SAP Datasphere development environment..."
        docker-compose down
        docker-compose up -d --build
        echo "✅ Environment restarted successfully!"
        ;;
    
    "logs")
        echo "📋 Showing application logs (Press Ctrl+C to exit)..."
        docker-compose logs -f sap-datasphere-app
        ;;
    
    "shell")
        echo "🐚 Accessing application container shell..."
        docker-compose exec sap-datasphere-app bash
        ;;
    
    "clean")
        echo "🧹 Cleaning up all containers and volumes..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup completed!"
        ;;
    
    "build")
        echo "🔨 Rebuilding containers..."
        docker-compose build --no-cache
        echo "✅ Build completed!"
        ;;
    
    "status")
        echo "📊 Container Status:"
        docker-compose ps
        echo ""
        echo "🔍 Docker System Info:"
        docker system df
        ;;
    
    "help"|"-h"|"--help")
        show_usage
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
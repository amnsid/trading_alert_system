#!/bin/bash
# Deployment script for Trading Alert System

echo "🚀 Trading Alert System Deployment"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your credentials"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed!"
    echo "Please install Docker first"
    exit 1
fi

# Build and run with Docker Compose
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting Trading Alert System..."
docker-compose up -d

echo "📊 Checking system status..."
sleep 10
docker-compose ps

echo "📋 View logs with:"
echo "docker-compose logs -f"

echo "🛑 Stop system with:"
echo "docker-compose down"

echo "✅ Deployment complete!"

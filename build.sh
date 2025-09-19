#!/bin/bash

# Build Docker image
echo "Building Docker image trinhlk2:n8n-crawling..."
docker build -t trinhlk2:n8n-crawling .

# Start services
echo "Starting services..."
docker-compose up -d

echo "Services started!"
echo "n8n: http://localhost:5678"
echo "PostgreSQL: localhost:5432"
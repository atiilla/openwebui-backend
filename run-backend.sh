#!/bin/bash

# Generate a random secret key if not provided
if [ -z "$WEBUI_SECRET_KEY" ]; then
    WEBUI_SECRET_KEY=$(openssl rand -base64 32)
    echo "Generated random WEBUI_SECRET_KEY: $WEBUI_SECRET_KEY"
    
    # Update the docker-compose file
    sed -i "s/your_secret_key_here/$WEBUI_SECRET_KEY/g" docker-compose.yaml
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start the containers
echo "Building and starting Open WebUI Backend..."
docker-compose up -d --build

echo ""
echo "Open WebUI Backend is now running!"
echo "Backend API available at: http://localhost:8080"
echo ""
echo "To stop the backend: docker-compose down"
echo "To view logs: docker-compose logs -f" 
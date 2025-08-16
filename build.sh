# build.sh - Build script for the application
#!/bin/bash

echo "🚀 Building MultiChat Application..."

# Create necessary directories
mkdir -p templates static/js src/components

# Build React frontend
echo "📦 Installing dependencies..."
npm install

echo "🔨 Building React components..."
npm run build

echo "🐳 Building Docker image..."
docker build -t multichat-app .

echo "✅ Build complete! Run with: docker-compose up"

# start.sh - Development start script
#!/bin/bash

echo "🚀 Starting MultiChat in development mode..."

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Build frontend
npm run build

# Start Flask app
export FLASK_ENV=development
python app.py

# deploy.sh - Production deployment script
#!/bin/bash

echo "🚀 Deploying MultiChat to production..."

# Pull latest code
git pull origin main

# Build and start with docker-compose
docker-compose down
docker-compose build
docker-compose up -d

echo "✅ Deployment complete!"
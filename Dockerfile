# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for building React frontend
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json for frontend dependencies
COPY package.json ./
RUN npm install

# Copy application files
COPY . .

# Build React frontend
RUN npm run build

# Expose port
EXPOSE 3044

# Run the application
CMD ["python", "app.py"]


# webpack.config.js

#!/bin/bash

# Docker Entrypoint Script
# This script runs data collection and vector database setup on container start

set -e

echo "Starting Study Abroad AI Assistant..."

check_data_exists() {
    # Check if any scraped data exists
    if ls data/czech_integrated_data_*.json 1> /dev/null 2>&1; then
        echo "Scraped data already exists, skipping scraping..."
        return 0
    else
        echo "No existing scraped data found, will scrape..."
        return 1
    fi
}

check_vector_db() {
    if [ -d "data/vector_db" ] && [ "$(ls -A data/vector_db)" ]; then
        echo "Vector database already exists, skipping loading..."
        return 0
    else
        echo "No existing vector database found, will load data..."
        return 1
    fi
}

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Step 1: Run scraping if needed
if ! check_data_exists; then
    echo "Running Czech scholarship scraper..."
    python scripts/scrape_czech.py
    echo "Scraping completed!"
else
    echo "Using existing scraped data"
fi

# Step 2: Load data into vector database if needed
if ! check_vector_db; then
    echo "Loading data into vector database..."
    python scripts/load_to_vector_db.py --all
    echo "Vector database loading completed!"
else
    echo "Using existing vector database"
fi

# Step 3: Show vector database statistics
echo "Vector Database Statistics:"
python scripts/load_to_vector_db.py --stats

# Step 4: Execute the CMD (uvicorn)
echo "Starting FastAPI server..."
exec "$@"


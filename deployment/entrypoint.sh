#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis is ready!"

# Run database migrations if needed
echo "Running database setup..."
python -c "
from sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
analyzer.setup_database()
print('Database setup completed')
"

# Start the application
echo "Starting K-Pop Sentiment Analyzer..."
exec "$@"
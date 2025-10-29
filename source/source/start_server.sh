#!/bin/bash
# AuroraMart Server Startup Script

echo "🚀 Starting AuroraMart Server..."
echo "================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if migrations are up to date
echo "Checking migrations..."
python3 manage.py migrate

# Start the server
echo ""
echo "Starting Django development server..."
echo "Server will be available at: http://127.0.0.1:8000/"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

python3 manage.py runserver


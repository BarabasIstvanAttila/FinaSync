#!/bin/bash
if [ -f .env ]; then
    # Loads the variables nicely, handling quotes and special chars
    export $(cat .env | xargs)
    echo "API key loaded from .env file"
else
    echo "Error: .env file not found"
    exit 1
fi

echo "Running agents..."
python src/main.py
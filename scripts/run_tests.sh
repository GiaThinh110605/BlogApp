#!/bin/bash
# scripts/run_tests.sh
echo "Running tests..."
pytest --cov=app --cov-report=html

echo "Starting development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

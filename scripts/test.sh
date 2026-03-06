#!/bin/bash
# Test script for OrchestRAI

set -e

echo "🧪 OrchestRAI Test Suite"
echo "========================"
echo ""

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Run tests
echo "🔬 Running unit tests..."
pytest tests/ -v --tb=short

echo ""
echo "✅ All tests passed!"
echo ""

# Optional: Run with coverage
if [ "$1" == "--coverage" ]; then
    echo "📊 Running tests with coverage..."
    pytest tests/ --cov=lambdas --cov=shared --cov-report=html --cov-report=term
    echo ""
    echo "📈 Coverage report generated in htmlcov/index.html"
fi

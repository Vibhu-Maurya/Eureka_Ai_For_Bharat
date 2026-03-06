#!/bin/bash
# Quick local test script for OrchestRAI

set -e

echo "========================================"
echo "OrchestRAI Local Test Script"
echo "========================================"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi
echo "[OK] Python found: $(python3 --version)"

# Check pip
echo "Checking pip..."
if ! command -v pip &> /dev/null; then
    echo "[ERROR] pip is not installed"
    exit 1
fi
echo "[OK] pip found"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "[OK] Dependencies installed"

# Run unit tests
echo ""
echo "========================================"
echo "Running Unit Tests"
echo "========================================"
echo ""

pytest tests/ -v

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "[SUCCESS] All tests passed!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Deploy to AWS: cd infrastructure && cdk deploy --all"
    echo "2. Test API: python examples/test_upload.py <API_URL> <API_KEY>"
    echo "3. Monitor: Check AWS Console for Step Functions and CloudWatch"
    echo ""
    echo "See TESTING_GUIDE.md for detailed instructions"
    echo ""
else
    echo ""
    echo "[FAILED] Some tests failed"
    exit 1
fi

#!/bin/bash
# Cleanup script for OrchestRAI

set -e

echo "🧹 OrchestRAI Cleanup Script"
echo "============================"
echo ""

echo "⚠️  WARNING: This will delete all OrchestRAI resources including:"
echo "   - S3 buckets and all stored content"
echo "   - DynamoDB tables and all data"
echo "   - Lambda functions"
echo "   - Step Functions state machines"
echo "   - API Gateway"
echo ""

read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "🗑️  Destroying infrastructure..."
cd infrastructure
cdk destroy --all --force

echo ""
echo "✅ Cleanup complete!"
echo ""

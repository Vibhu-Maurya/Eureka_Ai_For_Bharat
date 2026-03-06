#!/bin/bash
# Deployment script for OrchestRAI

set -e

echo "🚀 OrchestRAI Deployment Script"
echo "================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    exit 1
fi

if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Install with: npm install -g aws-cdk"
    exit 1
fi

echo "✅ All prerequisites met"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
cd infrastructure
pip install -r requirements.txt
cd ..
echo "✅ Dependencies installed"
echo ""

# Bootstrap CDK (if needed)
echo "🔧 Checking CDK bootstrap..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
    echo "Bootstrapping CDK..."
    cd infrastructure
    cdk bootstrap
    cd ..
    echo "✅ CDK bootstrapped"
else
    echo "✅ CDK already bootstrapped"
fi
echo ""

# Deploy infrastructure
echo "🏗️  Deploying infrastructure..."
cd infrastructure

echo "Synthesizing CloudFormation templates..."
cdk synth

echo "Deploying stacks..."
cdk deploy --all --require-approval never

echo "✅ Infrastructure deployed"
echo ""

# Get outputs
echo "📊 Deployment Outputs:"
echo "====================="
aws cloudformation describe-stacks \
    --stack-name OrchestRAIApiStack \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Get your API key from AWS Console → API Gateway → API Keys"
echo "2. Test the API using the examples in DEPLOYMENT.md"
echo "3. Monitor workflows in Step Functions console"
echo ""

# OrchestRAI Quick Start Guide

Get your OrchestRAI prototype up and running in 15 minutes!

## 🎯 What You'll Build

A working AI video orchestration engine that:
- Accepts video/text uploads via REST API
- Extracts transcripts using Amazon Transcribe
- Generates engaging scripts using Amazon Bedrock
- Evaluates quality with AI critic
- Iteratively refines content until quality threshold is met

## 📋 Prerequisites (5 minutes)

1. **AWS Account** - [Sign up here](https://aws.amazon.com/)
2. **AWS CLI** - [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. **Python 3.11+** - [Download here](https://www.python.org/downloads/)
4. **Node.js 18+** - [Download here](https://nodejs.org/)

## 🚀 Installation (5 minutes)

### Step 1: Clone and Setup

```bash
# Navigate to your project directory
cd orchestrai

# Install Python dependencies
pip install -r requirements.txt

# Install AWS CDK
npm install -g aws-cdk

# Install CDK dependencies
cd infrastructure
pip install -r requirements.txt
cd ..
```

### Step 2: Configure AWS

```bash
# Configure AWS credentials
aws configure

# Enter your credentials when prompted:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1 (recommended)
# - Default output format: json
```

### Step 3: Enable Bedrock Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in the left menu
3. Click "Manage model access"
4. Enable "Claude 3 Sonnet"
5. Click "Save changes"

## 🏗️ Deploy (3 minutes)

### Option A: Automated Deployment

```bash
# Make script executable (Linux/Mac)
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### Option B: Manual Deployment

```bash
cd infrastructure

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks
cdk deploy --all
```

## 🧪 Test Your API (2 minutes)

### Get Your API Details

```bash
# Get API URL
aws cloudformation describe-stacks \
  --stack-name OrchestRAIApiStack \
  --query 'Stacks[0].Outputs' \
  --output table
```

### Get API Key

1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway/)
2. Click "API Keys" in left menu
3. Click on your API key
4. Click "Show" to reveal the key

### Run Test Script

```bash
cd examples
python test_upload.py <YOUR_API_URL> <YOUR_API_KEY>
```

Example:
```bash
python test_upload.py https://abc123.execute-api.us-east-1.amazonaws.com/prod abc123xyz789
```

## 📊 Monitor Your Workflow

### View Step Functions Execution

1. Go to [Step Functions Console](https://console.aws.amazon.com/states/)
2. Click "VideoGenerationWorkflow"
3. See your workflow execution in real-time!

### View CloudWatch Logs

1. Go to [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
2. Click "Log groups"
3. Look for `/aws/lambda/OrchestRAI-*`

### View DynamoDB Data

1. Go to [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Click "Tables"
3. Select "OrchestRAI-ContentMetadata"
4. Click "Explore table items"

## 🎉 Success Indicators

You'll know it's working when you see:

✅ API returns 200 status with workflowId  
✅ Step Functions execution starts  
✅ CloudWatch logs show Lambda invocations  
✅ DynamoDB tables contain your content metadata  
✅ Transcribe job completes  
✅ Bedrock generates script  
✅ AI Critic evaluates quality  

## 🐛 Troubleshooting

### "Bedrock Access Denied"
→ Enable model access in Bedrock console (see Step 3 above)

### "CDK Bootstrap Required"
→ Run `cdk bootstrap` in infrastructure directory

### "API Key Invalid"
→ Verify you copied the full API key from console

### "Lambda Timeout"
→ Check CloudWatch logs for specific error

## 💰 Cost Estimate

For testing (10 uploads):
- **Total**: ~$2-3
- S3: $0.01
- DynamoDB: $0.10
- Lambda: $0.20
- Transcribe: $2.40
- Bedrock: $0.50

## 🧹 Cleanup

When you're done testing:

```bash
# Option A: Automated
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh

# Option B: Manual
cd infrastructure
cdk destroy --all
```

## 📚 Next Steps

1. ✅ **You're here!** - Basic prototype working
2. 📖 Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment info
3. 📊 Check [PROTOTYPE_STATUS.md](PROTOTYPE_STATUS.md) for what's implemented
4. 🔧 Explore the code in `lambdas/` directory
5. 🧪 Run tests: `pytest tests/`
6. 🚀 Implement remaining features (see tasks.md)

## 🆘 Need Help?

- **AWS Documentation**: [docs.aws.amazon.com](https://docs.aws.amazon.com/)
- **CDK Guide**: [AWS CDK Workshop](https://cdkworkshop.com/)
- **Bedrock Guide**: [Amazon Bedrock Docs](https://docs.aws.amazon.com/bedrock/)

## 🎓 What You've Built

Congratulations! You now have:

- ✅ Serverless REST API with authentication
- ✅ AI-powered script generation
- ✅ Quality evaluation system
- ✅ Iterative refinement loop
- ✅ Multi-language support foundation
- ✅ Scalable cloud infrastructure
- ✅ Comprehensive monitoring

This is a production-ready foundation for building the complete OrchestRAI video orchestration engine!

---

**Time to first API call**: ~15 minutes  
**Infrastructure**: 100% serverless  
**Scalability**: Automatic  
**Cost**: Pay-per-use  

Happy building! 🚀

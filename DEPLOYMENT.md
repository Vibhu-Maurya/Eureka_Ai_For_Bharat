# Deployment Guide

This guide walks you through deploying OrchestRAI to your AWS account.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Python 3.11 or higher
- Node.js 18 or higher
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Step 1: Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure

# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (us-east-1)
# - Default output format (json)
```

## Step 2: Set Up Environment

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/orchestrai.git
cd orchestrai

# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate.bat

# Install Python dependencies
pip install -r requirements.txt

# Install CDK dependencies
cd infrastructure
npm install
cd ..
```

## Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
# Required:
# - AWS_ACCOUNT_ID
# - AWS_REGION
```

## Step 4: Update Infrastructure Code

Edit `infrastructure/app.py` and replace the account ID:

```python
env = cdk.Environment(account="YOUR_AWS_ACCOUNT_ID", region="us-east-1")
```

## Step 5: Bootstrap CDK (First Time Only)

```bash
# Set region
set AWS_DEFAULT_REGION=us-east-1

# Bootstrap CDK
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1
```

## Step 6: Deploy Infrastructure

```bash
# Synthesize CloudFormation templates
cdk synth

# Deploy all stacks
cdk deploy --all

# Or deploy individual stacks
cdk deploy OrchestRAIStorageStack
cdk deploy OrchestRAIComputeStack
cdk deploy OrchestRAIWorkflowStack
cdk deploy OrchestRAIApiStack
```

## Step 7: Configure Bedrock Access

1. Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in the left sidebar
3. Click "Manage model access"
4. Enable access to:
   - Claude 3 Haiku
   - Claude 3 Sonnet (optional)
5. Click "Save changes"
6. Wait for approval (usually instant)

## Step 8: Set Up FFmpeg Layer

### Option A: AWS Serverless Application Repository (Recommended)

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click "Layers" in the left sidebar
3. Click "Create layer"
4. Choose "AWS Serverless Application Repository"
5. Search for "ffmpeg"
6. Deploy the layer
7. Note the Layer ARN

### Option B: Custom Layer

```bash
# Create FFmpeg layer package
mkdir -p ffmpeg-layer/bin
cd ffmpeg-layer

# Download FFmpeg static build
# (Instructions vary by OS)

# Create layer zip
zip -r ffmpeg-layer.zip .

# Upload to Lambda
aws lambda publish-layer-version \
  --layer-name ffmpeg \
  --zip-file fileb://ffmpeg-layer.zip \
  --compatible-runtimes python3.11
```

### Attach Layer to Video Assembler

```bash
# Get Video Assembler function name
aws lambda list-functions --query "Functions[?contains(FunctionName, 'VideoAssembler')].FunctionName"

# Attach layer
aws lambda update-function-configuration \
  --function-name YOUR_VIDEO_ASSEMBLER_FUNCTION \
  --layers YOUR_FFMPEG_LAYER_ARN
```

## Step 9: Get API Credentials

After deployment, get your API endpoint and key:

```bash
# Get API endpoint
aws apigateway get-rest-apis --query "items[?name=='OrchestRAI-API'].id" --output text

# Get API key
aws apigateway get-api-keys --include-values --query "items[0].value" --output text
```

Or check the CDK outputs:

```bash
cdk deploy OrchestRAIApiStack --outputs-file outputs.json
cat outputs.json
```

## Step 10: Update Public Interface

Edit `public_interface.html`:

```javascript
const API_BASE_URL = 'YOUR_API_GATEWAY_ENDPOINT';
const API_KEY = 'YOUR_API_KEY';
```

## Step 11: Deploy Public Interface (Optional)

```bash
# Upload to S3
aws s3 cp public_interface.html s3://orchestrai-public-interface/index.html

# Enable static website hosting
aws s3 website s3://orchestrai-public-interface/ \
  --index-document index.html

# Make bucket public (if desired)
aws s3api put-bucket-policy \
  --bucket orchestrai-public-interface \
  --policy file://bucket-policy.json
```

## Step 12: Test Deployment

```bash
# Test upload endpoint
curl -X POST YOUR_API_ENDPOINT/api/v1/upload \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contentType": "text",
    "content": "Test content",
    "targetLanguages": ["en"]
  }'

# Check status
curl -X GET YOUR_API_ENDPOINT/api/v1/status/WORKFLOW_ID \
  -H "x-api-key: YOUR_API_KEY"
```

## Verification Checklist

- [ ] All CDK stacks deployed successfully
- [ ] Bedrock model access granted
- [ ] FFmpeg layer attached to Video Assembler
- [ ] API Gateway endpoint accessible
- [ ] API key working
- [ ] Upload endpoint returns workflow ID
- [ ] Status endpoint returns workflow state
- [ ] Step Functions workflow executes
- [ ] Videos generate successfully
- [ ] Public interface loads (if deployed)

## Troubleshooting

### CDK Bootstrap Failed

```bash
# Ensure you have admin permissions
# Try with explicit credentials
aws sts get-caller-identity

# Re-run bootstrap
cdk bootstrap --force
```

### Deployment Failed

```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name OrchestRAIComputeStack \
  --max-items 10

# View error details
cdk deploy --verbose
```

### Bedrock Access Denied

1. Verify model access in Bedrock console
2. Check IAM role has `bedrock:InvokeModel` permission
3. Ensure you're using a supported model ID

### FFmpeg Not Found

1. Verify layer is attached to Lambda
2. Check layer path is `/opt/bin/ffmpeg`
3. Test FFmpeg in Lambda:

```python
import subprocess
result = subprocess.run(['/opt/bin/ffmpeg', '-version'], capture_output=True)
print(result.stdout.decode())
```

### API Gateway 403 Forbidden

1. Verify API key is correct
2. Check API key is enabled
3. Ensure usage plan is attached
4. Verify CORS settings

## Updating Deployment

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt

# Deploy changes
cdk deploy --all

# Or deploy specific stack
cdk deploy OrchestRAIComputeStack
```

## Rollback

```bash
# Rollback specific stack
aws cloudformation rollback-stack --stack-name OrchestRAIComputeStack

# Or delete and redeploy
cdk destroy OrchestRAIComputeStack
cdk deploy OrchestRAIComputeStack
```

## Clean Up

To remove all resources:

```bash
# Destroy all stacks
cdk destroy --all

# Manually delete S3 buckets (if not empty)
aws s3 rm s3://orchestrai-uploads --recursive
aws s3 rb s3://orchestrai-uploads

aws s3 rm s3://orchestrai-content --recursive
aws s3 rb s3://orchestrai-content
```

## Cost Optimization

### Development

- Use on-demand pricing
- Set Lambda timeouts appropriately
- Enable S3 lifecycle policies
- Use DynamoDB on-demand mode

### Production

- Consider reserved capacity for predictable workloads
- Enable S3 Intelligent-Tiering
- Use Lambda provisioned concurrency for critical functions
- Set up CloudWatch alarms for cost monitoring

## Security Hardening

### Production Checklist

- [ ] Enable CloudTrail logging
- [ ] Set up AWS WAF for API Gateway
- [ ] Enable S3 bucket encryption
- [ ] Configure VPC for Lambda functions
- [ ] Use AWS Secrets Manager for credentials
- [ ] Enable DynamoDB point-in-time recovery
- [ ] Set up AWS Config rules
- [ ] Enable GuardDuty
- [ ] Configure AWS Shield
- [ ] Set up CloudWatch alarms

## Monitoring

### CloudWatch Dashboards

Create dashboards for:
- API request count and latency
- Lambda invocation count and errors
- Step Functions execution success rate
- Bedrock token usage
- S3 storage usage

### Alarms

Set up alarms for:
- API error rate > 5%
- Lambda error rate > 10%
- Step Functions failure rate > 5%
- Cost > budget threshold

## Support

For deployment issues:
- Check CloudWatch Logs
- Review CloudFormation events
- Consult AWS documentation
- Open an issue on GitHub

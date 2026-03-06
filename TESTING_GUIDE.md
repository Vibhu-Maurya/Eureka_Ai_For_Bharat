# OrchestRAI Testing Guide

## 🧪 Testing Options

You have three ways to test OrchestRAI:

1. **Local Unit Tests** (No AWS required) - Test individual components
2. **Mock Integration Tests** (No AWS required) - Test with mocked AWS services
3. **Full AWS Deployment** (AWS account required) - Test the complete system

## Option 1: Local Unit Tests (Fastest - 2 minutes)

Test individual Lambda functions without deploying to AWS.

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_upload_handler.py -v

# Run with coverage report
pytest tests/ --cov=lambdas --cov=shared --cov-report=html
```

### Expected Output
```
tests/test_upload_handler.py::TestUploadHandler::test_valid_video_upload PASSED
tests/test_upload_handler.py::TestUploadHandler::test_valid_text_upload PASSED
tests/test_upload_handler.py::TestUploadHandler::test_invalid_format PASSED
tests/test_upload_handler.py::TestUploadHandler::test_invalid_duration PASSED
tests/test_upload_handler.py::TestUploadHandler::test_missing_required_field PASSED
tests/test_script_generator.py::TestScriptGenerator::test_validate_script_valid PASSED
...
```

## Option 2: Mock Integration Tests (Recommended for Development)

Test the system with mocked AWS services using LocalStack or moto.

### Setup LocalStack (Optional)

```bash
# Install LocalStack
pip install localstack

# Start LocalStack
localstack start
```

### Run Mock Tests

```bash
# Run integration tests with mocks
pytest tests/ -m integration -v
```

## Option 3: Full AWS Deployment (Complete System Test)

Deploy to AWS and test the real system end-to-end.

### Step 1: Prerequisites Check

**Required:**
- ✅ AWS Account with admin access
- ✅ AWS CLI installed and configured
- ✅ Python 3.11+
- ✅ Node.js 18+
- ✅ AWS CDK CLI (`npm install -g aws-cdk`)

**Check your setup:**

```bash
# Check AWS CLI
aws --version
# Should show: aws-cli/2.x.x

# Check Python
python --version
# Should show: Python 3.11.x or higher

# Check Node.js
node --version
# Should show: v18.x.x or higher

# Check CDK
cdk --version
# Should show: 2.x.x

# Check AWS credentials
aws sts get-caller-identity
# Should show your AWS account details
```

### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Enter when prompted:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json
```

### Step 3: Enable Bedrock Access

**IMPORTANT:** You must enable Bedrock model access before deployment.

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click **"Model access"** in the left menu
3. Click **"Manage model access"**
4. Enable **"Claude 3 Sonnet"** (anthropic.claude-3-sonnet-20240229-v1:0)
5. Click **"Save changes"**
6. Wait for status to show "Access granted" (takes 1-2 minutes)

### Step 4: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install CDK dependencies
cd infrastructure
pip install -r requirements.txt
cd ..
```

### Step 5: Deploy to AWS

**Option A: Automated Deployment (Recommended)**

```bash
# Make script executable (Git Bash on Windows)
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

**Option B: Manual Deployment**

```bash
cd infrastructure

# Bootstrap CDK (first time only)
cdk bootstrap

# Synthesize CloudFormation templates
cdk synth

# Deploy all stacks
cdk deploy --all --require-approval never

# Note the outputs (API URL and other details)
```

**Deployment Time:** 10-15 minutes

**Expected Output:**
```
✅ OrchestRAIStorageStack
✅ OrchestRAIComputeStack
✅ OrchestRAIApiStack

Outputs:
OrchestRAIApiStack.ApiUrl = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
```

### Step 6: Get Your API Key

```bash
# Get API key from AWS CLI
aws apigateway get-api-keys --include-values --query 'items[0].value' --output text
```

**Or via AWS Console:**
1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway/)
2. Click **"API Keys"** in left menu
3. Click on your API key
4. Click **"Show"** to reveal the key
5. Copy the key value

### Step 7: Test the System

**Test 1: Upload Text Content**

```bash
cd examples
python test_upload.py <YOUR_API_URL> <YOUR_API_KEY>
```

Example:
```bash
python test_upload.py https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod abc123key456
```

**Expected Output:**
```
🚀 OrchestRAI API Test
==================================================
API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
API Key: abc123key4...
==================================================

📝 Uploading text content...
✅ Upload successful!
   Workflow ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   Content ID: f9e8d7c6-b5a4-3210-9876-543210fedcba
   Status: initiated
   Estimated completion: 300s

⏳ Waiting 10 seconds before checking status...

🔍 Checking workflow status...
✅ Status retrieved:
   Status: processing
   Progress: 50%
```

**Test 2: Check Workflow Status**

```bash
# Using curl (replace with your values)
curl -H "x-api-key: YOUR_API_KEY" \
  https://YOUR_API_URL/api/v1/status/WORKFLOW_ID
```

**Expected Response:**
```json
{
  "workflowId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "currentStage": "TranslateScript",
  "progress": 60
}
```

**Test 3: Monitor in AWS Console**

1. **Step Functions:**
   - Go to [Step Functions Console](https://console.aws.amazon.com/states/)
   - Click "VideoGenerationWorkflow"
   - See your execution in real-time with visual workflow

2. **CloudWatch Logs:**
   - Go to [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
   - Click "Log groups"
   - Look for `/aws/lambda/OrchestRAI-*`
   - View execution logs

3. **DynamoDB:**
   - Go to [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
   - Click "Tables"
   - Select "OrchestRAI-ContentMetadata"
   - Click "Explore table items"
   - See your uploaded content

**Test 4: Retrieve Video (After Completion)**

```bash
# Get video URL
curl -H "x-api-key: YOUR_API_KEY" \
  "https://YOUR_API_URL/api/v1/video/VIDEO_ID?language=hi"
```

**Expected Response:**
```json
{
  "videoId": "video-uuid",
  "videoUrl": "https://s3.amazonaws.com/...",
  "subtitleUrl": "https://s3.amazonaws.com/...",
  "duration": 60,
  "language": "hi",
  "qualityScore": 85,
  "metadata": {
    "resolution": {"width": 1080, "height": 1920},
    "createdAt": "2024-01-01T12:00:00Z",
    "downloadCount": 1
  }
}
```

## 🔍 Monitoring Your Tests

### View Step Functions Execution

1. Go to [Step Functions Console](https://console.aws.amazon.com/states/)
2. Click "VideoGenerationWorkflow"
3. Click on your execution
4. See visual workflow with each stage:
   - ✅ ExtractTranscript
   - ✅ GenerateScript
   - ✅ TranslateScript
   - ✅ PlanScenes
   - ✅ SynthesizeVoice
   - ✅ EvaluateQuality
   - ✅ FinalizeOutput

### View CloudWatch Logs

```bash
# View recent logs for upload handler
aws logs tail /aws/lambda/OrchestRAI-UploadHandler --follow

# View logs for specific Lambda
aws logs tail /aws/lambda/OrchestRAI-ScriptGenerator --follow
```

### Query DynamoDB

```bash
# Get content metadata
aws dynamodb get-item \
  --table-name OrchestRAI-ContentMetadata \
  --key '{"contentId": {"S": "YOUR_CONTENT_ID"}}'

# Scan workflow states
aws dynamodb scan \
  --table-name OrchestRAI-WorkflowState \
  --max-items 5
```

## 🐛 Troubleshooting

### Issue: "Bedrock Access Denied"

**Solution:**
1. Go to Bedrock Console
2. Enable Claude 3 Sonnet model access
3. Wait for "Access granted" status
4. Redeploy: `cdk deploy --all`

### Issue: "CDK Bootstrap Required"

**Solution:**
```bash
cd infrastructure
cdk bootstrap
```

### Issue: "Lambda Timeout"

**Solution:**
1. Check CloudWatch logs for specific error
2. Increase timeout in `compute_stack.py`
3. Redeploy

### Issue: "API Key Invalid"

**Solution:**
```bash
# Get correct API key
aws apigateway get-api-keys --include-values
```

### Issue: "Transcribe Job Failed"

**Solution:**
- Verify video format is supported (MP4, MOV, AVI)
- Check video file is not corrupted
- Ensure S3 bucket permissions are correct

## 📊 Test Scenarios

### Scenario 1: Text Article Processing

```python
# Upload text content
payload = {
    "contentType": "text",
    "content": "Your article text here...",
    "sourceLanguage": "en",
    "targetLanguages": ["hi", "ta"],
    "qualityThreshold": 75
}
```

**Expected Flow:**
1. Upload → S3 storage
2. Skip transcription (text input)
3. Generate script with Bedrock
4. Translate to Hindi and Tamil
5. Plan scenes
6. Synthesize voice in both languages
7. Evaluate quality
8. Finalize output

**Duration:** ~2-3 minutes

### Scenario 2: Video Processing (Simulated)

```python
# Upload video metadata
payload = {
    "contentType": "video",
    "file": base64_encoded_video,
    "fileName": "lecture.mp4",
    "durationMinutes": 10,
    "targetLanguages": ["hi"],
    "qualityThreshold": 80
}
```

**Expected Flow:**
1. Upload → S3 storage
2. Transcribe with Amazon Transcribe
3. Generate script
4. Translate to Hindi
5. Plan scenes
6. Synthesize voice
7. Evaluate quality
8. Refine if score < 80
9. Finalize output

**Duration:** ~5-10 minutes (includes transcription)

### Scenario 3: Quality Refinement Loop

Set quality threshold high to trigger refinement:

```python
payload = {
    "contentType": "text",
    "content": "Short text",
    "qualityThreshold": 95  # High threshold
}
```

**Expected Flow:**
1. Generate script
2. Evaluate → Score: 78 (below threshold)
3. Refine script with feedback
4. Evaluate → Score: 85 (below threshold)
5. Refine again
6. Evaluate → Score: 92 (below threshold)
7. Max iterations reached → Flag for review

## 💰 Cost Tracking

Monitor costs during testing:

```bash
# View cost explorer
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

**Expected Costs for Testing:**
- 10 text uploads: ~$2-3
- 10 video uploads: ~$25-30
- Storage (1 month): ~$0.50

## 🧹 Cleanup After Testing

**Remove all resources:**

```bash
# Option A: Automated
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh

# Option B: Manual
cd infrastructure
cdk destroy --all
```

**Verify cleanup:**
```bash
# Check for remaining stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE
```

## ✅ Test Checklist

Before considering testing complete, verify:

- [ ] Unit tests pass locally
- [ ] CDK deployment succeeds
- [ ] API returns 200 on upload
- [ ] Step Functions execution starts
- [ ] CloudWatch shows Lambda logs
- [ ] DynamoDB contains metadata
- [ ] Transcribe job completes (for video)
- [ ] Bedrock generates script
- [ ] Translation produces multiple languages
- [ ] Scene planning creates visual descriptions
- [ ] Polly synthesizes audio
- [ ] AI Critic evaluates quality
- [ ] Status API returns workflow progress
- [ ] Video API returns presigned URLs
- [ ] Workflow completes or refines appropriately

## 🎓 Next Steps After Testing

1. **Analyze Results:**
   - Review CloudWatch logs
   - Check quality scores in DynamoDB
   - Examine generated scripts and translations

2. **Optimize:**
   - Adjust quality thresholds
   - Tune Lambda memory/timeout
   - Optimize Bedrock prompts

3. **Enhance:**
   - Add video rendering with FFmpeg
   - Implement property-based tests
   - Create monitoring dashboards

4. **Scale:**
   - Test with larger files
   - Test concurrent uploads
   - Monitor costs at scale

## 📞 Support

If you encounter issues:

1. Check CloudWatch logs for detailed errors
2. Review Step Functions execution history
3. Verify AWS service quotas
4. Consult AWS documentation
5. Check the DEPLOYMENT.md troubleshooting section

---

**Happy Testing!** 🚀

For questions or issues, refer to:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [COMPLETE_SYSTEM_STATUS.md](COMPLETE_SYSTEM_STATUS.md) - System details
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture overview

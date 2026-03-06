# 🚀 Get Started with OrchestRAI - Step by Step

## Choose Your Testing Path

### Path 1: Quick Local Test (2 minutes) ⚡
**No AWS account needed - Test code locally**

```bash
# Windows (Command Prompt or PowerShell)
scripts\quick_test.bat

# Linux/Mac/Git Bash
chmod +x scripts/test_local.sh
./scripts/test_local.sh
```

This will:
- ✅ Check your Python installation
- ✅ Install dependencies
- ✅ Run unit tests
- ✅ Show you if everything works

---

### Path 2: Full AWS Deployment (15 minutes) 🌐
**Deploy to AWS and test the complete system**

## Step-by-Step Instructions

### 1️⃣ Check Prerequisites (2 minutes)

Open Command Prompt or PowerShell and run:

```bash
# Check Python (need 3.11+)
python --version

# Check AWS CLI
aws --version

# Check Node.js (need 18+)
node --version

# Check CDK
cdk --version

# Check AWS credentials
aws sts get-caller-identity
```

**Missing something?**
- Python: https://www.python.org/downloads/
- AWS CLI: https://aws.amazon.com/cli/
- Node.js: https://nodejs.org/
- CDK: `npm install -g aws-cdk`

### 2️⃣ Configure AWS (3 minutes)

```bash
# Set up AWS credentials
aws configure

# Enter when prompted:
# AWS Access Key ID: [Get from AWS Console → IAM → Users → Security credentials]
# AWS Secret Access Key: [From same place]
# Default region: us-east-1
# Default output format: json
```

### 3️⃣ Enable Bedrock (2 minutes)

**CRITICAL STEP - Don't skip!**

1. Open: https://console.aws.amazon.com/bedrock/
2. Click "Model access" (left menu)
3. Click "Manage model access"
4. Find "Claude 3 Sonnet" and enable it
5. Click "Save changes"
6. Wait for "Access granted" (1-2 minutes)

### 4️⃣ Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Install CDK packages
cd infrastructure
pip install -r requirements.txt
cd ..
```

### 5️⃣ Deploy to AWS (10 minutes)

```bash
cd infrastructure

# First time only - bootstrap CDK
cdk bootstrap

# Deploy everything
cdk deploy --all --require-approval never
```

**Wait for deployment...** ☕

You'll see:
```
✅ OrchestRAIStorageStack
✅ OrchestRAIComputeStack  
✅ OrchestRAIApiStack

Outputs:
OrchestRAIApiStack.ApiUrl = https://abc123.execute-api.us-east-1.amazonaws.com/prod/
```

**Copy the API URL!** You'll need it.

### 6️⃣ Get Your API Key (1 minute)

**Option A: AWS CLI**
```bash
aws apigateway get-api-keys --include-values --query 'items[0].value' --output text
```

**Option B: AWS Console**
1. Go to: https://console.aws.amazon.com/apigateway/
2. Click "API Keys" (left menu)
3. Click on your key
4. Click "Show"
5. Copy the key

### 7️⃣ Test It! (2 minutes)

```bash
cd examples

# Replace with your actual values
python test_upload.py https://YOUR_API_URL YOUR_API_KEY
```

Example:
```bash
python test_upload.py https://abc123.execute-api.us-east-1.amazonaws.com/prod abc123key456
```

**You should see:**
```
🚀 OrchestRAI API Test
==================================================

📝 Uploading text content...
✅ Upload successful!
   Workflow ID: a1b2c3d4-...
   Content ID: f9e8d7c6-...
   Status: initiated
   Estimated completion: 300s

⏳ Waiting 10 seconds before checking status...

🔍 Checking workflow status...
✅ Status retrieved:
   Status: processing
   Progress: 50%
```

### 8️⃣ Monitor Your Workflow (Real-time!)

**Step Functions (Visual Workflow):**
1. Go to: https://console.aws.amazon.com/states/
2. Click "VideoGenerationWorkflow"
3. Click on your execution
4. Watch it progress through each stage! 🎬

**CloudWatch Logs (Detailed):**
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click "Log groups"
3. Click `/aws/lambda/OrchestRAI-ScriptGenerator`
4. See what's happening inside!

**DynamoDB (Data):**
1. Go to: https://console.aws.amazon.com/dynamodb/
2. Click "Tables"
3. Click "OrchestRAI-ContentMetadata"
4. Click "Explore table items"
5. See your content!

---

## 🎉 Success Checklist

You'll know it's working when:

- ✅ Upload returns 200 with workflowId
- ✅ Step Functions shows execution running
- ✅ CloudWatch has logs from Lambda functions
- ✅ DynamoDB has your content metadata
- ✅ Status API returns progress updates

---

## 🐛 Common Issues & Fixes

### "Bedrock Access Denied"
→ Go back to step 3 and enable Claude 3 Sonnet

### "CDK Bootstrap Required"
→ Run: `cd infrastructure && cdk bootstrap`

### "Python not found"
→ Install Python 3.11+ and add to PATH

### "AWS credentials not configured"
→ Run: `aws configure` and enter your credentials

### "API Key Invalid"
→ Get new key: `aws apigateway get-api-keys --include-values`

---

## 📊 What Happens During Testing

When you upload content, here's what happens:

```
1. Upload → API Gateway → Upload Handler Lambda
   ↓
2. Store in S3 + DynamoDB
   ↓
3. Start Step Functions Workflow
   ↓
4. Extract Transcript (Transcribe)
   ↓
5. Generate Script (Bedrock AI)
   ↓
6. Translate to Languages (Bedrock AI)
   ↓
7. Plan Visual Scenes (Bedrock AI)
   ↓
8. Synthesize Voice (Polly)
   ↓
9. Evaluate Quality (Bedrock AI)
   ↓
10. If quality < 75 → Refine and repeat
    If quality ≥ 75 → Finalize!
   ↓
11. Generate Download URLs
   ↓
12. Done! ✅
```

**Total time:** 2-5 minutes per upload

---

## 💰 Cost During Testing

**10 test uploads:**
- Transcribe: ~$2.40
- Bedrock: ~$2.00
- Polly: ~$0.40
- Lambda: ~$0.20
- S3 + DynamoDB: ~$0.10
- **Total: ~$5**

---

## 🧹 Clean Up When Done

**Remove everything from AWS:**

```bash
cd infrastructure
cdk destroy --all
```

Type `y` to confirm.

This removes:
- All Lambda functions
- All DynamoDB tables
- All S3 buckets
- API Gateway
- Step Functions
- Everything!

**Cost after cleanup:** $0

---

## 🎓 What to Try Next

### Test Different Content Types

**Short text:**
```python
payload = {
    "contentType": "text",
    "content": "AI is transforming video creation.",
    "targetLanguages": ["hi"]
}
```

**Long article:**
```python
payload = {
    "contentType": "text",
    "content": "Your 1000-word article here...",
    "targetLanguages": ["hi", "ta", "te"]
}
```

**Multiple languages:**
```python
payload = {
    "contentType": "text",
    "content": "Your content...",
    "targetLanguages": ["hi", "ta", "te", "bn", "mr"]
}
```

**High quality threshold:**
```python
payload = {
    "contentType": "text",
    "content": "Your content...",
    "qualityThreshold": 90  # Will trigger refinement
}
```

### Monitor Different Stages

Watch each Lambda function:
```bash
# Script generation
aws logs tail /aws/lambda/OrchestRAI-ScriptGenerator --follow

# Translation
aws logs tail /aws/lambda/OrchestRAI-TranslationService --follow

# Voice synthesis
aws logs tail /aws/lambda/OrchestRAI-VoiceSynthesizer --follow

# AI Critic
aws logs tail /aws/lambda/OrchestRAI-AICritic --follow
```

### Check Generated Data

```bash
# View scripts
aws dynamodb scan --table-name OrchestRAI-ScriptVersions --max-items 5

# View translations
aws dynamodb scan --table-name OrchestRAI-Translations --max-items 5

# View quality scores
aws dynamodb scan --table-name OrchestRAI-QualityEvaluations --max-items 5
```

---

## 📚 Learn More

- **TESTING_GUIDE.md** - Comprehensive testing documentation
- **DEPLOYMENT.md** - Detailed deployment guide
- **COMPLETE_SYSTEM_STATUS.md** - What's implemented
- **ARCHITECTURE.md** - How it all works

---

## 🆘 Need Help?

1. Check TESTING_GUIDE.md for detailed troubleshooting
2. Review CloudWatch logs for specific errors
3. Check Step Functions execution for failed stages
4. Verify AWS service quotas and limits

---

## 🎉 You're Ready!

Pick your path:
- **Quick test:** Run `scripts\quick_test.bat`
- **Full deployment:** Follow steps 1-8 above
- **Learn more:** Read TESTING_GUIDE.md

**Let's build something amazing!** 🚀

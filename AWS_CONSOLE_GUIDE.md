# AWS Console Navigation Guide for OrchestRAI

## What You Should See in AWS Console

### 1. CloudFormation Stacks
**URL**: https://console.aws.amazon.com/cloudformation/home?region=us-east-1

**What to look for**:
- ✅ OrchestRAIStorageStack (Status: UPDATE_COMPLETE)
- ✅ OrchestRAIComputeStack (Status: UPDATE_COMPLETE)
- ✅ OrchestRAIWorkflowStack (Status: UPDATE_COMPLETE)
- ✅ OrchestRAIApiStack (Status: CREATE_COMPLETE)

**If you see "empty"**: Make sure you're in the **us-east-1** region (top-right corner)

---

### 2. Step Functions State Machine
**URL**: https://us-east-1.console.aws.amazon.com/states/home?region=us-east-1#/statemachines

**What to look for**:
- State machine name: `VideoGenerationWorkflow77F51D29-u3soPPPStGMO`
- Status: ACTIVE
- Click on it to see executions

**To view executions**:
1. Click on the state machine name
2. Click "Executions" tab
3. You should see 5+ SUCCEEDED executions

**If you see "empty"**: 
- Check you're in us-east-1 region
- Click "Executions" tab (not "Definition" tab)

---

### 3. DynamoDB Tables
**URL**: https://us-east-1.console.aws.amazon.com/dynamodbv2/home?region=us-east-1#tables

**What to look for**:
- OrchestRAI-WorkflowState (11 items)
- OrchestRAI-ContentMetadata (items)
- OrchestRAI-FinalVideos (5 items)
- OrchestRAI-ScriptVersions (items)
- OrchestRAI-Translations (items)
- OrchestRAI-ScenePlans (items)
- OrchestRAI-QualityEvaluations (items)

**To view items**:
1. Click on table name
2. Click "Explore table items" button
3. Click "Run" to scan items

**If you see "empty"**: 
- Make sure you clicked "Run" to scan
- Check you're in us-east-1 region

---

### 4. S3 Buckets
**URL**: https://s3.console.aws.amazon.com/s3/buckets?region=us-east-1

**What to look for**:
- `orchestrai-uploads` bucket (44 objects, ~12 KB)
- `orchestrai-content` bucket (44 objects, ~2.3 MB)

**To view files**:
1. Click on bucket name
2. Browse folders: uploads/, transcripts/, audio/, finals/
3. Click on folders to see files

**If you see "empty"**: 
- Make sure you're viewing the correct bucket
- Check folder structure (files are in subfolders)

---

### 5. Lambda Functions
**URL**: https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions

**What to look for** (10 functions):
- OrchestRAIComputeStack-UploadHandler*
- OrchestRAIComputeStack-ScriptGenerator*
- OrchestRAIComputeStack-AICritic*
- OrchestRAIComputeStack-TranscriptExtractor*
- OrchestRAIComputeStack-TranslationService*
- OrchestRAIComputeStack-ScenePlanner*
- OrchestRAIComputeStack-VoiceSynthesizer*
- OrchestRAIComputeStack-CompletionHandler*
- OrchestRAIComputeStack-StatusHandler*
- OrchestRAIComputeStack-VideoRetrievalHandler*

**If you see "empty"**: Check you're in us-east-1 region

---

### 6. API Gateway
**URL**: https://us-east-1.console.aws.amazon.com/apigateway/main/apis?region=us-east-1

**What to look for**:
- API name: "OrchestRAI Video Engine API"
- API ID: yt103tg9n6
- Stage: prod

**To view endpoints**:
1. Click on API name
2. Click "Resources" in left menu
3. You should see: /api/v1/upload, /api/v1/status/{workflowId}, /api/v1/video/{videoId}

**If you see "empty"**: Check you're in us-east-1 region

---

### 7. CloudWatch Logs
**URL**: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups

**What to look for**:
- Log groups starting with `/aws/lambda/OrchestRAIComputeStack-`
- Recent log streams (within last few hours)

**To view logs**:
1. Click on log group name
2. Click on most recent log stream
3. View log events

**If you see "empty"**: 
- Check you're in us-east-1 region
- Make sure you've run at least one workflow

---

## Common Issues

### "I don't see any resources"
**Solution**: Check the region selector in top-right corner. It MUST be **us-east-1 (N. Virginia)**

### "Tables show 0 items"
**Solution**: In DynamoDB, click "Explore table items" then click "Run" button to scan

### "S3 buckets are empty"
**Solution**: Files are in subfolders. Click through: uploads/ → [contentId]/ → files

### "No Step Functions executions"
**Solution**: 
1. Make sure you're viewing the correct state machine
2. Click "Executions" tab
3. If truly empty, run: `.\test_workflow_now.bat`

---

## Quick Verification Commands

Run these from your terminal to verify data exists:

```batch
# Check CloudFormation stacks
set AWS_DEFAULT_REGION=us-east-1
C:\Python313\python.exe -m awscli cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query "StackSummaries[?contains(StackName, 'OrchestRAI')].[StackName,StackStatus]" --output table

# Check S3 files
C:\Python313\python.exe -m awscli s3 ls s3://orchestrai-uploads/ --recursive | findstr /C:"Total"

# Check DynamoDB items
C:\Python313\python.exe -m awscli dynamodb scan --table-name OrchestRAI-WorkflowState --select COUNT

# Check Step Functions executions
C:\Python313\python.exe -m awscli stepfunctions list-executions --state-machine-arn "arn:aws:states:us-east-1:240122312905:stateMachine:VideoGenerationWorkflow77F51D29-u3soPPPStGMO" --max-results 5
```

---

## Need Help?

If you're still seeing "empty" after checking the region and following these steps, please specify:
1. Which AWS service page you're looking at
2. What exactly shows as empty
3. Screenshot if possible

Your system has:
- ✅ 4 CloudFormation stacks deployed
- ✅ 11 workflow records in DynamoDB
- ✅ 5 completed videos generated
- ✅ 44 files in S3 (uploads)
- ✅ 44 files in S3 (content)
- ✅ 10 Lambda functions active
- ✅ 1 API Gateway with 3 endpoints
- ✅ 1 Step Functions state machine with 5+ successful executions

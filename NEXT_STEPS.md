# Next Steps - Testing OrchestRAI Workflow

## Current Status
✅ Lambda functions updated to use Claude 3 Haiku (ACTIVE model)
✅ Marketplace permissions added to Lambda role
✅ Step Functions workflow deployed
✅ All infrastructure is ready

## What Just Happened
The marketplace permissions were just added to your Lambda execution role. AWS mentioned these permissions can take up to 2 minutes to propagate across their systems.

## Test the Workflow Now

### Option 1: Use the Web Interface (Recommended)
1. Open `orchestrai_interface.html` in your browser
2. Go to the "Upload Content" tab
3. Enter a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
4. Select language, tone, and pacing
5. Click "Upload Content"
6. Switch to "Check Status" tab to monitor progress

### Option 2: Use the Test Script
Run this command:
```
.\test_workflow_now.bat
```

This will:
- Upload test content via API
- Show the workflow execution status
- Display any errors if they occur

### Option 3: Check Latest Execution
To see details of the most recent workflow execution:
```
.\check_latest_execution.bat
```

To see detailed error logs if it failed:
```
.\check_latest_failure.bat
```

## What to Expect

### If It Works ✅
- Upload Handler will accept your content
- Step Functions workflow will start
- Script Generator will create a video script using Claude 3 Haiku
- AI Critic will evaluate the script quality
- If quality score < 80, it will iterate (max 3 times)
- Final video will be generated and stored

### If It Still Fails ❌
The most likely issues:

1. **Permissions still propagating** (wait 2-5 minutes and try again)
2. **Claude 3 Haiku requires marketplace subscription** (even though it shows ACTIVE)
3. **Different Bedrock permission needed**

## Alternative Models to Try

If Claude 3 Haiku continues to fail, we can switch to these ACTIVE models that don't require marketplace:

1. **Amazon Nova Pro** (`amazon.nova-pro-v1:0`) - Amazon's own model, no marketplace needed
2. **Amazon Nova 2 Lite** (`amazon.nova-2-lite-v1:0`) - Lighter Amazon model
3. **Claude Sonnet 4** (`anthropic.claude-sonnet-4-20250514-v1:0`) - Newer Claude model

To switch models, we would update the `BEDROCK_MODEL_ID` in the Lambda functions and redeploy.

## Troubleshooting Commands

Check if workflow is running:
```
.\check_latest_execution.bat
```

See detailed error logs:
```
.\check_latest_failure.bat
```

List all recent executions:
```
.\check_recent_executions.bat
```

## Need Help?
If the workflow still fails after 5 minutes, run `.\check_latest_failure.bat` and share the output. We'll analyze the exact error and fix it.

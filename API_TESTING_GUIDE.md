# OrchestRAI API Testing Guide

## 🔑 API Credentials

**API Endpoint**: `YOUR_API_GATEWAY_ENDPOINT_HERE`

**API Key**: `YOUR_API_KEY_HERE`

**Region**: us-east-1 (US East - N. Virginia)

## 📋 Available Endpoints

### 1. Upload Endpoint
**POST** `/api/v1/upload`

Upload a video or text for processing.

**Headers**:
```
x-api-key: YOUR_API_KEY_HERE
Content-Type: application/json
```

**Request Body** (Text Input):
```json
{
  "content_type": "text",
  "source_text": "Your video script text here",
  "target_language": "hi",
  "style_preferences": {
    "tone": "professional",
    "pacing": "moderate"
  }
}
```

**Request Body** (Video Input):
```json
{
  "content_type": "video",
  "source_url": "s3://orchestrai-uploads/my-video.mp4",
  "target_language": "hi",
  "style_preferences": {
    "tone": "professional",
    "pacing": "moderate"
  }
}
```

**Example curl command**:
```bash
curl -X POST YOUR_API_GATEWAY_ENDPOINT_HERE/upload \
  -H "x-api-key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "source_text": "Welcome to our AI video generation platform. This system can transform your content into engaging videos in multiple languages.",
    "target_language": "hi",
    "style_preferences": {
      "tone": "professional",
      "pacing": "moderate"
    }
  }'
```

**Windows PowerShell**:
```powershell
$headers = @{
    "x-api-key" = "YOUR_API_KEY_HERE"
    "Content-Type" = "application/json"
}

$body = @{
    content_type = "text"
    source_text = "Welcome to our AI video generation platform."
    target_language = "hi"
    style_preferences = @{
        tone = "professional"
        pacing = "moderate"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR_API_GATEWAY_ENDPOINT_HERE/upload" -Method Post -Headers $headers -Body $body
```

### 2. Status Endpoint
**GET** `/api/v1/status/{workflowId}`

Check the status of a workflow.

**Headers**:
```
x-api-key: YOUR_API_KEY_HERE
```

**Example curl command**:
```bash
curl -X GET YOUR_API_GATEWAY_ENDPOINT_HERE/status/YOUR_WORKFLOW_ID \
  -H "x-api-key: YOUR_API_KEY_HERE"
```

**Windows PowerShell**:
```powershell
$headers = @{
    "x-api-key" = "YOUR_API_KEY_HERE"
}

Invoke-RestMethod -Uri "YOUR_API_GATEWAY_ENDPOINT_HERE/status/YOUR_WORKFLOW_ID" -Method Get -Headers $headers
```

### 3. Video Retrieval Endpoint
**GET** `/api/v1/video/{videoId}`

Retrieve the final generated video.

**Headers**:
```
x-api-key: YOUR_API_KEY_HERE
```

**Example curl command**:
```bash
curl -X GET YOUR_API_GATEWAY_ENDPOINT_HERE/video/YOUR_VIDEO_ID \
  -H "x-api-key: YOUR_API_KEY_HERE"
```

**Windows PowerShell**:
```powershell
$headers = @{
    "x-api-key" = "YOUR_API_KEY_HERE"
}

Invoke-RestMethod -Uri "YOUR_API_GATEWAY_ENDPOINT_HERE/video/YOUR_VIDEO_ID" -Method Get -Headers $headers
```

## 🧪 Quick Test Script

Run the included test script:
```bash
.\test_api.bat
```

This will test all three endpoints and show you the responses.

## 📊 Expected Responses

### Successful Upload Response
```json
{
  "workflow_id": "wf_abc123xyz",
  "status": "initiated",
  "message": "Workflow started successfully"
}
```

### Status Response
```json
{
  "workflow_id": "wf_abc123xyz",
  "status": "processing",
  "current_stage": "script_generation",
  "progress": 45,
  "estimated_completion": "2024-02-28T18:30:00Z"
}
```

### Video Retrieval Response
```json
{
  "video_id": "vid_xyz789",
  "status": "completed",
  "download_url": "https://orchestrai-content.s3.amazonaws.com/videos/vid_xyz789.mp4",
  "metadata": {
    "duration": 120,
    "language": "hi",
    "created_at": "2024-02-28T18:00:00Z"
  }
}
```

## 🔍 Monitoring and Debugging

### View Lambda Logs
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click "Log groups" in the left sidebar
3. Find logs for your Lambda functions:
   - `/aws/lambda/OrchestRAIComputeStack-UploadHandler...`
   - `/aws/lambda/OrchestRAIComputeStack-StatusHandler...`
   - `/aws/lambda/OrchestRAIComputeStack-VideoRetrievalHandler...`

### Check DynamoDB Tables
1. Go to: https://console.aws.amazon.com/dynamodb/
2. Click "Tables" in the left sidebar
3. View data in:
   - `OrchestRAI-WorkflowState` - Workflow status
   - `OrchestRAI-ContentMetadata` - Content metadata
   - `OrchestRAI-FinalVideos` - Final video information

### Check S3 Buckets
1. Go to: https://console.aws.amazon.com/s3/
2. View buckets:
   - `orchestrai-uploads` - Uploaded content
   - `orchestrai-content` - Generated content

## ⚠️ Current Limitations

1. **No Step Functions Workflow**: Lambda functions are deployed but not orchestrated by Step Functions. You'll need to invoke them manually or add Step Functions in a future update.

2. **Manual Workflow Invocation**: To process a video end-to-end, you'll need to:
   - Call Upload Handler
   - Manually invoke Transcript Extractor
   - Manually invoke Script Generator
   - Continue through the pipeline

3. **Error Handling**: Some Lambda functions may have minor bugs that need fixing during testing.

## 🚀 Next Steps

1. **Test the Upload Endpoint** with sample text
2. **Monitor CloudWatch Logs** to see Lambda execution
3. **Check DynamoDB Tables** for stored data
4. **(Optional) Add Step Functions** to automate the workflow
5. **(Optional) Fix minor bugs** discovered during testing

## 💡 Tips

- Use Postman or Insomnia for easier API testing
- Save your API key securely (don't commit to git)
- Monitor CloudWatch logs for debugging
- Check DynamoDB tables to verify data storage
- Use AWS CLI to invoke Lambda functions directly for testing

## 📞 Support Resources

- **AWS Lambda Console**: https://console.aws.amazon.com/lambda/
- **API Gateway Console**: https://console.aws.amazon.com/apigateway/
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/
- **DynamoDB Console**: https://console.aws.amazon.com/dynamodb/
- **S3 Console**: https://console.aws.amazon.com/s3/

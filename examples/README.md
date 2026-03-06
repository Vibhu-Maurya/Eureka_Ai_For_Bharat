# OrchestRAI Examples

This directory contains example scripts for testing the OrchestRAI API.

## Prerequisites

Install required packages:

```bash
pip install requests
```

## Usage

### Test Text Upload

```bash
python test_upload.py <API_URL> <API_KEY>
```

Example:
```bash
python test_upload.py https://abc123.execute-api.us-east-1.amazonaws.com/prod your-api-key-here
```

### Get API URL and Key

After deploying the infrastructure:

1. **Get API URL**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name OrchestRAIApiStack \
     --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
     --output text
   ```

2. **Get API Key**:
   - Go to AWS Console → API Gateway
   - Click on "API Keys" in the left menu
   - Find your API key and click "Show"

## Monitoring

### View Step Functions Execution

1. Go to AWS Console → Step Functions
2. Click on "VideoGenerationWorkflow"
3. View execution history

### View CloudWatch Logs

1. Go to AWS Console → CloudWatch → Log Groups
2. Look for `/aws/lambda/OrchestRAI-*` log groups
3. View recent log streams

### View DynamoDB Data

1. Go to AWS Console → DynamoDB → Tables
2. Select a table (e.g., OrchestRAI-ContentMetadata)
3. Click "Explore table items"

## Example Outputs

### Successful Upload Response

```json
{
  "workflowId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "contentId": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "status": "initiated",
  "estimatedCompletionTime": 300
}
```

### Workflow Status Response

```json
{
  "workflowId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "currentStage": "GenerateScript",
  "progress": 50
}
```

## Troubleshooting

### 403 Forbidden
- Check that your API key is correct
- Verify the API key is associated with the usage plan

### 429 Too Many Requests
- You've exceeded the rate limit (100 req/min)
- Wait a minute and try again

### 500 Internal Server Error
- Check CloudWatch logs for detailed error messages
- Verify all Lambda functions have proper permissions
- Ensure Bedrock access is enabled in your AWS account

## Next Steps

1. Try uploading different types of content
2. Experiment with different target languages
3. Adjust quality thresholds
4. Monitor costs in AWS Cost Explorer

# 🎬 How to Use OrchestRAI

## Quick Start - Web Interface

### Step 1: Open the Interface

Simply double-click the file:
```
orchestrai_interface.html
```

This will open a beautiful web interface in your browser where you can interact with your OrchestRAI system.

---

## Using the Web Interface

### 📤 Tab 1: Upload Content

This is where you start the video generation process.

**What you can do:**
1. **Choose Content Type**:
   - **Text Content**: Enter text that will be transformed into a video
   - **Video URL**: Provide an S3 URL to an existing video for processing

2. **Enter Your Content**:
   - For text: Type or paste your content in the text area
   - For video: Enter the S3 URL (e.g., `s3://orchestrai-uploads/my-video.mp4`)

3. **Select Target Language**:
   - Hindi (हिन्दी)
   - English
   - Spanish (Español)
   - French (Français)
   - German (Deutsch)
   - Japanese (日本語)
   - Chinese (中文)

4. **Choose Style Preferences**:
   - **Tone**: Professional, Casual, Enthusiastic, or Educational
   - **Pacing**: Slow, Moderate, or Fast

5. **Click "🚀 Start Processing"**

**What happens:**
- Your content is uploaded to AWS S3
- Metadata is stored in DynamoDB
- A workflow is initiated
- You receive a **Workflow ID** - save this!

**Example Response:**
```json
{
  "workflowId": "da5d827f-c9ae-4dcc-a1eb-ea2ae3bb5227",
  "contentId": "d2688754-208f-4237-abb7-f5b4c6f9339d",
  "status": "initiated",
  "estimatedCompletionTime": 300
}
```

---

### 📊 Tab 2: Check Status

Monitor the progress of your video generation.

**What you can do:**
1. Enter the **Workflow ID** from the upload response
2. Click "🔍 Check Status"

**What you'll see:**
- Current workflow status
- Processing stage
- Progress percentage
- Estimated completion time
- Any errors or issues

**Example Response:**
```json
{
  "workflow_id": "da5d827f-c9ae-4dcc-a1eb-ea2ae3bb5227",
  "status": "processing",
  "current_stage": "script_generation",
  "progress": 45,
  "estimated_completion": "2024-02-28T18:30:00Z"
}
```

---

### 🎥 Tab 3: Retrieve Video

Download your completed video.

**What you can do:**
1. Enter the **Video ID** (from completed workflow)
2. Click "📥 Retrieve Video"

**What you'll get:**
- Download URL for the final video
- Video metadata (duration, language, etc.)
- Creation timestamp

**Example Response:**
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

---

## Alternative: Command Line Usage

### Using PowerShell

**Upload Content:**
```powershell
$headers = @{
    "x-api-key" = "hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d"
    "Content-Type" = "application/json"
}

$body = @{
    content_type = "text"
    source_text = "Your content here"
    target_language = "hi"
    style_preferences = @{
        tone = "professional"
        pacing = "moderate"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/upload" -Method Post -Headers $headers -Body $body
```

**Check Status:**
```powershell
$headers = @{
    "x-api-key" = "hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d"
}

Invoke-RestMethod -Uri "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/status/YOUR_WORKFLOW_ID" -Method Get -Headers $headers
```

---

### Using Python

**Run the test script:**
```bash
.\venv\Scripts\python.exe test_api.py
```

**Or use Python code:**
```python
import requests

API_URL = "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d"

# Upload content
response = requests.post(
    f"{API_URL}/api/v1/upload",
    headers={
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "content_type": "text",
        "source_text": "Your content here",
        "target_language": "hi",
        "style_preferences": {
            "tone": "professional",
            "pacing": "moderate"
        }
    }
)

print(response.json())
```

---

### Using curl (Command Line)

**Upload Content:**
```bash
curl -X POST https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/upload \
  -H "x-api-key: hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "source_text": "Your content here",
    "target_language": "hi",
    "style_preferences": {
      "tone": "professional",
      "pacing": "moderate"
    }
  }'
```

---

## Complete Workflow Example

### Step-by-Step Process

1. **Upload Content** (Tab 1)
   - Enter your text: "Welcome to our AI platform"
   - Select language: Hindi
   - Choose tone: Professional
   - Click "Start Processing"
   - **Save the Workflow ID**: `da5d827f-c9ae-4dcc-a1eb-ea2ae3bb5227`

2. **Monitor Progress** (Tab 2)
   - Enter the Workflow ID
   - Click "Check Status"
   - Wait for status to change from "processing" to "completed"

3. **Download Video** (Tab 3)
   - Enter the Video ID (from status response)
   - Click "Retrieve Video"
   - Download the video from the provided URL

---

## What Happens Behind the Scenes

When you upload content, OrchestRAI:

1. **Stores your content** in S3 bucket
2. **Creates metadata** in DynamoDB
3. **Initiates workflow** with a unique ID
4. **Processes through stages**:
   - Transcript extraction (for videos)
   - Script generation with AI
   - Quality evaluation
   - Translation to target language
   - Scene planning
   - Voice synthesis
   - Video assembly
   - Final output

---

## Monitoring Your System

### View Logs in AWS Console

**CloudWatch Logs:**
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click "Log groups"
3. Find logs for your Lambda functions

**DynamoDB Tables:**
1. Go to: https://console.aws.amazon.com/dynamodb/
2. Click "Tables"
3. View data in:
   - `OrchestRAI-ContentMetadata`
   - `OrchestRAI-WorkflowState`
   - `OrchestRAI-FinalVideos`

**S3 Buckets:**
1. Go to: https://console.aws.amazon.com/s3/
2. View buckets:
   - `orchestrai-uploads` - Your uploaded content
   - `orchestrai-content` - Generated videos

---

## Troubleshooting

### Upload fails
- Check that your text is not empty
- Verify API key is correct
- Check internet connection

### Status returns 404
- Verify the Workflow ID is correct
- Wait a few seconds after upload before checking status

### Video retrieval fails
- Ensure the workflow is completed
- Check that the Video ID is correct
- Verify the video was successfully generated

---

## Tips for Best Results

1. **Text Content**:
   - Keep it between 100-500 words for best results
   - Use clear, well-structured sentences
   - Avoid special characters or formatting

2. **Language Selection**:
   - Choose the target language carefully
   - The system will translate and generate voice in that language

3. **Style Preferences**:
   - **Professional**: For business, educational content
   - **Casual**: For social media, informal content
   - **Enthusiastic**: For marketing, promotional content
   - **Educational**: For tutorials, how-to guides

4. **Pacing**:
   - **Slow**: For complex topics, educational content
   - **Moderate**: For general content (recommended)
   - **Fast**: For quick updates, social media

---

## Next Steps

1. **Try the web interface** - Open `orchestrai_interface.html`
2. **Upload sample content** - Test with the provided example text
3. **Monitor the workflow** - Check status periodically
4. **View your data** - Check AWS Console for stored data
5. **Experiment** - Try different languages, tones, and content types

---

## Support

For issues or questions:
- Check `API_TESTING_GUIDE.md` for detailed API documentation
- View `DEPLOYMENT_COMPLETE.md` for system information
- Check CloudWatch logs for error details
- Review DynamoDB tables for workflow data

---

**Enjoy using OrchestRAI! 🎬✨**

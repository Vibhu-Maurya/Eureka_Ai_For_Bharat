# 🎬 OrchestRAI - Public Access Information

## 🌐 Live Web Interface

Your OrchestRAI system is deployed and accessible! Anyone can use it through the web interface.

### Option 1: Local File (Recommended for Testing)
Open the file in your browser:
```
file:///C:/Users/Vibhu-Kavi/Downloads/aibhart/public_interface.html
```

Or simply double-click: `public_interface.html`

### Option 2: Host on a Web Server
To make it publicly accessible on the internet, you can:

1. **GitHub Pages** (Free):
   - Create a GitHub repository
   - Upload `public_interface.html`
   - Enable GitHub Pages in repository settings
   - Access at: `https://yourusername.github.io/repository-name/public_interface.html`

2. **Netlify** (Free):
   - Drag and drop `public_interface.html` to https://app.netlify.com/drop
   - Get instant public URL

3. **AWS S3 Static Website** (Your AWS Account):
   - Upload to S3 bucket with static website hosting enabled
   - Access at: `http://your-bucket-name.s3-website-us-east-1.amazonaws.com`

---

## 🔗 Direct API Access

Anyone can also use the API directly without the web interface:

### API Endpoint
```
https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1
```

### API Key
```
hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d
```

### Example API Calls

#### 1. Upload Content (Text)
```bash
curl -X POST "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/upload" \
  -H "Content-Type: application/json" \
  -H "x-api-key: hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d" \
  -d '{
    "contentType": "text",
    "content": "Your story or article text here...",
    "targetLanguages": ["hi", "en"],
    "qualityThreshold": 75
  }'
```

#### 2. Upload Content (YouTube URL)
```bash
curl -X POST "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/upload" \
  -H "Content-Type: application/json" \
  -H "x-api-key: hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d" \
  -d '{
    "contentType": "video",
    "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "targetLanguages": ["hi", "en"],
    "qualityThreshold": 75
  }'
```

#### 3. Check Status
```bash
curl -X GET "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/status/YOUR_WORKFLOW_ID" \
  -H "x-api-key: hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d"
```

#### 4. Retrieve Video
```bash
curl -X GET "https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1/video/YOUR_VIDEO_ID" \
  -H "x-api-key: hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d"
```

---

## 📱 Share with Others

### For Non-Technical Users:
1. Host `public_interface.html` on GitHub Pages or Netlify (see above)
2. Share the public URL
3. Users can upload content and generate videos through the web interface

### For Developers:
Share this information:
- **API Endpoint**: `https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1`
- **API Key**: `hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d`
- **Documentation**: See API examples above

---

## 🎯 What Users Can Do

1. **Upload Text Content**: Paste articles, stories, or scripts
2. **Upload Video URLs**: Provide YouTube links
3. **Select Languages**: Choose from 7 Indian languages (Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati)
4. **Track Progress**: Check workflow status with workflow ID
5. **Download Videos**: Retrieve generated videos when complete

---

## ⚙️ System Capabilities

- **AI Script Generation**: Powered by Amazon Nova Pro
- **Multi-Language Support**: 7 Indian languages
- **Voice Synthesis**: Natural-sounding AI voices
- **Scene Planning**: Intelligent video structure
- **Quality Evaluation**: AI-driven quality checks
- **Automatic Processing**: End-to-end workflow automation

---

## 🔒 Security Notes

### Current Setup (Development/Demo):
- API key is embedded in the interface (visible to users)
- Suitable for demos and testing
- No user authentication required

### For Production Use:
Consider implementing:
1. **User Authentication**: AWS Cognito or Auth0
2. **API Key Rotation**: Regular key updates
3. **Rate Limiting**: Prevent abuse
4. **Usage Quotas**: Per-user limits
5. **Billing Integration**: Track costs per user

---

## 💰 Cost Considerations

Your AWS account will incur costs for:
- **Amazon Bedrock (Nova Pro)**: ~$0.0008 per 1K input tokens, ~$0.0032 per 1K output tokens
- **Lambda Executions**: ~$0.20 per 1M requests
- **S3 Storage**: ~$0.023 per GB/month
- **DynamoDB**: ~$0.25 per GB/month
- **Step Functions**: ~$0.025 per 1K state transitions
- **API Gateway**: ~$3.50 per million requests

**Estimated cost per video**: $0.10 - $0.50 depending on content length and complexity

---

## 📊 Monitoring

Monitor your system in AWS Console:
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups
- **Step Functions**: https://console.aws.amazon.com/states/home?region=us-east-1
- **Cost Explorer**: https://console.aws.amazon.com/cost-management/home?region=us-east-1#/dashboard

---

## 🆘 Support

If users encounter issues:
1. Check workflow status with their workflow ID
2. View CloudWatch logs for errors
3. Verify API key is correct
4. Ensure they're using the correct endpoint

---

## 🚀 Next Steps

To make this production-ready:
1. Set up custom domain (e.g., `orchestrai.yourdomain.com`)
2. Implement user authentication
3. Add usage analytics
4. Set up monitoring and alerts
5. Create user documentation
6. Add payment/subscription system (if monetizing)

---

**Your OrchestRAI system is live and ready to use!** 🎉

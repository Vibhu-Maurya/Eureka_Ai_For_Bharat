# OrchestRAI - AI Video Orchestration Engine

An AI-powered video generation platform that transforms text content or YouTube videos into engaging short-form videos optimized for Indian audiences. Built with AWS serverless architecture.

## Features

- **Multi-format Input**: Accept text content or YouTube URLs
- **AI-Powered Script Generation**: Uses Amazon Bedrock (Claude 3) for intelligent script creation
- **Multi-language Support**: Generate videos in Hindi, English, Tamil, Telugu, Bengali, Marathi, and Gujarati
- **Quality Assurance**: Automated AI critic evaluates and refines scripts
- **Voice Synthesis**: Natural-sounding narration with Amazon Polly
- **Video Assembly**: FFmpeg-based video rendering with subtitles
- **Serverless Architecture**: Fully scalable AWS infrastructure

## Architecture

The system uses a serverless architecture built on AWS:

- **API Gateway**: REST API with API key authentication
- **Lambda Functions**: Serverless compute for each processing stage
- **Step Functions**: Workflow orchestration
- **Amazon Bedrock**: AI script generation and evaluation
- **Amazon Transcribe**: Speech-to-text for video inputs
- **Amazon Polly**: Text-to-speech for narration
- **S3**: Media storage
- **DynamoDB**: Metadata and state management

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.11+
- Node.js 18+ (for AWS CDK)
- AWS CDK CLI (`npm install -g aws-cdk`)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/orchestrai.git
cd orchestrai
```

### 2. Configure Environment

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your AWS account details:

```bash
AWS_ACCOUNT_ID=your-account-id
AWS_REGION=us-east-1
```

### 3. Install Dependencies

```bash
# Install Python dependencies
python -m pip install -r requirements.txt

# Install CDK dependencies
cd infrastructure
npm install
cd ..
```

### 4. Bootstrap CDK (First Time Only)

```bash
set AWS_DEFAULT_REGION=us-east-1
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1
```

### 5. Deploy Infrastructure

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate.bat

# Set region
set AWS_DEFAULT_REGION=us-east-1

# Deploy all stacks
cdk deploy --all
```

### 6. Configure FFmpeg Layer

The Video Assembler Lambda requires an FFmpeg layer. You can use the AWS Serverless Application Repository FFmpeg layer:

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Navigate to Layers
3. Create layer from AWS Serverless Application Repository
4. Search for "ffmpeg" and deploy the layer
5. Attach the layer to your Video Assembler Lambda function

### 7. Update Public Interface

After deployment, update `public_interface.html` with your API endpoint and key:

```javascript
const API_BASE_URL = 'YOUR_API_GATEWAY_ENDPOINT';
const API_KEY = 'YOUR_API_KEY';
```

## Usage

### API Endpoints

#### Upload Content

```bash
POST /api/v1/upload
Headers: x-api-key: YOUR_API_KEY
Body: {
  "contentType": "text",
  "content": "Your content here",
  "targetLanguages": ["en", "hi"],
  "qualityThreshold": 75
}
```

#### Check Status

```bash
GET /api/v1/status/{workflowId}
Headers: x-api-key: YOUR_API_KEY
```

#### Retrieve Video

```bash
GET /api/v1/video/{videoId}
Headers: x-api-key: YOUR_API_KEY
```

See [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) for detailed API documentation.

## Project Structure

```
orchestrai/
├── infrastructure/          # AWS CDK infrastructure code
│   ├── app.py              # CDK app entry point
│   └── stacks/             # CDK stack definitions
├── lambdas/                # Lambda function code
│   ├── upload_handler/     # Upload API handler
│   ├── transcript_extractor/  # Video transcription
│   ├── script_generator/   # AI script generation
│   ├── ai_critic/          # Quality evaluation
│   ├── video_assembler/    # Video rendering
│   └── completion_handler/ # Workflow completion
├── tests/                  # Unit tests
├── public_interface.html   # Web UI
└── README.md              # This file
```

## Configuration

### Bedrock Model

The system uses Claude 3 Haiku by default. To change the model, update `infrastructure/stacks/compute_stack.py`:

```python
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
```

### Default Languages

To change default target languages, update `lambdas/upload_handler/handler.py`:

```python
target_languages = body.get('targetLanguages', ['en'])
```

### Quality Threshold

The default quality threshold is 75. Scripts scoring below this are refined up to 3 times.

## Monitoring

### CloudWatch Logs

View Lambda logs in CloudWatch:
- `/aws/lambda/OrchestRAIComputeStack-UploadHandler*`
- `/aws/lambda/OrchestRAIComputeStack-VideoAssembler*`

### Step Functions

Monitor workflow executions in the [Step Functions Console](https://console.aws.amazon.com/states/).

### DynamoDB

View workflow state and metadata in the [DynamoDB Console](https://console.aws.amazon.com/dynamodb/).

## Troubleshooting

### Bedrock Access

Ensure you have access to Amazon Bedrock and the Claude models:

1. Go to [Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Request model access for Claude 3 Haiku
3. Wait for approval (usually instant for base models)

### FFmpeg Issues

If video rendering fails:

1. Verify FFmpeg layer is attached to Video Assembler Lambda
2. Check layer path is `/opt/bin/ffmpeg`
3. Ensure layer includes all required filters (drawtext, nullsrc, geq)

### Payment/Marketplace Issues

If you see payment errors:

1. Use base models (no marketplace subscription required)
2. Avoid Hindi translation if using marketplace models
3. Set default language to English only

## Security

### Before Deploying to Production

- [ ] Rotate API keys regularly
- [ ] Enable CloudTrail logging
- [ ] Set up AWS WAF for API Gateway
- [ ] Enable S3 bucket encryption
- [ ] Configure VPC for Lambda functions
- [ ] Set up AWS Secrets Manager for credentials
- [ ] Enable DynamoDB point-in-time recovery

### Never Commit

- AWS credentials
- API keys
- Account numbers
- Private keys
- `.env` files

See [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md) for security checklist.

## Cost Estimation

Approximate costs for 100 videos/month:

- Lambda: $5-10
- Bedrock: $20-50 (depends on script length)
- Transcribe: $10-20 (for video inputs)
- Polly: $5-10
- S3: $1-5
- DynamoDB: $1-5
- Step Functions: $1-2

**Total**: ~$50-100/month

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- Open an issue on GitHub
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system details
- Review [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) for API usage

## Roadmap

- [ ] Real-time progress updates via WebSocket
- [ ] Batch video processing
- [ ] Custom voice training
- [ ] Advanced video effects
- [ ] Multi-region deployment
- [ ] CDN integration for video delivery
- [ ] Analytics dashboard

## Acknowledgments

- Built with AWS CDK
- Uses Amazon Bedrock (Claude 3)
- FFmpeg for video processing
- AWS Serverless Application Repository for FFmpeg layer

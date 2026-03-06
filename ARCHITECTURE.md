# OrchestRAI Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER / FRONTEND                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTPS + API Key
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ POST /upload │  │ GET /status  │  │ GET /video   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     UPLOAD HANDLER LAMBDA                            │
│  • Validate input                                                    │
│  • Store in S3                                                       │
│  • Create metadata                                                   │
│  • Start workflow                                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP FUNCTIONS WORKFLOW                           │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  1. Extract Transcript                                       │   │
│  │     ↓                                                        │   │
│  │  2. Generate Script                                          │   │
│  │     ↓                                                        │   │
│  │  3. Evaluate Quality ──→ [Score < 75?] ──→ Refine (Loop)   │   │
│  │     ↓                                                        │   │
│  │  4. Success / Flag for Review                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   TRANSCRIBE │    │   BEDROCK    │    │    POLLY     │
│              │    │              │    │              │
│ Speech-to-   │    │ • Script Gen │    │ Text-to-     │
│ Text         │    │ • Translation│    │ Speech       │
│              │    │ • AI Critic  │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │                                        │
        ▼                                        ▼
┌──────────────┐                        ┌──────────────┐
│      S3      │                        │  DYNAMODB    │
│              │                        │              │
│ • Uploads    │                        │ • Metadata   │
│ • Transcripts│                        │ • Scripts    │
│ • Audio      │                        │ • Evaluations│
│ • Videos     │                        │ • Workflows  │
└──────────────┘                        └──────────────┘
        │                                        │
        └────────────────────┬───────────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │  CLOUDWATCH  │
                    │              │
                    │ • Logs       │
                    │ • Metrics    │
                    │ • Alarms     │
                    └──────────────┘
```

## Component Details

### 1. API Layer

**API Gateway**
- REST API with OpenAPI specification
- API key authentication
- Rate limiting: 100 req/min per key
- CORS enabled for web clients
- Request/response validation

**Endpoints**:
- `POST /api/v1/upload` - Upload content
- `GET /api/v1/status/{workflowId}` - Check status
- `GET /api/v1/video/{videoId}` - Retrieve video

### 2. Compute Layer

**Lambda Functions**:

1. **Upload Handler**
   - Runtime: Python 3.11
   - Memory: 512 MB
   - Timeout: 30s
   - Triggers: API Gateway

2. **Transcript Extractor**
   - Runtime: Python 3.11
   - Memory: 1024 MB
   - Timeout: 15 min
   - Integrations: Transcribe, S3

3. **Script Generator**
   - Runtime: Python 3.11
   - Memory: 1024 MB
   - Timeout: 5 min
   - Integrations: Bedrock, DynamoDB

4. **AI Critic**
   - Runtime: Python 3.11
   - Memory: 1024 MB
   - Timeout: 5 min
   - Integrations: Bedrock, DynamoDB

**Step Functions**:
- State machine for workflow orchestration
- Retry logic with exponential backoff
- Error handling and logging
- Visual workflow monitoring

### 3. AI Services Layer

**Amazon Bedrock**:
- Model: Claude 3 Sonnet
- Use cases:
  - Script generation from transcripts
  - Multi-language translation
  - Quality evaluation
  - Feedback generation

**Amazon Transcribe**:
- Automatic language detection
- Timestamp preservation
- 10 Indian languages supported
- Vocabulary filtering

**Amazon Polly** (planned):
- Neural TTS engine
- Multi-language voices
- Natural-sounding narration

### 4. Storage Layer

**S3 Buckets**:
```
orchestrai-uploads/
  └── {contentId}/
      └── source.{ext}

orchestrai-content/
  ├── transcripts/{contentId}/
  ├── audio/{contentId}/
  ├── drafts/{contentId}/
  ├── finals/{videoId}/
  └── temp/{contentId}/
```

**DynamoDB Tables**:
- ContentMetadata (PK: contentId)
- WorkflowState (PK: workflowId)
- ScriptVersions (PK: scriptId, SK: version)
- Translations (PK: translationId, SK: language)
- ScenePlans (PK: scenePlanId)
- QualityEvaluations (PK: evaluationId)
- FinalVideos (PK: videoId, SK: language)

### 5. Observability Layer

**CloudWatch**:
- Log Groups: `/aws/lambda/OrchestRAI-*`
- Metrics: Custom metrics for each stage
- Alarms: Failure rate, latency, cost

## Data Flow

### Upload Flow

```
1. User → API Gateway → Upload Handler
2. Upload Handler → S3 (store content)
3. Upload Handler → DynamoDB (store metadata)
4. Upload Handler → Step Functions (start workflow)
5. Return workflowId to user
```

### Processing Flow

```
1. Step Functions → Transcript Extractor
   ├─→ Transcribe (if video)
   └─→ S3 (store transcript)

2. Step Functions → Script Generator
   ├─→ Bedrock (generate script)
   └─→ DynamoDB (store script)

3. Step Functions → AI Critic
   ├─→ Bedrock (evaluate quality)
   └─→ DynamoDB (store evaluation)

4. Step Functions → Decision
   ├─→ [Score ≥ 75] → Success
   ├─→ [Score < 75 & iterations < 3] → Loop to step 2
   └─→ [iterations ≥ 3] → Flag for review
```

### Refinement Loop

```
┌─────────────────────────────────────┐
│                                     │
│  Generate Script                    │
│       ↓                             │
│  Evaluate Quality                   │
│       ↓                             │
│  Score < Threshold? ────Yes────┐    │
│       │                        │    │
│       No                       │    │
│       ↓                        │    │
│  Finalize                      │    │
│                                │    │
└────────────────────────────────┼────┘
                                 │
                    Iteration < 3? ──Yes──→ Loop
                                 │
                                 No
                                 ↓
                          Flag for Review
```

## Security Architecture

### Authentication & Authorization

```
User Request
    ↓
API Key Validation (API Gateway)
    ↓
IAM Role Assumption (Lambda)
    ↓
Service-specific Permissions
    ├─→ S3: Read/Write specific buckets
    ├─→ DynamoDB: Read/Write specific tables
    ├─→ Bedrock: InvokeModel
    ├─→ Transcribe: Start/Get jobs
    └─→ CloudWatch: PutLogs
```

### Network Security

- API Gateway: HTTPS only
- Lambda: VPC isolation (optional)
- S3: Bucket policies + encryption at rest
- DynamoDB: Encryption at rest (default)

## Scalability

### Automatic Scaling

- **API Gateway**: Handles any request volume
- **Lambda**: Auto-scales to 1000 concurrent executions
- **DynamoDB**: On-demand capacity mode
- **S3**: Unlimited storage

### Performance Optimization

- Lambda memory tuning per function
- DynamoDB query optimization
- S3 transfer acceleration (optional)
- CloudFront CDN for video delivery (planned)

## Cost Optimization

### Development
- On-demand pricing for all services
- S3 lifecycle policies for cleanup
- Lambda timeout optimization
- DynamoDB on-demand mode

### Production
- Reserved capacity for predictable workloads
- S3 Intelligent-Tiering
- Lambda provisioned concurrency
- DynamoDB reserved capacity

## Monitoring & Alerting

### Metrics Tracked

- API request count and latency
- Lambda invocation count and duration
- Step Functions execution success/failure rate
- Bedrock token usage and cost
- Transcribe job duration
- S3 storage usage
- DynamoDB read/write capacity

### Alarms

- Failure rate > 5%
- API latency > 3s
- Lambda errors > 10/min
- Cost > budget threshold

## Disaster Recovery

### Backup Strategy

- S3: Versioning enabled
- DynamoDB: Point-in-time recovery
- CloudWatch Logs: Retention policy

### Recovery Procedures

1. Infrastructure: Redeploy with CDK
2. Data: Restore from S3 versions
3. Metadata: Restore from DynamoDB backups

## Future Enhancements

### Phase 2 (Video Processing)
- EC2 Auto Scaling Group for FFmpeg
- ECS Fargate for containerized processing
- MediaConvert for professional encoding

### Phase 3 (Advanced Features)
- Real-time progress updates (WebSocket)
- Batch processing
- Custom model fine-tuning
- Multi-region deployment

### Phase 4 (Enterprise)
- VPC peering for hybrid cloud
- AWS PrivateLink for secure access
- AWS Organizations for multi-account
- AWS Control Tower for governance

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | API Gateway | REST API endpoints |
| Compute | Lambda | Serverless functions |
| Orchestration | Step Functions | Workflow management |
| AI | Bedrock | Script generation & evaluation |
| Speech | Transcribe | Speech-to-text |
| Voice | Polly | Text-to-speech |
| Storage | S3 | Media files |
| Database | DynamoDB | Metadata |
| Monitoring | CloudWatch | Logs & metrics |
| IaC | CDK | Infrastructure as code |

## Deployment Architecture

```
Developer
    ↓
CDK CLI
    ↓
CloudFormation
    ↓
AWS Resources
    ├─→ API Gateway
    ├─→ Lambda Functions
    ├─→ Step Functions
    ├─→ S3 Buckets
    ├─→ DynamoDB Tables
    └─→ IAM Roles
```

---

**Architecture Version**: 1.0  
**Last Updated**: 2024  
**Status**: Prototype - Core components implemented

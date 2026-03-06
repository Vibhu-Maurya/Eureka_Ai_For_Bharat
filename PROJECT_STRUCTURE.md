# OrchestRAI Project Structure

```
orchestrai/
│
├── 📄 README.md                    # Project overview
├── 📄 QUICKSTART.md                # 15-minute setup guide
├── 📄 DEPLOYMENT.md                # Detailed deployment instructions
├── 📄 ARCHITECTURE.md              # System architecture documentation
├── 📄 PROTOTYPE_STATUS.md          # Current implementation status
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 pytest.ini                   # Pytest configuration
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 .kiro/                       # Kiro spec files
│   └── specs/
│       └── ai-video-orchestration-engine/
│           ├── requirements.md     # Feature requirements
│           ├── design.md          # Design document
│           └── tasks.md           # Implementation tasks
│
├── 📁 infrastructure/              # AWS CDK infrastructure code
│   ├── 📄 app.py                  # CDK app entry point
│   ├── 📄 cdk.json                # CDK configuration
│   ├── 📄 requirements.txt        # CDK dependencies
│   │
│   └── 📁 stacks/                 # CDK stack definitions
│       ├── __init__.py
│       ├── storage_stack.py       # S3 + DynamoDB
│       ├── compute_stack.py       # Lambda + Step Functions
│       └── api_stack.py           # API Gateway
│
├── 📁 lambdas/                    # Lambda function implementations
│   ├── __init__.py
│   │
│   ├── 📁 upload_handler/         # Content upload handler
│   │   └── handler.py
│   │
│   ├── 📁 transcript_extractor/   # Transcribe integration
│   │   └── handler.py
│   │
│   ├── 📁 script_generator/       # Bedrock script generation
│   │   └── handler.py
│   │
│   ├── 📁 ai_critic/              # Quality evaluation
│   │   └── handler.py
│   │
│   ├── 📁 translation_service/    # (Planned) Multi-language translation
│   ├── 📁 scene_planner/          # (Planned) Visual scene planning
│   ├── 📁 voice_synthesizer/      # (Planned) Polly integration
│   ├── 📁 video_assembler/        # (Planned) FFmpeg processing
│   ├── 📁 completion_handler/     # (Planned) Final output delivery
│   └── 📁 api_handlers/           # (Planned) Status & retrieval
│
├── 📁 shared/                     # Shared utilities and models
│   ├── __init__.py
│   ├── models.py                  # Pydantic data models
│   └── aws_clients.py             # AWS service clients
│
├── 📁 tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_upload_handler.py     # Upload handler tests
│   └── test_script_generator.py   # Script generator tests
│
├── 📁 scripts/                    # Utility scripts
│   ├── deploy.sh                  # Automated deployment
│   ├── cleanup.sh                 # Resource cleanup
│   └── test.sh                    # Test runner
│
└── 📁 examples/                   # Example usage scripts
    ├── README.md                  # Examples documentation
    └── test_upload.py             # API test script
```

## Directory Descriptions

### Root Level

- **Documentation Files**: Comprehensive guides for setup, deployment, and architecture
- **Configuration Files**: Python dependencies, pytest config, git ignore

### `.kiro/specs/`

Contains the complete feature specification:
- **requirements.md**: 13 detailed requirements with acceptance criteria
- **design.md**: Architecture, components, data models, 52 correctness properties
- **tasks.md**: 20 major tasks with 80+ sub-tasks for implementation

### `infrastructure/`

AWS CDK infrastructure as code:
- **app.py**: Main CDK application
- **stacks/**: Modular stack definitions
  - Storage: S3 buckets + DynamoDB tables
  - Compute: Lambda functions + Step Functions
  - API: API Gateway + endpoints

### `lambdas/`

Serverless function implementations:
- **upload_handler/**: Validates and stores uploaded content
- **transcript_extractor/**: Integrates with Amazon Transcribe
- **script_generator/**: Uses Bedrock for AI script generation
- **ai_critic/**: Evaluates video quality with AI

Each Lambda has its own directory with `handler.py` containing the main logic.

### `shared/`

Common code shared across Lambda functions:
- **models.py**: Pydantic models for type safety
- **aws_clients.py**: Singleton AWS service clients

### `tests/`

Comprehensive test suite:
- **Unit tests**: Test individual functions
- **Property-based tests**: Test universal properties (planned)
- **Integration tests**: Test component interactions (planned)

### `scripts/`

Automation scripts:
- **deploy.sh**: One-command deployment
- **cleanup.sh**: Remove all AWS resources
- **test.sh**: Run test suite with coverage

### `examples/`

Working examples for testing:
- **test_upload.py**: Upload content via API
- Sample payloads and responses

## File Naming Conventions

### Python Files
- `handler.py` - Lambda function entry point
- `test_*.py` - Test files
- `*_stack.py` - CDK stack definitions

### Configuration Files
- `requirements.txt` - Python dependencies
- `cdk.json` - CDK configuration
- `pytest.ini` - Test configuration

### Documentation Files
- `*.md` - Markdown documentation
- ALL_CAPS.md - Important guides

## Key Files to Know

### For Development

1. **lambdas/*/handler.py** - Lambda function logic
2. **shared/models.py** - Data models
3. **infrastructure/stacks/*.py** - Infrastructure definitions

### For Deployment

1. **QUICKSTART.md** - Fast setup guide
2. **DEPLOYMENT.md** - Detailed deployment
3. **scripts/deploy.sh** - Automated deployment

### For Understanding

1. **README.md** - Project overview
2. **ARCHITECTURE.md** - System design
3. **PROTOTYPE_STATUS.md** - What's implemented

### For Testing

1. **examples/test_upload.py** - API testing
2. **tests/test_*.py** - Unit tests
3. **scripts/test.sh** - Test runner

## Code Organization Principles

### Modularity
- Each Lambda function is self-contained
- Shared code in `shared/` directory
- Infrastructure separated from application code

### Testability
- Unit tests for each component
- Mock AWS services in tests
- Property-based tests for correctness

### Maintainability
- Clear directory structure
- Comprehensive documentation
- Type hints with Pydantic models

### Scalability
- Serverless architecture
- Stateless Lambda functions
- Managed AWS services

## Development Workflow

```
1. Read requirements.md
   ↓
2. Review design.md
   ↓
3. Check tasks.md for next task
   ↓
4. Implement in lambdas/
   ↓
5. Write tests in tests/
   ↓
6. Update infrastructure/ if needed
   ↓
7. Deploy with scripts/deploy.sh
   ↓
8. Test with examples/test_upload.py
   ↓
9. Monitor in AWS Console
```

## Adding New Components

### New Lambda Function

1. Create directory: `lambdas/new_function/`
2. Add `handler.py` with `lambda_handler(event, context)`
3. Update `infrastructure/stacks/compute_stack.py`
4. Add tests: `tests/test_new_function.py`
5. Deploy: `cdk deploy`

### New DynamoDB Table

1. Update `infrastructure/stacks/storage_stack.py`
2. Add model in `shared/models.py`
3. Grant permissions in `compute_stack.py`
4. Deploy: `cdk deploy`

### New API Endpoint

1. Update `infrastructure/stacks/api_stack.py`
2. Create handler Lambda
3. Add integration
4. Deploy: `cdk deploy`

## Environment Variables

Lambda functions use these environment variables:

```python
UPLOADS_BUCKET              # S3 bucket for uploads
CONTENT_BUCKET              # S3 bucket for processed content
CONTENT_METADATA_TABLE      # DynamoDB table
WORKFLOW_STATE_TABLE        # DynamoDB table
SCRIPT_VERSIONS_TABLE       # DynamoDB table
QUALITY_EVALUATIONS_TABLE   # DynamoDB table
STATE_MACHINE_ARN           # Step Functions ARN
BEDROCK_MODEL_ID            # Bedrock model identifier
```

Set in `infrastructure/stacks/compute_stack.py`

## Dependencies

### Python Packages

**Application**:
- boto3 - AWS SDK
- pydantic - Data validation

**Infrastructure**:
- aws-cdk-lib - CDK framework
- constructs - CDK constructs

**Testing**:
- pytest - Test framework
- hypothesis - Property-based testing
- moto - AWS mocking

### AWS Services

- API Gateway
- Lambda
- Step Functions
- S3
- DynamoDB
- Bedrock
- Transcribe
- Polly (planned)
- CloudWatch

## Build Artifacts

Generated during deployment:

```
infrastructure/
├── cdk.out/              # CDK synthesis output
│   ├── *.template.json   # CloudFormation templates
│   └── manifest.json     # CDK manifest
│
└── .cdk.staging/         # Staging directory
```

These are gitignored and regenerated on each deployment.

## Next Steps

1. ✅ **You are here** - Basic prototype complete
2. 📖 Read QUICKSTART.md to deploy
3. 🧪 Run tests with scripts/test.sh
4. 🚀 Deploy with scripts/deploy.sh
5. 🔧 Implement remaining tasks from tasks.md
6. 📊 Monitor in AWS Console

---

**Project Structure Version**: 1.0  
**Total Files**: 40+  
**Total Lines of Code**: ~3000+  
**Test Coverage**: Core components  
**Documentation**: Comprehensive

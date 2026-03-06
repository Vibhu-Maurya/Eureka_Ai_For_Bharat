# GitHub Upload Guide - Security Precautions

## ⚠️ CRITICAL: Before Uploading to GitHub

### 1. Remove Sensitive Information

**NEVER commit these files:**
- AWS credentials
- API keys
- Account numbers
- Private keys
- Environment variables with secrets

### 2. Check These Files

Before committing, review and remove sensitive data from:

#### `public_interface.html`
```javascript
// REMOVE OR REPLACE:
const API_ENDPOINT = 'https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1';
const API_KEY = 'hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d';

// REPLACE WITH:
const API_ENDPOINT = process.env.API_ENDPOINT || 'YOUR_API_ENDPOINT_HERE';
const API_KEY = process.env.API_KEY || 'YOUR_API_KEY_HERE';
```

#### Documentation Files
Search for and remove:
- AWS Account ID: `240122312905`
- API endpoints with your account
- Workflow IDs
- S3 bucket names (if private)
- Lambda function ARNs

### 3. Use .gitignore

The `.gitignore` file I created will exclude:
- Temporary files
- Debug documentation
- Batch scripts with credentials
- Test outputs
- AWS CDK output
- Python cache
- Node modules

### 4. Create Environment Template

Create `.env.example` (safe to commit):
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=YOUR_ACCOUNT_ID

# API Configuration
API_ENDPOINT=YOUR_API_ENDPOINT
API_KEY=YOUR_API_KEY

# S3 Buckets
UPLOADS_BUCKET=your-uploads-bucket
CONTENT_BUCKET=your-content-bucket

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### 5. Update README.md

Create a proper README with:
- Project description
- Architecture overview
- Setup instructions (without credentials)
- Deployment guide
- Configuration steps

### 6. Clean Up Before Commit

Run these commands:

```bash
# Remove all temporary files
del *.bat
del *_FIXED.md
del *_READY.md
del test_video.mp4

# Remove CDK output
rmdir /s /q cdk.out

# Remove Python cache
rmdir /s /q __pycache__
rmdir /s /q .pytest_cache

# Remove node modules
rmdir /s /q node_modules
```

### 7. Files Safe to Commit

✅ **Infrastructure Code:**
- `infrastructure/` folder (CDK stacks)
- `lambdas/` folder (Lambda functions)
- `tests/` folder

✅ **Documentation:**
- `README.md`
- `ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `API_TESTING_GUIDE.md`

✅ **Configuration Templates:**
- `.env.example`
- `cdk.json`
- `package.json`
- `requirements.txt`

✅ **Public Interface (sanitized):**
- `public_interface.html` (after removing credentials)

### 8. Files to EXCLUDE

❌ **Never Commit:**
- `.env` (actual environment variables)
- `*.pem`, `*.key` (private keys)
- `cdk.out/` (CDK output)
- `node_modules/` (dependencies)
- `venv/` (Python virtual environment)
- `*.bat` files with credentials
- Debug/temporary markdown files
- Test videos/audio files

### 9. Sanitize Public Interface

Before committing `public_interface.html`, replace:

```javascript
// BEFORE (DON'T COMMIT THIS):
const API_ENDPOINT = 'https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1';
const API_KEY = 'hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d';

// AFTER (SAFE TO COMMIT):
const API_ENDPOINT = '${API_ENDPOINT}'; // Set via environment or config
const API_KEY = '${API_KEY}'; // Set via environment or config
```

### 10. Add Security Notice

Add to README.md:

```markdown
## Security Notice

This project requires AWS credentials and API keys. Never commit:
- AWS credentials
- API keys
- Account numbers
- Private configuration

Use environment variables or AWS Secrets Manager for sensitive data.
```

### 11. Git Commands

```bash
# Initialize git (if not already)
git init

# Add files (respects .gitignore)
git add .

# Check what will be committed
git status

# Review changes
git diff --cached

# Commit
git commit -m "Initial commit: AI Video Orchestration Engine"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push
git push -u origin main
```

### 12. Post-Upload Checklist

After uploading, verify:
- [ ] No AWS credentials in any file
- [ ] No API keys visible
- [ ] No account numbers
- [ ] No private S3 bucket names
- [ ] No Lambda ARNs with account ID
- [ ] `.gitignore` is working
- [ ] README has setup instructions
- [ ] Environment template exists

### 13. If You Accidentally Commit Secrets

If you accidentally commit credentials:

1. **Immediately rotate the credentials** (generate new API keys)
2. **Remove from git history:**
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH_TO_FILE" \
  --prune-empty --tag-name-filter cat -- --all
```
3. **Force push:**
```bash
git push origin --force --all
```

### 14. Recommended Repository Structure

```
your-repo/
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── DEPLOYMENT.md
├── .env.example
├── infrastructure/
│   ├── app.py
│   └── stacks/
├── lambdas/
│   ├── upload_handler/
│   ├── video_assembler/
│   └── ...
├── tests/
├── public/
│   └── index.html (sanitized)
└── docs/
    └── API.md
```

---

## 🔒 Security First!

Always review files before committing. When in doubt, don't commit it!

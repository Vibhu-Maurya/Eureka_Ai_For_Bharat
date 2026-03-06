# Security Checklist for GitHub Upload

## Before Committing

### 1. Remove Sensitive Files

- [ ] No `.env` files (only `.env.example`)
- [ ] No AWS credentials files
- [ ] No private keys (`.pem`, `.key`)
- [ ] No API keys in code
- [ ] No account IDs hardcoded
- [ ] No workflow execution logs with sensitive data
- [ ] No temporary debug files

### 2. Sanitize Code Files

- [ ] `public_interface.html` - API credentials replaced with placeholders
- [ ] `infrastructure/app.py` - Account ID replaced with placeholder
- [ ] `API_TESTING_GUIDE.md` - Credentials replaced with placeholders
- [ ] All Lambda functions - No hardcoded credentials
- [ ] All batch scripts - No sensitive data

### 3. Sanitize Documentation

- [ ] Remove specific AWS account IDs
- [ ] Remove specific API endpoints (or mark as examples)
- [ ] Remove specific ARNs
- [ ] Remove workflow IDs
- [ ] Remove S3 bucket names (if private)
- [ ] Remove Lambda function names (if sensitive)

### 4. Verify .gitignore

- [ ] `.env` files excluded
- [ ] Credentials excluded
- [ ] Temporary files excluded
- [ ] Debug files excluded
- [ ] CDK output excluded
- [ ] Python cache excluded
- [ ] Node modules excluded

### 5. Create Template Files

- [ ] `.env.example` created with placeholders
- [ ] `README.md` has setup instructions
- [ ] `DEPLOYMENT.md` has deployment guide
- [ ] `CONTRIBUTING.md` has contribution guidelines
- [ ] `LICENSE` file added

## Files Safe to Commit

### Infrastructure Code ✅
- `infrastructure/app.py` (sanitized)
- `infrastructure/stacks/*.py`
- `cdk.json`
- `requirements.txt`

### Lambda Functions ✅
- `lambdas/*/handler.py`
- `lambdas/*/requirements.txt`
- All Lambda function code (no credentials)

### Documentation ✅
- `README.md`
- `ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `CONTRIBUTING.md`
- `API_TESTING_GUIDE.md` (sanitized)
- `GITHUB_UPLOAD_GUIDE.md`
- `LICENSE`

### Configuration Templates ✅
- `.env.example`
- `.gitignore`
- `package.json`

### Public Interface ✅
- `public_interface.html` (sanitized)

### Tests ✅
- `tests/**/*.py`

## Files to EXCLUDE

### Never Commit ❌
- `.env` (actual environment variables)
- `*.pem`, `*.key` (private keys)
- `cdk.out/` (CDK output)
- `node_modules/` (dependencies)
- `venv/` (Python virtual environment)
- `__pycache__/` (Python cache)
- `.pytest_cache/` (test cache)
- `*.bat` files (except `deploy.bat`)
- Debug markdown files (`*_FIXED.md`, `*_READY.md`, etc.)
- Test videos/audio files
- `execution_history.json`
- `workflow_history*.json`
- `current_config.json`
- `bedrock_models.json`
- `ffmpeg-layer/` directory
- `test_stories.txt`
- `orchestrai_interface.html` (old version)
- `generate_*.html`

## Verification Steps

### 1. Search for Sensitive Data

```bash
# Search for account ID
grep -r "240122312905" .

# Search for API keys
grep -r "hcRNhlLtFh4Mjc5A4uKbax5" .

# Search for API endpoints
grep -r "yt103tg9n6.execute-api" .

# Search for specific ARNs
grep -r "arn:aws:lambda:us-east-1:240122312905" .
```

### 2. Check Git Status

```bash
# See what will be committed
git status

# Review changes
git diff

# Check what's being tracked
git ls-files
```

### 3. Test .gitignore

```bash
# Create test sensitive file
echo "test" > .env

# Verify it's ignored
git status | grep ".env"
# Should not appear in untracked files
```

### 4. Review Each File

Before committing, manually review:
- [ ] `public_interface.html`
- [ ] `infrastructure/app.py`
- [ ] `API_TESTING_GUIDE.md`
- [ ] All `.md` files in root
- [ ] All Lambda handler files

## Post-Upload Verification

### 1. Check GitHub Repository

- [ ] No `.env` files visible
- [ ] No credentials in code
- [ ] No account IDs in documentation
- [ ] `.gitignore` is working
- [ ] README displays correctly
- [ ] License is visible

### 2. Test Clone

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/orchestrai.git test-clone
cd test-clone

# Verify no sensitive files
ls -la
cat .env 2>/dev/null  # Should not exist

# Check for credentials
grep -r "240122312905" .
grep -r "hcRNhlLtFh4Mjc5A4uKbax5" .
```

### 3. Security Scan

Use GitHub's security features:
- [ ] Enable Dependabot alerts
- [ ] Enable secret scanning
- [ ] Review security advisories
- [ ] Check for exposed secrets

## If You Accidentally Commit Secrets

### Immediate Actions

1. **Rotate credentials immediately**
   - Generate new API keys
   - Update AWS credentials
   - Revoke old credentials

2. **Remove from git history**

```bash
# Remove file from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH_TO_FILE" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
git push origin --force --tags
```

3. **Use BFG Repo-Cleaner (easier)**

```bash
# Install BFG
# Download from https://rtyley.github.io/bfg-repo-cleaner/

# Remove credentials
java -jar bfg.jar --replace-text passwords.txt

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force
```

4. **Contact GitHub Support**
   - Report exposed credentials
   - Request cache purge

## Best Practices

### Development

- Use environment variables for all secrets
- Never hardcode credentials
- Use AWS Secrets Manager in production
- Rotate credentials regularly
- Use IAM roles instead of access keys when possible

### Git Workflow

- Review changes before committing
- Use `git diff --cached` before commit
- Set up pre-commit hooks
- Use `.gitignore` properly
- Never force push to main/master

### AWS Security

- Enable CloudTrail
- Use least privilege IAM policies
- Enable MFA for root account
- Use AWS Organizations for multi-account
- Set up AWS Config rules
- Enable GuardDuty

## Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Git Security](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)

## Questions?

If you're unsure whether something is safe to commit:
1. Assume it's sensitive
2. Ask for review
3. Use placeholders
4. Document in `.env.example`

**When in doubt, leave it out!**

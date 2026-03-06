# Install AWS Tools for Deployment

You need two tools to deploy OrchestRAI to AWS:
1. **AWS CLI** - To configure your AWS credentials
2. **AWS CDK CLI** - To deploy the infrastructure

## Step 1: Install AWS CLI

### Option A: Using MSI Installer (Recommended for Windows)

1. Download the AWS CLI installer:
   - Visit: https://awscli.amazonaws.com/AWSCLIV2.msi
   - Or go to: https://aws.amazon.com/cli/

2. Run the downloaded MSI installer

3. Verify installation:
```powershell
aws --version
```

You should see something like: `aws-cli/2.x.x Python/3.x.x Windows/10`

### Option B: Using Python pip

```powershell
# Activate your virtual environment first
.\venv\Scripts\activate.bat

# Install AWS CLI
pip install awscli

# Verify
aws --version
```

## Step 2: Configure AWS Credentials

After installing AWS CLI, configure your credentials:

```powershell
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security Credentials
- **AWS Secret Access Key**: Get from AWS Console (shown only once when created)
- **Default region**: Enter `us-east-1` (or your preferred region)
- **Default output format**: Enter `json`

### How to Get AWS Credentials:

1. Log in to AWS Console: https://console.aws.amazon.com/
2. Go to IAM (Identity and Access Management)
3. Click "Users" → Your username
4. Click "Security credentials" tab
5. Click "Create access key"
6. Download the credentials (you won't see them again!)

## Step 3: Install AWS CDK CLI

The CDK CLI is a Node.js package. You have two options:

### Option A: Install Node.js and CDK (Recommended)

1. **Install Node.js**:
   - Download from: https://nodejs.org/
   - Choose LTS version (20.x or later)
   - Run the installer

2. **Install CDK CLI globally**:
```powershell
npm install -g aws-cdk

# Verify
cdk --version
```

### Option B: Use CDK from Python (Alternative)

If you don't want to install Node.js, you can use CDK through Python:

```powershell
# Activate virtual environment
.\venv\Scripts\activate.bat

# The CDK library is already installed in your venv
# But you still need the CDK CLI, which requires Node.js
```

**Note**: You really need Node.js for CDK CLI. There's no pure Python alternative.

## Step 4: Verify Everything is Installed

```powershell
# Check AWS CLI
aws --version

# Check CDK CLI
cdk --version

# Check AWS credentials are configured
aws sts get-caller-identity
```

The last command should show your AWS account details if configured correctly.

## Step 5: Deploy OrchestRAI

Once everything is installed:

```powershell
# Navigate to infrastructure directory
cd infrastructure

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks
cdk deploy --all
```

## Troubleshooting

### "aws: command not found" after installation
- Close and reopen PowerShell
- Check if AWS CLI is in PATH: `$env:PATH`
- Try restarting your computer

### "cdk: command not found" after npm install
- Close and reopen PowerShell
- Check Node.js installation: `node --version`
- Check npm installation: `npm --version`
- Try: `npm install -g aws-cdk --force`

### AWS credentials not working
- Check credentials file: `cat ~/.aws/credentials`
- Reconfigure: `aws configure`
- Test: `aws sts get-caller-identity`

### CDK bootstrap fails
- Make sure you have admin permissions in AWS
- Check your AWS region is correct
- Try: `cdk bootstrap aws://ACCOUNT-ID/REGION`

## Quick Installation Summary

```powershell
# 1. Install AWS CLI
# Download and run: https://awscli.amazonaws.com/AWSCLIV2.msi

# 2. Configure AWS
aws configure

# 3. Install Node.js
# Download and run: https://nodejs.org/

# 4. Install CDK CLI
npm install -g aws-cdk

# 5. Verify
aws --version
cdk --version
aws sts get-caller-identity

# 6. Deploy
cd infrastructure
cdk bootstrap
cdk deploy --all
```

## Estimated Time
- AWS CLI installation: 2 minutes
- Node.js installation: 3 minutes
- CDK CLI installation: 2 minutes
- AWS configuration: 5 minutes (getting credentials)
- CDK bootstrap: 2-3 minutes
- CDK deploy: 10-15 minutes

**Total: ~30 minutes**

## Need Help?

- AWS CLI docs: https://docs.aws.amazon.com/cli/
- AWS CDK docs: https://docs.aws.amazon.com/cdk/
- Node.js download: https://nodejs.org/

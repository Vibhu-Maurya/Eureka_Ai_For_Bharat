# Install AWS CLI - Quick Guide

## Current Status ✓
- ✅ Node.js v24.14.0 installed
- ✅ npm v11.9.0 installed  
- ✅ AWS CDK v2.1108.0 installed
- ❌ AWS CLI not installed yet

## Install AWS CLI (2 minutes)

### Option 1: Direct Download (Easiest)

1. **Download the installer**:
   - Click this link: https://awscli.amazonaws.com/AWSCLIV2.msi
   - Or visit: https://aws.amazon.com/cli/

2. **Run the installer**:
   - Double-click the downloaded `AWSCLIV2.msi` file
   - Click "Next" through the installation wizard
   - Accept the license agreement
   - Click "Install"

3. **Restart PowerShell**:
   - Close your current PowerShell window
   - Open a new PowerShell window

4. **Verify installation**:
   ```powershell
   aws --version
   ```
   
   You should see: `aws-cli/2.x.x Python/3.x.x Windows/10`

### Option 2: Using Python pip

Since you already have Python in your virtual environment:

```powershell
# Activate virtual environment
.\venv\Scripts\activate.bat

# Install AWS CLI
pip install awscli

# Verify
aws --version
```

## After Installation

Once AWS CLI is installed, configure your credentials:

```powershell
aws configure
```

You'll need:
- **AWS Access Key ID**: From AWS Console → IAM → Users → Security Credentials
- **AWS Secret Access Key**: From AWS Console (shown only once)
- **Default region**: `us-east-1`
- **Default output format**: `json`

## Then Deploy!

```powershell
cd infrastructure
cdk bootstrap
cdk deploy --all
```

## Quick Test

After configuring AWS CLI:

```powershell
# Test AWS credentials
aws sts get-caller-identity

# Should show your AWS account info
```

---

**TL;DR**: Download https://awscli.amazonaws.com/AWSCLIV2.msi and run it!

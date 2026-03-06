# Windows Setup Guide for OrchestRAI

## 🔧 Step-by-Step Setup for Windows

### Issue You're Facing
The error occurs because `pydantic-core` requires Rust compiler, but we can avoid this by using a virtual environment and installing compatible versions.

## ✅ Solution: Use Virtual Environment

### Step 1: Create Virtual Environment

Open PowerShell or Command Prompt in your project directory:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

**If you get execution policy error:**
```powershell
# Run this first (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\Activate.ps1
```

**Or use Command Prompt instead:**
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat
```

You should see `(venv)` at the start of your prompt.

### Step 2: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies (Fixed Version)

Instead of the current requirements.txt, install with compatible versions:

```powershell
# Install core dependencies first
pip install boto3==1.34.34
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install hypothesis==6.92.1
pip install python-dotenv==1.0.0

# Install pydantic with pre-built wheels (no Rust needed)
pip install pydantic==2.5.3 --only-binary :all:

# Install moto for testing
pip install moto==4.2.9

# Install CDK (for infrastructure)
pip install aws-cdk-lib==2.120.0
pip install constructs>=10.0.0
```

### Step 4: Run Tests

```powershell
# Run tests
pytest tests/ -v
```

## 🚀 Quick Setup Script

I'll create an automated script for you:

```powershell
# Save this as setup.ps1 and run it

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install boto3==1.34.34
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install hypothesis==6.92.1
pip install python-dotenv==1.0.0
pip install pydantic==2.5.3 --only-binary :all:
pip install moto==4.2.9
pip install aws-cdk-lib==2.120.0
pip install constructs>=10.0.0

# Run tests
pytest tests/ -v
```

## 📝 Alternative: Use requirements-windows.txt

I'll create a Windows-specific requirements file for you.


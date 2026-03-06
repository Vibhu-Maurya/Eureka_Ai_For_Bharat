# PowerShell Setup Script for OrchestRAI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OrchestRAI Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
Write-Host "[OK] pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

$packages = @(
    "boto3==1.34.34",
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
    "hypothesis==6.92.1",
    "python-dotenv==1.0.0",
    "pydantic==2.9.2",
    "moto==4.2.9",
    "aws-cdk-lib==2.120.0",
    "constructs>=10.0.0"
)

$i = 1
foreach ($package in $packages) {
    pip install $package -q
    Write-Host "[$i/$($packages.Count)] $package installed" -ForegroundColor Green
    $i++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[SUCCESS] Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Virtual environment is activated." -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run tests: pytest tests/ -v"
Write-Host "2. Deploy to AWS: cd infrastructure; cdk deploy --all"
Write-Host "3. Test API: python examples\test_upload.py <API_URL> <API_KEY>"
Write-Host ""
Write-Host "To activate virtual environment later:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To deactivate:" -ForegroundColor Yellow
Write-Host "  deactivate"
Write-Host ""

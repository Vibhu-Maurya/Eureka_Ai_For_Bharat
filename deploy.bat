@echo off
REM OrchestRAI Deployment Script

echo ========================================
echo OrchestRAI AWS Deployment
echo ========================================
echo.

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

echo Checking AWS credentials...
python -m awscli sts get-caller-identity >nul 2>&1

if errorlevel 1 (
    echo [ERROR] AWS credentials not configured or invalid.
    echo.
    echo Please run: .\aws_configure.bat
    echo.
    pause
    exit /b 1
)

echo [OK] AWS credentials verified
echo.

echo Checking CDK installation...
cdk --version
if errorlevel 1 (
    echo [ERROR] CDK not installed
    echo Please run: npm install -g aws-cdk
    pause
    exit /b 1
)
echo.

echo Checking Python dependencies...
python -c "import aws_cdk; print('CDK Python library: OK')"
if errorlevel 1 (
    echo [ERROR] CDK Python library not installed
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

echo ========================================
echo Step 1: CDK Bootstrap
echo ========================================
echo This prepares your AWS account for CDK deployments.
echo This only needs to be done once per account/region.
echo.
pause

cdk bootstrap

if errorlevel 1 (
    echo [ERROR] CDK bootstrap failed
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Bootstrap complete!
echo.

echo ========================================
echo Step 2: Deploy All Stacks
echo ========================================
echo This will deploy:
echo   - Storage Stack (S3 buckets, DynamoDB tables)
echo   - Compute Stack (Lambda functions, Step Functions)
echo   - API Stack (API Gateway, API Key)
echo.
echo This may take 10-15 minutes...
echo.
pause

cdk deploy --all --require-approval never

if errorlevel 1 (
    echo [ERROR] Deployment failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Deployment Complete!
echo ========================================
echo.
echo Your OrchestRAI system is now live on AWS!
echo.
echo Check the outputs above for:
echo   - API Gateway URL
echo   - API Key
echo.
echo To test the API:
echo   cd ..
echo   python examples\test_upload.py ^<API_URL^> ^<API_KEY^>
echo.

cd ..
pause

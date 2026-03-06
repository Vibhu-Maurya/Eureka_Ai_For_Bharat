"""Pytest configuration and fixtures."""
import pytest
import os

# Set AWS region before any imports
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for tests."""
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')
    monkeypatch.setenv('AWS_REGION', 'us-east-1')
    monkeypatch.setenv('UPLOADS_BUCKET', 'test-uploads-bucket')
    monkeypatch.setenv('CONTENT_BUCKET', 'test-content-bucket')
    monkeypatch.setenv('CONTENT_METADATA_TABLE', 'test-content-metadata')
    monkeypatch.setenv('WORKFLOW_STATE_TABLE', 'test-workflow-state')
    monkeypatch.setenv('SCRIPT_VERSIONS_TABLE', 'test-script-versions')
    monkeypatch.setenv('QUALITY_EVALUATIONS_TABLE', 'test-quality-evaluations')
    monkeypatch.setenv('STATE_MACHINE_ARN', 'arn:aws:states:us-east-1:123456789012:stateMachine:test')
    monkeypatch.setenv('BEDROCK_MODEL_ID', 'anthropic.claude-haiku-4-5-20251001-v1:0')


@pytest.fixture(scope='function')
def aws_credentials(monkeypatch):
    """Mock AWS credentials for moto."""
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SECURITY_TOKEN', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')

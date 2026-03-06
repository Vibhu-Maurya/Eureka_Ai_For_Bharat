"""AWS service client utilities."""
import boto3
import os
from typing import Optional


class AWSClients:
    """Singleton class for AWS service clients."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_clients()
        return cls._instance
    
    def _initialize_clients(self):
        """Initialize AWS service clients."""
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.transcribe = boto3.client('transcribe')
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.polly = boto3.client('polly')
        self.stepfunctions = boto3.client('stepfunctions')
        self.cloudwatch = boto3.client('cloudwatch')
        self.logs = boto3.client('logs')
    
    @staticmethod
    def get_table(table_name: str):
        """Get DynamoDB table resource."""
        clients = AWSClients()
        return clients.dynamodb.Table(table_name)
    
    @staticmethod
    def get_bucket_name(bucket_type: str) -> str:
        """Get S3 bucket name from environment."""
        env_var = f"ORCHESTRAI_{bucket_type.upper()}_BUCKET"
        bucket_name = os.environ.get(env_var)
        if not bucket_name:
            raise ValueError(f"Environment variable {env_var} not set")
        return bucket_name

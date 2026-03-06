"""Upload handler Lambda function."""
import json
import uuid
import os
import base64
import traceback
from datetime import datetime
from typing import Dict, Any
import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
stepfunctions = boto3.client('stepfunctions')

# Environment variables
UPLOADS_BUCKET = os.environ.get('UPLOADS_BUCKET', 'orchestrai-uploads')
CONTENT_METADATA_TABLE = os.environ.get('CONTENT_METADATA_TABLE', 'OrchestRAI-ContentMetadata')
STATE_MACHINE_ARN = os.environ.get('STATE_MACHINE_ARN')
WORKFLOW_STATE_TABLE = os.environ.get('WORKFLOW_STATE_TABLE', 'OrchestRAI-WorkflowState')

# Supported formats and constraints
SUPPORTED_VIDEO_FORMATS = ['mp4', 'mov', 'avi']
MIN_DURATION_MINUTES = 5
MAX_DURATION_MINUTES = 30
MAX_FILE_SIZE_MB = 500


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle content upload requests."""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract parameters (support both camelCase and snake_case)
        content_type = body.get('contentType') or body.get('content_type', 'video')
        target_languages = body.get('targetLanguages') or body.get('target_languages', ['en'])
        if isinstance(target_languages, str):
            target_languages = [target_languages]
        quality_threshold = body.get('qualityThreshold') or body.get('quality_threshold', 75)
        user_id = event.get('requestContext', {}).get('identity', {}).get('apiKey', 'anonymous')
        
        # Validate input
        if content_type == 'video':
            # Support both file upload and URL (accept both contentUrl and source_url)
            content_url = body.get('contentUrl') or body.get('source_url')
            if content_url:
                # URL-based upload (e.g., YouTube, S3)
                file_content = json.dumps({'url': content_url}).encode('utf-8')
                file_name = 'content_url.json'
                file_extension = 'json'
            elif 'file' in body:
                # Direct file upload
                file_content = base64.b64decode(body['file'])
                file_name = body.get('fileName', 'video.mp4')
                file_extension = file_name.split('.')[-1].lower()
            else:
                return error_response(400, "Missing required field: file, contentUrl, or source_url")
            
            # Only validate format for direct uploads
            if file_extension != 'json' and file_extension not in SUPPORTED_VIDEO_FORMATS:
                return error_response(
                    400,
                    f"Invalid file format. Supported formats: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
                )
            
            # Validate format
            if file_extension != 'json' and file_extension not in SUPPORTED_VIDEO_FORMATS:
                return error_response(
                    400,
                    f"Invalid file format. Supported formats: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
                )
            
            # Validate file size (skip for URLs)
            file_size = len(file_content)
            if file_extension != 'json' and file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                return error_response(413, f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB")
            
            # Validate duration (placeholder - would need actual video analysis)
            duration_minutes = body.get('durationMinutes', 10)
            if not (MIN_DURATION_MINUTES <= duration_minutes <= MAX_DURATION_MINUTES):
                return error_response(
                    400,
                    f"Invalid duration. Must be between {MIN_DURATION_MINUTES} and {MAX_DURATION_MINUTES} minutes"
                )
            
        elif content_type == 'text':
            # Support both 'content' and 'source_text' fields
            text_content = body.get('content') or body.get('source_text')
            if not text_content:
                return error_response(400, "Missing required field: content or source_text")
            
            file_content = text_content.encode('utf-8')
            file_name = 'article.txt'
            file_size = len(file_content)
            duration_minutes = None
            
        else:
            return error_response(400, "Invalid contentType. Must be 'video' or 'text'")
        
        # Generate unique IDs
        content_id = str(uuid.uuid4())
        workflow_id = str(uuid.uuid4())
        
        # Upload to S3
        s3_key = f"uploads/{content_id}/{file_name}"
        s3_client.put_object(
            Bucket=UPLOADS_BUCKET,
            Key=s3_key,
            Body=file_content
        )
        
        # Store metadata in DynamoDB
        metadata_table = dynamodb.Table(CONTENT_METADATA_TABLE)
        metadata_table.put_item(
            Item={
                'contentId': content_id,
                'userId': user_id,
                'uploadTimestamp': datetime.utcnow().isoformat(),
                'contentType': content_type,
                'sourceS3Key': s3_key,
                'sourceLanguage': body.get('sourceLanguage') or body.get('source_language', 'en'),
                'targetLanguages': target_languages,
                'qualityThreshold': quality_threshold,
                'stylePreferences': body.get('stylePreferences') or body.get('style_preferences', {}),
                'status': 'uploaded',
                'workflowId': workflow_id,
                'fileSize': file_size,
                'duration': duration_minutes
            }
        )
        # Also create an initial entry in the workflow state table so status
        # requests can observe the workflow immediately. This mirrors the
        # metadata table but lives in its own table for step-function updates.
        if WORKFLOW_STATE_TABLE:
            wf_table = dynamodb.Table(WORKFLOW_STATE_TABLE)
            wf_table.put_item(
                Item={
                    'workflowId': workflow_id,
                    'contentId': content_id,
                    'status': 'uploaded',
                    'currentStage': '',
                    'progress': 0,
                    'qualityScore': None,
                    'error': None,
                    'lastUpdateTime': datetime.utcnow().isoformat()
                }
            )
        
        # Initiate Step Functions workflow
        print(f"DEBUG: STATE_MACHINE_ARN = {STATE_MACHINE_ARN}")
        if STATE_MACHINE_ARN:
            try:
                print(f"DEBUG: Starting Step Functions execution with ARN: {STATE_MACHINE_ARN}")
                stepfunctions.start_execution(
                    stateMachineArn=STATE_MACHINE_ARN,
                    name=workflow_id,
                    input=json.dumps({
                        'contentId': content_id,
                        'workflowId': workflow_id,
                        's3Key': s3_key,
                        'contentType': content_type,
                        'targetLanguages': target_languages,
                        'qualityThreshold': quality_threshold,
                        'iterationCount': 0
                    })
                )
                print(f"DEBUG: Step Functions execution started successfully")
            except Exception as e:
                print(f"ERROR: Could not start Step Functions workflow: {str(e)}")
                print(f"ERROR: Exception type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                # Continue anyway - workflow can be started manually
        else:
            print(f"WARNING: STATE_MACHINE_ARN is not set in environment")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'workflowId': workflow_id,
                'contentId': content_id,
                'status': 'initiated',
                'estimatedCompletionTime': 300  # 5 minutes estimate
            })
        }
        
    except Exception as e:
        # Print stack trace for CloudWatch debugging
        print("Error processing upload:")
        traceback.print_exc()
        return error_response(500, f"Internal server error: {str(e)}")


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Generate error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'code': f'ERROR_{status_code}'
        })
    }

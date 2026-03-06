"""Video retrieval handler Lambda function."""
import json
import os
import traceback
from typing import Dict, Any
from decimal import Decimal
import boto3

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
FINAL_VIDEOS_TABLE = os.environ.get('FINAL_VIDEOS_TABLE', 'OrchestRAI-FinalVideos')
CONTENT_BUCKET = os.environ.get('CONTENT_BUCKET', 'orchestrai-content')
PRESIGNED_URL_EXPIRATION = 7 * 24 * 60 * 60  # 7 days


def decimal_to_number(obj):
    """Convert Decimal types to int or float for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_number(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_number(i) for i in obj]
    return obj


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve video download URLs."""
    try:
        # Extract video ID from path parameters
        video_id = event.get('pathParameters', {}).get('videoId')
        # Guard against None for queryStringParameters
        qparams = event.get('queryStringParameters') or {}
        language = qparams.get('language', 'en')
        
        if not video_id:
            return error_response(400, "Missing videoId parameter")
        
        # Query DynamoDB for video metadata
        videos_table = dynamodb.Table(FINAL_VIDEOS_TABLE)
        response = videos_table.get_item(
            Key={
                'videoId': video_id,
                'language': language
            }
        )
        
        # Log the DynamoDB response for debugging in CloudWatch
        print(f"DynamoDB get_item response for videoId={video_id}, language={language}: {response}")

        if 'Item' not in response:
            return error_response(404, "Video not found")
        
        video = response.get('Item')
        
        if not video:
            return error_response(404, "Video not found")
        
        # Safely get S3 keys with proper null checks
        video_s3_key = video.get('videoS3Key')
        subtitles_s3_key = video.get('subtitlesS3Key')
        
        if not video_s3_key:
            return error_response(400, "Video S3 key not available")
        
        # Generate fresh presigned URL for video
        video_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': CONTENT_BUCKET,
                'Key': video_s3_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        # Generate presigned URL for subtitles if available
        subtitle_url = None
        if subtitles_s3_key:
            subtitle_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': CONTENT_BUCKET,
                    'Key': subtitles_s3_key
                },
                ExpiresIn=PRESIGNED_URL_EXPIRATION
            )
        
        # Increment download count (only if table supports it)
        try:
            videos_table.update_item(
                Key={'videoId': video_id, 'language': language},
                UpdateExpression='SET downloadCount = if_not_exists(downloadCount, :zero) + :inc',
                ExpressionAttributeValues={':inc': 1, ':zero': 0}
            )
        except Exception as e:
            print(f"Warning: Could not update download count: {str(e)}")
            # Continue anyway - count update is not critical
        
        # Return video information
        response_body = decimal_to_number({
            'videoId': video_id,
            'videoUrl': video_url,
            'duration': video.get('duration'),
            'language': language,
            'qualityScore': video.get('qualityScore'),
            'metadata': {
                'resolution': video.get('resolution'),
                'createdAt': video.get('createdAt'),
                'downloadCount': video.get('downloadCount', 0) + 1
            }
        })
        
        # Only include subtitle URL if it's available
        if subtitle_url:
            response_body['subtitleUrl'] = subtitle_url
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        # Print full stack trace for CloudWatch debugging
        print("Error retrieving video:")
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

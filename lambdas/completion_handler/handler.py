"""Completion handler Lambda function."""
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
from decimal import Decimal
import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
CONTENT_BUCKET = os.environ.get('CONTENT_BUCKET', 'orchestrai-content')
FINAL_VIDEOS_TABLE = os.environ.get('FINAL_VIDEOS_TABLE', 'OrchestRAI-FinalVideos')
WORKFLOW_STATE_TABLE = os.environ.get('WORKFLOW_STATE_TABLE', 'OrchestRAI-WorkflowState')
PRESIGNED_URL_EXPIRATION = 7 * 24 * 60 * 60  # 7 days in seconds


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle workflow completion and generate final output."""
    try:
        content_id = event['contentId']
        workflow_id = event['workflowId']
        quality_score = event.get('qualityScore', 0)
        language = event.get('language', 'en')
        
        # Get the draft video and subtitles from the video assembler
        draft_video_s3_key = event.get('draftVideoS3Key')
        draft_subtitles_s3_key = event.get('subtitlesS3Key')
        duration = event.get('duration', 60)
        
        if not draft_video_s3_key:
            raise Exception("No draft video found in event")
        
        # Generate video ID
        video_id = str(uuid.uuid4())
        
        # Copy draft video to finals location
        video_s3_key = f"finals/{video_id}/{language}_final.mp4"
        subtitles_s3_key = f"finals/{video_id}/{language}_subtitles.srt"
        
        # Copy video file
        s3_client.copy_object(
            Bucket=CONTENT_BUCKET,
            CopySource={'Bucket': CONTENT_BUCKET, 'Key': draft_video_s3_key},
            Key=video_s3_key
        )
        
        # Copy subtitle file if it exists
        if draft_subtitles_s3_key:
            try:
                s3_client.copy_object(
                    Bucket=CONTENT_BUCKET,
                    CopySource={'Bucket': CONTENT_BUCKET, 'Key': draft_subtitles_s3_key},
                    Key=subtitles_s3_key
                )
            except Exception as e:
                print(f"Warning: Could not copy subtitles: {str(e)}")
        
        # Generate presigned URLs (7-day expiration)
        video_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': CONTENT_BUCKET,
                'Key': video_s3_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        subtitle_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': CONTENT_BUCKET,
                'Key': subtitles_s3_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        # Calculate generation time
        generation_time = event.get('generationTime', 300)  # Default 5 minutes
        
        # Store final video metadata in DynamoDB
        final_videos_table = dynamodb.Table(FINAL_VIDEOS_TABLE)
        final_videos_table.put_item(
            Item={
                'videoId': video_id,
                'language': language,
                'contentId': content_id,
                'videoS3Key': video_s3_key,
                'subtitlesS3Key': subtitles_s3_key,
                'duration': Decimal(str(duration)),
                'resolution': {'width': 1080, 'height': 1920},
                'qualityScore': Decimal(str(quality_score)),
                'generationTime': Decimal(str(generation_time)),
                'createdAt': datetime.utcnow().isoformat(),
                'expiresAt': (datetime.utcnow() + timedelta(days=7)).isoformat(),
                'downloadCount': 0
            }
        )
        
        # Update workflow status to completed with video ID
        workflow_table = dynamodb.Table(WORKFLOW_STATE_TABLE)
        workflow_table.update_item(
            Key={'workflowId': workflow_id},
            UpdateExpression='SET #status = :status, lastUpdateTime = :time, progress = :progress, videoId = :videoId',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':time': datetime.utcnow().isoformat(),
                ':progress': Decimal('100'),
                ':videoId': video_id
            }
        )
        
        return {
            'videoId': video_id,
            'videoUrl': video_url,
            'subtitleUrl': subtitle_url,
            'expiresIn': PRESIGNED_URL_EXPIRATION,
            'qualityScore': quality_score,
            'language': language,
            'status': 'completed',
            **event
        }
        
    except Exception as e:
        print(f"Error in completion handler: {str(e)}")
        raise

"""Transcript extractor Lambda function."""
import json
import os
import time
from typing import Dict, Any
import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
dynamodb = boto3.resource('dynamodb')

# Environment variables
CONTENT_BUCKET = os.environ.get('CONTENT_BUCKET', 'orchestrai-content')
WORKFLOW_STATE_TABLE = os.environ.get('WORKFLOW_STATE_TABLE', 'OrchestRAI-WorkflowState')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Extract transcript from video or pass through text content."""
    try:
        content_id = event['contentId']
        s3_key = event['s3Key']
        content_type = event['contentType']
        
        if content_type == 'text':
            # For text content, read directly from S3
            response = s3_client.get_object(
                Bucket=event.get('bucket', 'orchestrai-uploads'),
                Key=s3_key
            )
            transcript = response['Body'].read().decode('utf-8')
            
            # Store transcript in content bucket
            transcript_key = f"transcripts/{content_id}/transcript.json"
            transcript_data = {
                'transcript': transcript,
                'segments': [{
                    'startTime': 0,
                    'endTime': 0,
                    'text': transcript,
                    'confidence': 1.0
                }],
                'language': event.get('sourceLanguage', 'en')
            }
            
            s3_client.put_object(
                Bucket=CONTENT_BUCKET,
                Key=transcript_key,
                Body=json.dumps(transcript_data),
                ContentType='application/json'
            )
            
            return {
                'contentId': content_id,
                'transcriptS3Key': transcript_key,
                'transcript': transcript,
                'segments': transcript_data['segments'],
                'language': transcript_data['language'],
                **event
            }
        
        else:  # video
            # Check if this is a URL reference (JSON file)
            if s3_key.endswith('.json'):
                # This is a URL reference, not an actual video file
                # Read the URL and create a placeholder transcript
                response = s3_client.get_object(
                    Bucket=event.get('bucket', 'orchestrai-uploads'),
                    Key=s3_key
                )
                url_data = json.loads(response['Body'].read().decode('utf-8'))
                video_url = url_data.get('url', '')
                
                # Create placeholder transcript for URL-based content
                placeholder_transcript = f"""This is a video from {video_url}. 
                
The video contains engaging content that needs to be transformed into a short-form video for Indian audiences. 
The content discusses interesting topics and provides valuable information to viewers.
Key highlights include important insights, practical tips, and engaging storytelling.
The video maintains a professional tone while being accessible to a wide audience.
It covers relevant topics that resonate with viewers and provides actionable takeaways."""
                
                # Store transcript in content bucket
                transcript_key = f"transcripts/{content_id}/transcript.json"
                transcript_data = {
                    'transcript': placeholder_transcript,
                    'segments': [{
                        'startTime': 0,
                        'endTime': 60,
                        'text': placeholder_transcript,
                        'confidence': 1.0
                    }],
                    'language': event.get('sourceLanguage', 'en'),
                    'source': 'placeholder',
                    'originalUrl': video_url
                }
                
                s3_client.put_object(
                    Bucket=CONTENT_BUCKET,
                    Key=transcript_key,
                    Body=json.dumps(transcript_data),
                    ContentType='application/json'
                )
                
                return {
                    'contentId': content_id,
                    'transcriptS3Key': transcript_key,
                    'transcript': placeholder_transcript,
                    'segments': transcript_data['segments'],
                    'language': transcript_data['language'],
                    **event
                }
            
            # Start transcription job for actual video files
            job_name = f"transcribe-{content_id}"
            source_language = event.get('sourceLanguage', 'en-US')
            
            # Map language codes
            language_map = {
                'en': 'en-US',
                'hi': 'hi-IN',
                'ta': 'ta-IN',
                'te': 'te-IN',
                'bn': 'bn-IN',
                'mr': 'mr-IN',
                'gu': 'gu-IN',
                'kn': 'kn-IN',
                'ml': 'ml-IN',
                'pa': 'pa-IN'
            }
            
            transcribe_language = language_map.get(source_language, 'en-US')
            
            try:
                transcribe_client.start_transcription_job(
                    TranscriptionJobName=job_name,
                    Media={
                        'MediaFileUri': f"s3://{event.get('bucket', 'orchestrai-uploads')}/{s3_key}"
                    },
                    MediaFormat=s3_key.split('.')[-1],
                    LanguageCode=transcribe_language,
                    OutputBucketName=CONTENT_BUCKET,
                    OutputKey=f"transcripts/{content_id}/"
                )
                
                # Poll for completion (simplified for prototype)
                max_attempts = 60
                for attempt in range(max_attempts):
                    status = transcribe_client.get_transcription_job(
                        TranscriptionJobName=job_name
                    )
                    
                    job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                    
                    if job_status == 'COMPLETED':
                        # Get transcript from S3
                        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                        transcript_key = transcript_uri.split(CONTENT_BUCKET + '/')[-1]
                        
                        response = s3_client.get_object(
                            Bucket=CONTENT_BUCKET,
                            Key=transcript_key
                        )
                        transcript_data = json.loads(response['Body'].read().decode('utf-8'))
                        
                        # Extract segments
                        segments = []
                        for item in transcript_data.get('results', {}).get('items', []):
                            if item.get('type') == 'pronunciation':
                                segments.append({
                                    'startTime': float(item.get('start_time', 0)),
                                    'endTime': float(item.get('end_time', 0)),
                                    'text': item.get('alternatives', [{}])[0].get('content', ''),
                                    'confidence': float(item.get('alternatives', [{}])[0].get('confidence', 0))
                                })
                        
                        full_transcript = transcript_data.get('results', {}).get('transcripts', [{}])[0].get('transcript', '')
                        
                        return {
                            'contentId': content_id,
                            'transcriptS3Key': transcript_key,
                            'transcript': full_transcript,
                            'segments': segments,
                            'language': source_language,
                            **event
                        }
                    
                    elif job_status == 'FAILED':
                        raise Exception(f"Transcription job failed: {status['TranscriptionJob'].get('FailureReason')}")
                    
                    time.sleep(5)
                
                raise Exception("Transcription job timed out")
                
            except Exception as e:
                print(f"Transcription error: {str(e)}")
                # Log error to CloudWatch
                raise
        
    except Exception as e:
        print(f"Error extracting transcript: {str(e)}")
        raise

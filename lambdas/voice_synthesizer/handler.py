"""Voice synthesizer Lambda function using Amazon Polly."""
import json
import os
import uuid
from typing import Dict, Any
import boto3

# Initialize AWS clients
polly_client = boto3.client('polly')
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
CONTENT_BUCKET = os.environ.get('CONTENT_BUCKET', 'orchestrai-content')
TRANSLATIONS_TABLE = os.environ.get('TRANSLATIONS_TABLE', 'OrchestRAI-Translations')

# Language to voice mapping (Neural voices)
VOICE_MAP = {
    'hi': 'Kajal',  # Hindi
    'en': 'Joanna',  # English (US)
    'ta': 'Kajal',  # Tamil (use Hindi voice as fallback)
    'te': 'Kajal',  # Telugu (use Hindi voice as fallback)
    'bn': 'Kajal',  # Bengali (use Hindi voice as fallback)
    'mr': 'Kajal',  # Marathi (use Hindi voice as fallback)
    'gu': 'Kajal',  # Gujarati (use Hindi voice as fallback)
    'kn': 'Kajal',  # Kannada (use Hindi voice as fallback)
    'ml': 'Kajal',  # Malayalam (use Hindi voice as fallback)
    'pa': 'Kajal',  # Punjabi (use Hindi voice as fallback)
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Synthesize voice for translated scripts using Polly."""
    try:
        content_id = event['contentId']
        translations = event.get('translations', {})
        scene_plan = event.get('scenes', [])
        
        # Generate audio for each language
        audio_files = {}
        
        for language, translation in translations.items():
            try:
                # Combine all text for narration
                full_text = f"{translation['hook']}. "
                full_text += " ".join(translation['scenes'])
                full_text += f" {translation['cta']}"
                
                # Get appropriate voice for language
                voice_id = VOICE_MAP.get(language, 'Joanna')
                
                # Synthesize speech with retry logic
                max_retries = 3
                audio_content = None
                
                for attempt in range(max_retries):
                    try:
                        response = polly_client.synthesize_speech(
                            Text=full_text,
                            OutputFormat='mp3',
                            VoiceId=voice_id,
                            Engine='neural',
                            SampleRate='48000'
                        )
                        
                        audio_content = response['AudioStream'].read()
                        break
                        
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        print(f"Polly retry {attempt + 1}/{max_retries}: {str(e)}")
                        continue
                
                if not audio_content:
                    raise Exception(f"Failed to synthesize audio for {language}")
                
                # Store audio in S3
                audio_key = f"audio/{content_id}/{language}_v1.mp3"
                s3_client.put_object(
                    Bucket=CONTENT_BUCKET,
                    Key=audio_key,
                    Body=audio_content,
                    ContentType='audio/mpeg'
                )
                
                # Get audio duration (approximate based on text length)
                # Rough estimate: ~150 words per minute, ~2.5 words per second
                word_count = len(full_text.split())
                duration = word_count / 2.5
                
                audio_files[language] = {
                    'language': language,
                    's3Key': audio_key,
                    'duration': round(duration, 2),
                    'format': 'mp3',
                    'sampleRate': 48000
                }
                
                print(f"Generated audio for {language}: {audio_key}")
                
            except Exception as e:
                print(f"Error generating audio for {language}: {str(e)}")
                # Continue with other languages
                continue
        
        return {
            'contentId': content_id,
            'audioFiles': audio_files,
            **event
        }
        
    except Exception as e:
        print(f"Error in voice synthesizer: {str(e)}")
        raise

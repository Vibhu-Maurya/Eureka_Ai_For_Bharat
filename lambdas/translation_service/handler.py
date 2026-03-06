"""Translation service Lambda function using Amazon Bedrock."""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import boto3

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

# Environment variables
TRANSLATIONS_TABLE = os.environ.get('TRANSLATIONS_TABLE', 'OrchestRAI-Translations')
SCRIPT_VERSIONS_TABLE = os.environ.get('SCRIPT_VERSIONS_TABLE', 'OrchestRAI-ScriptVersions')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-haiku-4-5-20251001-v1:0')

# Supported languages
SUPPORTED_LANGUAGES = {
    'hi': 'Hindi',
    'en': 'English',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi'
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Translate script to target languages using Bedrock."""
    try:
        content_id = event['contentId']
        script_id = event['scriptId']
        script = event['script']
        source_language = event.get('sourceLanguage', 'en')
        target_languages = event.get('targetLanguages', ['hi', 'en'])
        
        # Load script from DynamoDB if not provided
        if not script:
            script_table = dynamodb.Table(SCRIPT_VERSIONS_TABLE)
            response = script_table.get_item(
                Key={'scriptId': script_id, 'version': event.get('version', 1)}
            )
            script = response.get('Item', {})
        
        # Translate to each target language
        translations = {}
        translation_id = str(uuid.uuid4())
        
        for target_lang in target_languages:
            if target_lang == source_language:
                # No translation needed for source language
                translations[target_lang] = {
                    'language': target_lang,
                    'hook': script['hook']['text'],
                    'scenes': [scene['text'] for scene in script['scenes']],
                    'cta': script['cta']['text'],
                    'culturalFlags': []
                }
                continue
            
            if target_lang not in SUPPORTED_LANGUAGES:
                print(f"Unsupported language: {target_lang}, skipping")
                continue
            
            # Translate using Bedrock
            try:
                translated = translate_script(script, source_language, target_lang)
                translations[target_lang] = translated
                
                # Store translation in DynamoDB
                trans_table = dynamodb.Table(TRANSLATIONS_TABLE)
                trans_table.put_item(
                    Item={
                        'translationId': translation_id,
                        'language': target_lang,
                        'contentId': content_id,
                        'scriptId': script_id,
                        'hook': translated['hook'],
                        'scenes': translated['scenes'],
                        'cta': translated['cta'],
                        'culturalFlags': translated['culturalFlags'],
                        'createdAt': datetime.utcnow().isoformat()
                    }
                )
                
            except Exception as e:
                print(f"Translation failed for {target_lang}: {str(e)}")
                # Continue with other languages
                continue
        
        return {
            'contentId': content_id,
            'scriptId': script_id,
            'translationId': translation_id,
            'translations': translations,
            'sourceLanguage': source_language,
            **event
        }
        
    except Exception as e:
        print(f"Error in translation service: {str(e)}")
        raise


def translate_script(script: Dict[str, Any], source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Translate script using Bedrock."""
    source_lang_name = SUPPORTED_LANGUAGES.get(source_lang, 'English')
    target_lang_name = SUPPORTED_LANGUAGES.get(target_lang, 'Hindi')
    
    # Build translation prompt
    prompt = f"""You are an expert translator specializing in {source_lang_name} to {target_lang_name} translation for video content.

Translate the following video script from {source_lang_name} to {target_lang_name}.

IMPORTANT REQUIREMENTS:
1. Preserve the meaning and intent of the original content
2. Maintain cultural appropriateness for Indian audiences
3. Use natural, conversational language
4. Keep idiomatic expressions culturally relevant
5. Flag any content that may be culturally inappropriate

Original Script:
Hook: {script['hook']['text']}
Scenes: {[scene['text'] for scene in script['scenes']]}
CTA: {script['cta']['text']}

Output format (JSON only):
{{
  "hook": "translated hook text",
  "scenes": ["translated scene 1", "translated scene 2", ...],
  "cta": "translated CTA text",
  "culturalFlags": ["flag1 if any", "flag2 if any"]
}}

If there are no cultural concerns, return an empty array for culturalFlags."""

    # Call Bedrock
    response = bedrock_runtime.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )
    
    response_body = json.loads(response['body'].read())
    translation_text = response_body['content'][0]['text']
    
    # Parse JSON from response
    translation_data = extract_json_from_response(translation_text)
    
    # Validate translation
    if 'hook' not in translation_data or 'scenes' not in translation_data or 'cta' not in translation_data:
        raise ValueError("Invalid translation response format")
    
    return {
        'language': target_lang,
        'hook': translation_data['hook'],
        'scenes': translation_data['scenes'],
        'cta': translation_data['cta'],
        'culturalFlags': translation_data.get('culturalFlags', [])
    }


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from Bedrock response."""
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    
    json_str = text[start:end]
    return json.loads(json_str)

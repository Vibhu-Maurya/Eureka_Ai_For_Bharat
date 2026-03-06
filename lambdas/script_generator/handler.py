"""Script generator Lambda function using Amazon Bedrock."""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any
import boto3

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

# Environment variables
SCRIPT_VERSIONS_TABLE = os.environ.get('SCRIPT_VERSIONS_TABLE', 'OrchestRAI-ScriptVersions')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Generate video script from transcript using Bedrock."""
    try:
        content_id = event['contentId']
        transcript = event['transcript']
        iteration_count = event.get('iterationCount', 0)
        feedback = event.get('feedback', {})
        
        # Construct Bedrock prompt
        prompt = build_script_prompt(transcript, feedback)
        
        # Call Bedrock with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = bedrock_runtime.invoke_model(
                    modelId=BEDROCK_MODEL_ID,
                    body=json.dumps({
                        "messages": [
                            {
                                "role": "user",
                                "content": [{"text": prompt}]
                            }
                        ],
                        "inferenceConfig": {
                            "maxTokens": 2000,
                            "temperature": 0.7
                        }
                    })
                )
                
                response_body = json.loads(response['body'].read())
                script_text = response_body['output']['message']['content'][0]['text']
                
                # Parse script JSON from response
                script_data = extract_json_from_response(script_text)
                
                # Validate script structure
                validate_script(script_data)
                
                # Generate script ID and store in DynamoDB
                script_id = str(uuid.uuid4())
                version = iteration_count + 1
                
                script_table = dynamodb.Table(SCRIPT_VERSIONS_TABLE)
                script_table.put_item(
                    Item={
                        'scriptId': script_id,
                        'version': version,
                        'contentId': content_id,
                        'hook': script_data['hook'],
                        'scenes': script_data['scenes'],
                        'cta': script_data['cta'],
                        'totalDuration': calculate_total_duration(script_data),
                        'createdAt': datetime.utcnow().isoformat(),
                        'iterationCount': iteration_count,
                        'appliedFeedback': feedback.get('suggestions', [])
                    }
                )
                
                return {
                    'contentId': content_id,
                    'scriptId': script_id,
                    'script': script_data,
                    'version': version,
                    **event
                }
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                continue
        
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        raise


def build_script_prompt(transcript: str, feedback: Dict[str, Any]) -> str:
    """Build Bedrock prompt for script generation."""
    feedback_section = ""
    if feedback:
        feedback_section = f"""
Previous Feedback:
Weaknesses: {', '.join(feedback.get('weaknesses', []))}
Suggestions: {', '.join(feedback.get('suggestions', []))}

Please address these issues in the new script.
"""
    
    prompt = f"""You are an expert video script writer specializing in short-form content for Indian audiences.

Analyze the following transcript and create an engaging 60-second video script.

Transcript:
{transcript[:2000]}  # Limit transcript length

Requirements:
- Create a compelling 3-second hook that grabs attention
- Identify 3-5 key highlights from the content
- Ensure cultural appropriateness for Indian audiences
- End with a clear call-to-action
- Total duration: 60 seconds
- Use simple, conversational language

{feedback_section}

Output format (JSON only, no other text):
{{
  "hook": {{"text": "...", "duration": 3}},
  "scenes": [
    {{"text": "...", "duration": 15}},
    {{"text": "...", "duration": 15}},
    {{"text": "...", "duration": 15}}
  ],
  "cta": {{"text": "...", "duration": 3}}
}}"""
    
    return prompt


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from Bedrock response."""
    # Find JSON in response
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    
    json_str = text[start:end]
    return json.loads(json_str)


def validate_script(script: Dict[str, Any]) -> None:
    """Validate script structure."""
    required_fields = ['hook', 'scenes', 'cta']
    for field in required_fields:
        if field not in script:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(script['scenes'], list) or len(script['scenes']) == 0:
        raise ValueError("Scenes must be a non-empty list")
    
    # Validate duration
    total_duration = calculate_total_duration(script)
    if not (30 <= total_duration <= 90):
        raise ValueError(f"Total duration {total_duration}s must be between 30 and 90 seconds")


def calculate_total_duration(script: Dict[str, Any]) -> float:
    """Calculate total script duration."""
    total = script['hook'].get('duration', 0)
    total += sum(scene.get('duration', 0) for scene in script['scenes'])
    total += script['cta'].get('duration', 0)
    return total
# Updated: 03-03-2026 16:15:17.60 
# Updated: 03-03-2026 16:28:30.39 
# Updated: 03-03-2026 17:38:15.92 

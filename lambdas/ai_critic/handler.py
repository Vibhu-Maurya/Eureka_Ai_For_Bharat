"""AI Critic Lambda function for quality evaluation."""
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
QUALITY_EVALUATIONS_TABLE = os.environ.get('QUALITY_EVALUATIONS_TABLE', 'OrchestRAI-QualityEvaluations')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Evaluate video quality using Bedrock."""
    try:
        content_id = event['contentId']
        script = event.get('script', {})
        transcript = event.get('transcript', '')
        iteration_count = event.get('iterationCount', 0)
        
        # Build evaluation prompt
        prompt = build_evaluation_prompt(transcript, script)
        
        # Call Bedrock
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
                        "maxTokens": 1500,
                        "temperature": 0.7
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            evaluation_text = response_body['output']['message']['content'][0]['text']
            
            # Parse evaluation JSON
            evaluation_data = extract_json_from_response(evaluation_text)
            
            # Validate scores
            scores = evaluation_data['scores']
            for key, value in scores.items():
                if not (0 <= value <= 100):
                    raise ValueError(f"Score {key} must be between 0 and 100")
            
            # Calculate weighted overall score
            overall_score = (
                scores['semanticAlignment'] * 0.4 +
                scores['pacing'] * 0.25 +
                scores['readability'] * 0.20 +
                scores['culturalAppropriateness'] * 0.15
            )
            
            # Store evaluation
            evaluation_id = str(uuid.uuid4())
            eval_table = dynamodb.Table(QUALITY_EVALUATIONS_TABLE)
            eval_table.put_item(
                Item={
                    'evaluationId': evaluation_id,
                    'contentId': content_id,
                    'scores': scores,
                    'overallScore': round(overall_score, 2),
                    'feedback': evaluation_data['feedback'],
                    'iterationCount': iteration_count,
                    'timestamp': datetime.utcnow().isoformat(),
                    'language': event.get('language', 'en')
                }
            )
            
            return {
                'contentId': content_id,
                'evaluationId': evaluation_id,
                'qualityScore': round(overall_score, 2),
                'scores': scores,
                'criticFeedback': evaluation_data['feedback'],
                'iterationCount': iteration_count,
                **event
            }
            
        except Exception as e:
            print(f"Bedrock evaluation error: {str(e)}")
            # Assign default failing score on error
            return {
                'contentId': content_id,
                'evaluationId': str(uuid.uuid4()),
                'qualityScore': 0,
                'scores': {
                    'semanticAlignment': 0,
                    'pacing': 0,
                    'readability': 0,
                    'culturalAppropriateness': 0
                },
                'criticFeedback': {
                    'strengths': [],
                    'weaknesses': ['Evaluation failed'],
                    'suggestions': ['Retry generation'],
                    'criticalIssues': [str(e)]
                },
                'iterationCount': iteration_count,
                **event
            }
        
    except Exception as e:
        print(f"Error in AI critic: {str(e)}")
        raise


def build_evaluation_prompt(transcript: str, script: Dict[str, Any]) -> str:
    """Build evaluation prompt for Bedrock."""
    prompt = f"""You are an expert video quality evaluator specializing in short-form content for Indian audiences.

Evaluate the following video script based on these criteria:

Original Content Summary:
{transcript[:1000]}

Generated Script:
Hook: {script.get('hook', {}).get('text', '')}
Scenes: {[s.get('text', '') for s in script.get('scenes', [])]}
CTA: {script.get('cta', {}).get('text', '')}

Evaluate on a scale of 0-100:

1. Semantic Alignment: Does the script accurately represent the original content?
2. Pacing: Is the script engaging with good rhythm and flow?
3. Readability: Are the text segments clear and easy to understand?
4. Cultural Appropriateness: Is the content suitable for Indian audiences?

Provide:
- Numerical scores for each criterion
- Specific strengths and weaknesses
- Actionable suggestions for improvement
- Any critical issues that must be addressed

Output format (JSON only):
{{
  "scores": {{
    "semanticAlignment": 85,
    "pacing": 70,
    "readability": 90,
    "culturalAppropriateness": 95
  }},
  "feedback": {{
    "strengths": ["Clear messaging", "Good hook"],
    "weaknesses": ["Scene 2 too fast"],
    "suggestions": ["Slow down scene 2", "Add more context"],
    "criticalIssues": []
  }}
}}"""
    
    return prompt


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from Bedrock response."""
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    
    json_str = text[start:end]
    return json.loads(json_str)
# Updated: 03-03-2026 16:15:17.60 
# Updated: 03-03-2026 16:28:30.39 
# Updated: 03-03-2026 17:38:15.92 

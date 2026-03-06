"""Scene planner Lambda function using Amazon Bedrock."""
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
SCENE_PLANS_TABLE = os.environ.get('SCENE_PLANS_TABLE', 'OrchestRAI-ScenePlans')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-haiku-4-5-20251001-v1:0')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Generate scene plan from script using Bedrock."""
    try:
        content_id = event['contentId']
        script_id = event['scriptId']
        script = event['script']
        source_video_s3_key = event.get('s3Key', '')
        
        # Build scene planning prompt
        prompt = build_scene_planning_prompt(script)
        
        # Call Bedrock with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
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
                scene_plan_text = response_body['content'][0]['text']
                
                # Parse scene plan JSON
                scene_plan_data = extract_json_from_response(scene_plan_text)
                
                # Validate and enrich scene plan
                scenes = process_scene_plan(scene_plan_data, script)
                
                # Store scene plan in DynamoDB
                scene_plan_id = str(uuid.uuid4())
                scene_plans_table = dynamodb.Table(SCENE_PLANS_TABLE)
                scene_plans_table.put_item(
                    Item={
                        'scenePlanId': scene_plan_id,
                        'contentId': content_id,
                        'scriptId': script_id,
                        'scenes': scenes,
                        'createdAt': datetime.utcnow().isoformat()
                    }
                )
                
                return {
                    'contentId': content_id,
                    'scriptId': script_id,
                    'scenePlanId': scene_plan_id,
                    'scenes': scenes,
                    **event
                }
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # last attempt failed, log and return a simple fallback plan instead of bubbling error
                    print(f"Scene planner failed after {max_retries} attempts: {str(e)}")
                    # create basic scenes from script text
                    scenes = []
                    for i, scene in enumerate(script.get('scenes', [])):
                        scenes.append({
                            'sceneNumber': i + 1,
                            'visualDescription': scene.get('text', f"Scene {i+1}"),
                            'sourceTimestamp': {'start': 0, 'end': scene.get('duration', 10)},
                            'assetType': 'text_overlay',
                            'transition': 'cut' if i == 0 else 'fade',
                            'duration': scene.get('duration', 10),
                        })
                    scene_plan_id = str(uuid.uuid4())
                    scene_plans_table = dynamodb.Table(SCENE_PLANS_TABLE)
                    scene_plans_table.put_item(
                        Item={
                            'scenePlanId': scene_plan_id,
                            'contentId': content_id,
                            'scriptId': script_id,
                            'scenes': scenes,
                            'createdAt': datetime.utcnow().isoformat()
                        }
                    )
                    return {
                        'contentId': content_id,
                        'scriptId': script_id,
                        'scenePlanId': scene_plan_id,
                        'scenes': scenes,
                        **event
                    }
                print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                # Simplify prompt for retry
                prompt = build_simplified_scene_planning_prompt(script)
                continue
        
    except Exception as e:
        print(f"Error in scene planner: {str(e)}")
        raise


def build_scene_planning_prompt(script: Dict[str, Any]) -> str:
    """Build Bedrock prompt for scene planning."""
    prompt = f"""You are an expert video director specializing in short-form content.

Create a detailed scene plan for the following video script.

Script:
Hook: {script['hook']['text']} (Duration: {script['hook']['duration']}s)
Scenes: {[(i+1, scene['text'], scene['duration']) for i, scene in enumerate(script['scenes'])]}
CTA: {script['cta']['text']} (Duration: {script['cta']['duration']}s)

For each scene, provide:
1. Scene number (sequential starting from 1)
2. Visual description (what should be shown)
3. Source timestamp (start and end time in seconds from original video, estimate based on content)
4. Asset type (video_clip, text_overlay, or image)
5. Transition type (cut, fade, or dissolve)
6. Duration (from script)

Output format (JSON only):
{{
  "scenes": [
    {{
      "sceneNumber": 1,
      "visualDescription": "Opening shot with engaging visual",
      "sourceTimestamp": {{"start": 0, "end": 3}},
      "assetType": "video_clip",
      "transition": "fade",
      "duration": 3,
      "textOverlay": {{"text": "Hook text", "position": "bottom", "style": "bold", "fontSize": 24}}
    }},
    ...
  ]
}}"""
    
    return prompt


def build_simplified_scene_planning_prompt(script: Dict[str, Any]) -> str:
    """Build simplified prompt for retry."""
    prompt = f"""Create a simple scene plan with visual descriptions for this script:

{json.dumps(script, indent=2)}

Output JSON with scenes array containing: sceneNumber, visualDescription, sourceTimestamp, assetType, transition, duration."""
    
    return prompt


def process_scene_plan(scene_plan_data: Dict[str, Any], script: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process and validate scene plan."""
    scenes = scene_plan_data.get('scenes', [])
    
    # Ensure sequential scene numbers
    for i, scene in enumerate(scenes):
        scene['sceneNumber'] = i + 1
        
        # Validate required fields
        if 'visualDescription' not in scene:
            scene['visualDescription'] = f"Scene {i + 1}"
        
        if 'sourceTimestamp' not in scene:
            # Estimate timestamps based on scene order
            start_time = sum(s.get('duration', 0) for s in scenes[:i])
            duration = scene.get('duration', 10)
            scene['sourceTimestamp'] = {'start': start_time, 'end': start_time + duration}
        
        if 'assetType' not in scene:
            scene['assetType'] = 'video_clip'
        
        if 'transition' not in scene:
            scene['transition'] = 'cut' if i == 0 else 'fade'
        
        if 'duration' not in scene:
            # Get duration from script
            if i < len(script.get('scenes', [])):
                scene['duration'] = script['scenes'][i].get('duration', 10)
            else:
                scene['duration'] = 10
    
    return scenes


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from Bedrock response."""
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    
    json_str = text[start:end]
    return json.loads(json_str)

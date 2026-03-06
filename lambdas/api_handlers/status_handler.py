"""Status handler Lambda function."""
import json
import os
import traceback
from typing import Dict, Any
from decimal import Decimal
import boto3
stepfunctions = boto3.client('stepfunctions')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
WORKFLOW_STATE_TABLE = os.environ.get('WORKFLOW_STATE_TABLE', 'OrchestRAI-WorkflowState')
CONTENT_METADATA_TABLE = os.environ.get('CONTENT_METADATA_TABLE', 'OrchestRAI-ContentMetadata')


from datetime import datetime

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
    """Get workflow status."""
    try:
        # Extract workflow ID from path parameters
        workflow_id = event.get('pathParameters', {}).get('workflowId')
        
        if not workflow_id:
            return error_response(400, "Missing workflowId parameter")
        
        # First, try to get status from WORKFLOW_STATE_TABLE (updated by Step Functions)
        workflow_state_table = dynamodb.Table(WORKFLOW_STATE_TABLE)
        
        try:
            workflow_state_response = workflow_state_table.get_item(Key={'workflowId': workflow_id})
            if 'Item' in workflow_state_response:
                workflow = workflow_state_response['Item']
                status_val = workflow.get('status', 'unknown')
                # if still uploaded, check Step Functions for execution outcome
                if status_val == 'uploaded':
                    # executions are named by workflowId
                    try:
                        # list executions and find one with matching name
                        sm_arn = os.environ.get('STEP_FUNCTIONS_ARN')
                        if sm_arn:
                            exe_list = stepfunctions.list_executions(
                                stateMachineArn=sm_arn
                            ).get('executions', [])
                            for ex in exe_list:
                                if ex.get('name') == workflow_id:
                                    exec_status = ex.get('status')
                                    if exec_status and exec_status != 'RUNNING':
                                        mapped = exec_status.lower()
                                        workflow_state_table.update_item(
                                            Key={'workflowId': workflow_id},
                                            UpdateExpression='SET #status = :s, lastUpdateTime = :t',
                                            ExpressionAttributeNames={'#status': 'status'},
                                            ExpressionAttributeValues={
                                                ':s': mapped,
                                                ':t': datetime.utcnow().isoformat()
                                            }
                                        )
                                        status_val = mapped
                                        workflow['status'] = status_val
                                    break
                    except Exception as sx:
                        print(f"Error checking step function execution: {sx}")
                        # ignore errors

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(decimal_to_number({
                        'workflowId': workflow_id,
                        'status': status_val,
                        'currentStage': workflow.get('currentStage', ''),
                        'progress': workflow.get('progress', 0),
                        'qualityScore': workflow.get('qualityScore'),
                        'videoId': workflow.get('videoId'),
                        'error': workflow.get('error')
                    }))
                }
        except Exception as e:
            print(f"Note: Could not fetch from WORKFLOW_STATE_TABLE: {str(e)}")
            # Fall through to check ContentMetadata table
        
        # Fallback to CONTENT_METADATA_TABLE for initial status  
        metadata_table = dynamodb.Table(CONTENT_METADATA_TABLE)
        
        # Scan for the item with matching workflowId (since it's not the primary key)
        response = metadata_table.scan(
            FilterExpression='workflowId = :workflow_id',
            ExpressionAttributeValues={':workflow_id': workflow_id}
        )
        
        items = response.get('Items', [])
        if not items:
            return error_response(404, "Workflow not found")
        
        workflow = items[0]
        
        # Return workflow status
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(decimal_to_number({
                'workflowId': workflow_id,
                'status': workflow.get('status', 'unknown'),
                'currentStage': workflow.get('currentStage', ''),
                'progress': workflow.get('progress', 0),
                'qualityScore': workflow.get('qualityScore'),
                'videoId': workflow.get('videoId'),
                'error': workflow.get('error')
            }))
        }
        
    except Exception as e:
        # Print stack trace for CloudWatch
        print("Error getting workflow status:")
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

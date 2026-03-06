import boto3, json

db=boto3.client('dynamodb', region_name='us-east-1')
workflow_id='5c78b875-e4eb-47de-8e07-1029d6bd36af'
resp=db.get_item(TableName='OrchestRAI-WorkflowState', Key={'workflowId':{'S':workflow_id}})
print(json.dumps(resp, indent=2))

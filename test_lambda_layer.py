"""Test script to check what's in the Lambda layer."""
import json

# Create a test payload that will make the Lambda list /opt/bin contents
test_payload = {
    "test": True,
    "contentId": "test-content-id",
    "audioFiles": {},
    "scenes": [],
    "script": {"hook": {"text": "test", "duration": 3}, "scenes": [], "cta": {"text": "test", "duration": 3}}
}

with open('test_lambda_payload.json', 'w') as f:
    json.dump(test_payload, f)

print("Created test_lambda_payload.json")
print("\nTo test, run:")
print("C:\\Python313\\python.exe -m awscli lambda invoke --function-name OrchestRAIComputeStack-VideoAssembler2FE6ABF1-dCrVWB22taM7 --payload file://test_lambda_payload.json --region us-east-1 test_response.json")
print("\nThen check test_response.json for the error message")

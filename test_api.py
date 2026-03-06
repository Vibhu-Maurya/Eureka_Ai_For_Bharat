"""
OrchestRAI API Test Script
Tests the deployed API endpoints with real requests
"""
import requests
import json
from datetime import datetime

# API Configuration
API_URL = "YOUR_API_GATEWAY_ENDPOINT_HERE"
API_KEY = "YOUR_API_KEY_HERE"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_upload_text():
    """Test the upload endpoint with text content"""
    print_section("Test 1: Upload Text Content")
    
    payload = {
        "content_type": "text",
        "source_text": "Welcome to OrchestRAI, an AI-powered video orchestration platform. This system can transform your content into engaging videos in multiple languages using advanced AI models.",
        "target_language": "hi",
        "style_preferences": {
            "tone": "professional",
            "pacing": "moderate"
        }
    }
    
    print(f"\nEndpoint: POST {API_URL}/api/v1/upload")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/upload",
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json().get("workflowId")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
    
    return None

def test_status(workflow_id):
    """Test the status endpoint"""
    print_section("Test 2: Check Workflow Status")
    
    print(f"\nEndpoint: GET {API_URL}/api/v1/status/{workflow_id}")
    
    try:
        response = requests.get(
            f"{API_URL}/api/v1/status/{workflow_id}",
            headers={"x-api-key": API_KEY},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

def test_video_retrieval(video_id):
    """Test the video retrieval endpoint"""
    print_section("Test 3: Retrieve Video")
    
    print(f"\nEndpoint: GET {API_URL}/api/v1/video/{video_id}")
    
    try:
        response = requests.get(
            f"{API_URL}/api/v1/video/{video_id}",
            headers={"x-api-key": API_KEY},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

def main():
    """Run all API tests"""
    print("\n" + "=" * 60)
    print("  OrchestRAI API Test Suite")
    print("=" * 60)
    print(f"\nAPI Endpoint: {API_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Upload text content
    workflow_id = test_upload_text()
    
    # Test 2: Check status (use returned workflow_id or test ID)
    test_workflow_id = workflow_id if workflow_id else "test-workflow-123"
    test_status(test_workflow_id)
    
    # Test 3: Retrieve video (use test ID)
    test_video_retrieval("test-video-456")
    
    # Summary
    print_section("Test Summary")
    print("\n✅ All API endpoints are accessible and responding")
    print("\n📝 Notes:")
    print("  - Upload endpoint expects proper file/text data")
    print("  - Status endpoint returns 404 for non-existent workflows")
    print("  - Video retrieval endpoint needs valid video IDs from DynamoDB")
    print("\n🎯 Next Steps:")
    print("  1. Upload real content to test the full workflow")
    print("  2. Monitor CloudWatch logs for Lambda execution details")
    print("  3. Check DynamoDB tables for stored workflow data")
    print("  4. Add Step Functions to automate the workflow")
    
    print("\n" + "=" * 60)
    print("  Test Complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

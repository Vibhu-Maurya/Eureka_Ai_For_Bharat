"""Example script to test OrchestRAI API."""
import requests
import json
import base64
import time
import sys


def upload_text_content(api_url: str, api_key: str):
    """Upload text content for processing."""
    print("📝 Uploading text content...")
    
    payload = {
        "contentType": "text",
        "content": """
        Artificial Intelligence is transforming how we create content. 
        With AI-powered tools, creators can now automate video editing, 
        generate scripts, and even translate content into multiple languages. 
        This technology is making content creation more accessible and efficient 
        for everyone, from individual creators to large enterprises.
        """,
        "sourceLanguage": "en",
        "targetLanguages": ["hi", "ta"],
        "qualityThreshold": 75
    }
    
    response = requests.post(
        f"{api_url}/api/v1/upload",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful!")
        print(f"   Workflow ID: {result['workflowId']}")
        print(f"   Content ID: {result['contentId']}")
        print(f"   Status: {result['status']}")
        print(f"   Estimated completion: {result['estimatedCompletionTime']}s")
        return result['workflowId']
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def check_workflow_status(api_url: str, api_key: str, workflow_id: str):
    """Check workflow status."""
    print(f"\n🔍 Checking workflow status...")
    
    response = requests.get(
        f"{api_url}/api/v1/status/{workflow_id}",
        headers={"x-api-key": api_key}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status retrieved:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Progress: {result.get('progress', 0)}%")
        return result
    else:
        print(f"❌ Status check failed: {response.status_code}")
        return None


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python test_upload.py <API_URL> <API_KEY>")
        print("Example: python test_upload.py https://abc123.execute-api.us-east-1.amazonaws.com your-api-key")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    api_key = sys.argv[2]
    
    print("🚀 OrchestRAI API Test")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"API Key: {api_key[:10]}...")
    print("=" * 50)
    print()
    
    # Upload content
    workflow_id = upload_text_content(api_url, api_key)
    
    if workflow_id:
        # Wait a bit
        print("\n⏳ Waiting 10 seconds before checking status...")
        time.sleep(10)
        
        # Check status
        check_workflow_status(api_url, api_key, workflow_id)
        
        print("\n💡 Tips:")
        print("   - Monitor workflow in Step Functions console")
        print("   - Check CloudWatch logs for detailed execution info")
        print("   - Use AWS Console to view DynamoDB tables")


if __name__ == "__main__":
    main()

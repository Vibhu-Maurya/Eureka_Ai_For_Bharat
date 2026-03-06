"""Unit tests for upload handler."""
import pytest
import json
import base64
from unittest.mock import Mock, patch
import sys
import os

# Add project root and lambdas to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'lambdas', 'upload_handler'))

# Import from upload handler specifically
from lambdas.upload_handler.handler import lambda_handler, error_response


class TestUploadHandler:
    """Test upload handler Lambda function."""
    
    @patch('lambdas.upload_handler.handler.stepfunctions')
    @patch('lambdas.upload_handler.handler.dynamodb')
    @patch('lambdas.upload_handler.handler.s3_client')
    def test_valid_video_upload(self, mock_s3, mock_ddb, mock_sfn):
        """Test valid video upload."""
        # Mock DynamoDB table
        mock_table = Mock()
        mock_ddb.Table.return_value = mock_table
        
        # Create test event
        event = {
            'body': json.dumps({
                'contentType': 'video',
                'file': base64.b64encode(b'fake video content').decode('utf-8'),
                'fileName': 'test.mp4',
                'durationMinutes': 10,
                'targetLanguages': ['hi', 'en'],
                'qualityThreshold': 75
            })
        }
        
        # Call handler
        response = lambda_handler(event, None)
        
        # Assertions
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'workflowId' in body
        assert 'contentId' in body
        assert body['status'] == 'initiated'
        
        # Verify S3 upload was called
        mock_s3.put_object.assert_called_once()
        
        # Verify DynamoDB write was called
        mock_table.put_item.assert_called_once()
    
    @patch('lambdas.upload_handler.handler.dynamodb')
    @patch('lambdas.upload_handler.handler.s3_client')
    def test_valid_text_upload(self, mock_s3, mock_ddb):
        """Test valid text article upload."""
        mock_table = Mock()
        mock_ddb.Table.return_value = mock_table
        
        event = {
            'body': json.dumps({
                'contentType': 'text',
                'content': 'This is a test article about technology.',
                'sourceLanguage': 'en',
                'targetLanguages': ['hi']
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'workflowId' in body
    
    def test_invalid_format(self):
        """Test invalid file format rejection."""
        event = {
            'body': json.dumps({
                'contentType': 'video',
                'file': base64.b64encode(b'fake content').decode('utf-8'),
                'fileName': 'test.exe',
                'durationMinutes': 10
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'format' in body['error'].lower()
    
    def test_invalid_duration(self):
        """Test invalid duration rejection."""
        event = {
            'body': json.dumps({
                'contentType': 'video',
                'file': base64.b64encode(b'fake content').decode('utf-8'),
                'fileName': 'test.mp4',
                'durationMinutes': 2  # Too short
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'duration' in body['error'].lower()
    
    def test_missing_required_field(self):
        """Test missing required field."""
        event = {
            'body': json.dumps({
                'contentType': 'video'
                # Missing 'file' field
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'file' in body['error'].lower()
    
    def test_error_response_format(self):
        """Test error response format."""
        response = error_response(400, "Test error message")
        
        assert response['statusCode'] == 400
        assert 'Content-Type' in response['headers']
        body = json.loads(response['body'])
        assert body['error'] == "Test error message"
        assert 'code' in body


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

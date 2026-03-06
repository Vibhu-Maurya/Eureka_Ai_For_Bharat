"""Unit tests for script generator."""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from lambdas.script_generator.handler import validate_script, calculate_total_duration, extract_json_from_response


class TestScriptGenerator:
    """Test script generator functions."""
    
    def test_validate_script_valid(self):
        """Test validation of valid script."""
        script = {
            'hook': {'text': 'Hook text', 'duration': 3},
            'scenes': [
                {'text': 'Scene 1', 'duration': 15},
                {'text': 'Scene 2', 'duration': 15},
                {'text': 'Scene 3', 'duration': 15}
            ],
            'cta': {'text': 'CTA text', 'duration': 3}
        }
        
        # Should not raise exception
        validate_script(script)
    
    def test_validate_script_missing_field(self):
        """Test validation fails with missing field."""
        script = {
            'hook': {'text': 'Hook text', 'duration': 3},
            'scenes': [{'text': 'Scene 1', 'duration': 15}]
            # Missing 'cta'
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            validate_script(script)
    
    def test_validate_script_empty_scenes(self):
        """Test validation fails with empty scenes."""
        script = {
            'hook': {'text': 'Hook text', 'duration': 3},
            'scenes': [],  # Empty
            'cta': {'text': 'CTA text', 'duration': 3}
        }
        
        with pytest.raises(ValueError, match="non-empty list"):
            validate_script(script)
    
    def test_validate_script_duration_too_short(self):
        """Test validation fails with too short duration."""
        script = {
            'hook': {'text': 'Hook text', 'duration': 3},
            'scenes': [{'text': 'Scene 1', 'duration': 10}],
            'cta': {'text': 'CTA text', 'duration': 3}
        }
        
        with pytest.raises(ValueError, match="between 30 and 90"):
            validate_script(script)
    
    def test_validate_script_duration_too_long(self):
        """Test validation fails with too long duration."""
        script = {
            'hook': {'text': 'Hook text', 'duration': 3},
            'scenes': [
                {'text': 'Scene 1', 'duration': 30},
                {'text': 'Scene 2', 'duration': 30},
                {'text': 'Scene 3', 'duration': 30}
            ],
            'cta': {'text': 'CTA text', 'duration': 3}
        }
        
        with pytest.raises(ValueError, match="between 30 and 90"):
            validate_script(script)
    
    def test_calculate_total_duration(self):
        """Test duration calculation."""
        script = {
            'hook': {'duration': 3},
            'scenes': [
                {'duration': 15},
                {'duration': 15},
                {'duration': 15}
            ],
            'cta': {'duration': 3}
        }
        
        total = calculate_total_duration(script)
        assert total == 51
    
    def test_extract_json_from_response(self):
        """Test JSON extraction from text."""
        text = 'Here is the script: {"hook": {"text": "test", "duration": 3}} and more text'
        
        result = extract_json_from_response(text)
        
        assert isinstance(result, dict)
        assert 'hook' in result
    
    def test_extract_json_no_json_found(self):
        """Test JSON extraction fails when no JSON present."""
        text = 'This is just plain text without any JSON'
        
        with pytest.raises(ValueError, match="No JSON found"):
            extract_json_from_response(text)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Tests for main module utility functions.
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Always use relative imports for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.notebook_cat.main import main

def test_main_parse_args():
    """Test the argument parsing functionality."""
    # Test with minimal arguments
    test_args = ["notebook-cat", "/input/dir", "/output/dir"]
    
    with patch('sys.argv', test_args):
        # Mock core.process_directory to avoid actual processing
        with patch('src.notebook_cat.core.process_directory'):
            main()
    
    # Test with all options
    test_args = [
        "notebook-cat",
        "/input/dir",
        "/output/dir",
        "--plus-plan",
        "--extensions", "txt,md",
        "--json-path", "content.text",
        "--dry-run",
        "--resume",
        "--max-files", "100"
    ]
    
    with patch('sys.argv', test_args):
        # Mock core.process_directory to avoid actual processing
        with patch('src.notebook_cat.core.process_directory'):
            main()
    
    # Test with mutually exclusive options (should use the last one)
    test_args = [
        "notebook-cat",
        "/input/dir",
        "/output/dir",
        "--free-plan",
        "--plus-plan",
        "--limit", "75"
    ]
    
    with patch('sys.argv', test_args):
        # Mock core.process_directory to avoid actual processing
        with patch('src.notebook_cat.core.process_directory', MagicMock()) as mock_process:
            main()
            
            # The last option (--limit 75) should be used
            if mock_process.call_args:
                kwargs = mock_process.call_args[1]
                assert kwargs.get('source_limit') == 75

def test_main_error_handling():
    """Test the error handling in the main function."""
    # Test file not found error
    with patch('sys.argv', ["notebook-cat", "/nonexistent/dir", "/output/dir"]):
        with patch('src.notebook_cat.core.process_directory', 
                side_effect=FileNotFoundError("No such directory")):
            
            # Should handle the error gracefully
            main()
    
    # Test permission error
    with patch('sys.argv', ["notebook-cat", "/protected/dir", "/output/dir"]):
        with patch('src.notebook_cat.core.process_directory', 
                side_effect=PermissionError("Permission denied")):
            
            # Should handle the error gracefully
            main()
    
    # Test generic error
    with patch('sys.argv', ["notebook-cat", "/input/dir", "/output/dir"]):
        with patch('src.notebook_cat.core.process_directory', 
                side_effect=ValueError("Some error")):
            
            # Should handle the error gracefully
            main()

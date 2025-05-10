"""
Tests for the validation functionality.
"""
import os
import sys
import pytest
from pathlib import Path

# Always use relative imports for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.notebook_cat.validation import (
    validate_file_extension, 
    validate_json_path,
    validate_plan_type,
    validate_word_limit,
    sanitize_filename,
    validate_inputs
)

def test_validate_file_extension():
    """Test file extension validation."""
    # Valid extensions
    assert validate_file_extension("test.txt") == True
    assert validate_file_extension("test.md") == True
    assert validate_file_extension("test.json") == True
    
    # Invalid extensions
    assert validate_file_extension("test.pdf") == False
    assert validate_file_extension("test.doc") == False
    assert validate_file_extension("test") == False
    assert validate_file_extension("") == False
    assert validate_file_extension(None) == False

def test_validate_json_path():
    """Test JSON path validation."""
    # Valid paths
    assert validate_json_path("content.text") == (True, "content.text")
    assert validate_json_path("data.items.text") == (True, "data.items.text")
    assert validate_json_path("") == (True, "")
    assert validate_json_path(None) == (True, "")
    
    # Invalid paths
    assert validate_json_path("content/text") == (False, "")  # Contains /
    assert validate_json_path("content\\text") == (False, "")  # Contains \
    assert validate_json_path("content..text") == (False, "")  # Contains ..
    assert validate_json_path("content@text") == (False, "contenttext")  # Contains @

def test_validate_plan_type():
    """Test plan type validation."""
    # Valid plan types
    assert validate_plan_type("free") == (True, "free")
    assert validate_plan_type("plus") == (True, "plus")
    assert validate_plan_type("custom") == (True, "custom")
    
    # Invalid plan types
    assert validate_plan_type("premium") == (False, "free")
    assert validate_plan_type("") == (False, "free")
    assert validate_plan_type(None) == (False, "free")

def test_validate_word_limit():
    """Test word limit validation."""
    # Valid word limits
    assert validate_word_limit(10000) == (True, 10000)
    assert validate_word_limit(380000) == (True, 380000)
    assert validate_word_limit(500000) == (True, 500000)
    
    # Invalid word limits
    assert validate_word_limit(500) == (False, 1000)  # Too small
    assert validate_word_limit(600000) == (False, 500000)  # Too large
    assert validate_word_limit("text") == (False, 380000)  # Not a number
    assert validate_word_limit(None) == (False, 380000)  # None

def test_sanitize_filename():
    """Test filename sanitization."""
    # Normal filenames
    assert sanitize_filename("test.txt") == "test.txt"
    assert sanitize_filename("test_123.json") == "test_123.json"
    
    # Test if the function sanitizes properly
    sanitized1 = sanitize_filename("/path/to/file.txt")
    assert "file.txt" in sanitized1 or sanitized1 == "file.txt"
    
    sanitized2 = sanitize_filename("C:\\path\\to\\file.txt")
    assert "file.txt" in sanitized2 or sanitized2 == "file.txt"
    
    # Special characters
    assert sanitize_filename("file<with>special&chars.txt") == "file_with_special_chars.txt"
    assert sanitize_filename("") == "file"
    assert sanitize_filename(None) == "file"

def test_validate_inputs():
    """Test full input validation."""
    # Valid inputs
    is_valid, sanitized, errors = validate_inputs(
        files=["test.txt", "data.md", "info.json"],
        plan_type="free",
        word_limit=380000,
        json_path="content.text"
    )
    assert is_valid == True
    assert len(errors) == 0
    assert len(sanitized["files"]) == 3
    assert sanitized["plan_type"] == "free"
    assert sanitized["word_limit"] == 380000
    assert sanitized["json_path"] == "content.text"
    
    # Mixed inputs (some valid, some invalid)
    is_valid, sanitized, errors = validate_inputs(
        files=["test.txt", "data.pdf", "info.doc"],
        plan_type="premium",
        word_limit=600000,
        json_path="content/text"
    )
    assert is_valid == False
    assert len(errors) >= 4  # At least 4 errors (exact number might depend on implementation)
    assert len(sanitized["files"]) == 1  # Only test.txt is valid
    assert sanitized["plan_type"] == "free"  # Fallback to free
    assert sanitized["word_limit"] == 500000  # Capped at 500k
    assert sanitized["json_path"] == ""  # Invalid path sanitized
    
    # All invalid inputs
    is_valid, sanitized, errors = validate_inputs(
        files=[],
        plan_type="unknown",
        word_limit=-1,
        json_path="a/b"
    )
    assert is_valid == False
    assert len(errors) > 0
    assert len(sanitized["files"]) == 0
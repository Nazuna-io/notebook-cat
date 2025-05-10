"""
Validation utilities for notebook-cat.

This module provides functions to validate user inputs and file content.
"""

from pathlib import Path
import re
import os
from typing import Tuple, List, Optional

# Import from the project if possible
try:
    from notebook_cat.config.defaults import SUPPORTED_EXTENSIONS, WORD_LIMIT
    from notebook_cat.utils import sanitize_filename
except ImportError:
    # Fall back to relative import for development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.notebook_cat.config.defaults import SUPPORTED_EXTENSIONS, WORD_LIMIT
    from src.notebook_cat.utils import sanitize_filename


def validate_file_extension(filename: str) -> bool:
    """
    Validate that the file has a supported extension.
    
    Args:
        filename: The filename to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not filename:
        return False
    
    allowed_extensions = set(SUPPORTED_EXTENSIONS.keys())
    extension = Path(filename).suffix.lower()[1:]  # Remove the leading dot
    
    return extension in allowed_extensions


def validate_json_path(json_path: Optional[str]) -> Tuple[bool, str]:
    """
    Validate that the JSON path is in a secure format.
    
    Args:
        json_path: The JSON path to validate
        
    Returns:
        tuple: (is_valid, sanitized_path)
    """
    if not json_path:
        return True, ""
    
    # Check for any dangerous characters or patterns
    if '..' in json_path or '/' in json_path or '\\' in json_path:
        return False, ""
    
    # Only allow alphanumeric and dot characters
    sanitized_path = ''.join(c for c in json_path if c.isalnum() or c == '.')
    
    # If the path was changed, it contained invalid characters
    if sanitized_path != json_path:
        return False, sanitized_path
    
    return True, sanitized_path


def validate_plan_type(plan_type: str) -> Tuple[bool, str]:
    """
    Validate the plan type selection.
    
    Args:
        plan_type: The plan type to validate
        
    Returns:
        tuple: (is_valid, sanitized_plan_type)
    """
    valid_plan_types = ["free", "plus", "custom"]
    
    if not plan_type or plan_type not in valid_plan_types:
        return False, "free"  # Default to free if invalid
    
    return True, plan_type


def validate_word_limit(word_limit: int) -> Tuple[bool, int]:
    """
    Validate the word limit value.
    
    Args:
        word_limit: The word limit to validate
        
    Returns:
        tuple: (is_valid, sanitized_word_limit)
    """
    try:
        limit = int(word_limit)
        
        # Enforce reasonable limits
        if limit < 1000:
            return False, 1000
        
        if limit > 500000:
            return False, 500000
            
        return True, limit
    except (ValueError, TypeError):
        return False, WORD_LIMIT  # Default to predefined word limit if invalid


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and injection.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: The sanitized filename
    """
    # Use the utility function
    from .utils import sanitize_filename as utils_sanitize_filename
    return utils_sanitize_filename(filename)


def validate_inputs(files: List[str], plan_type: str, word_limit: int, json_path: Optional[str]) -> Tuple[bool, dict, List[str]]:
    """
    Validate all input parameters.
    
    Args:
        files: List of file paths
        plan_type: NotebookLM plan type
        word_limit: Word limit per source
        json_path: JSON path for text extraction
        
    Returns:
        tuple: (is_valid, sanitized_inputs, error_messages)
    """
    errors = []
    sanitized = {}
    
    # Validate files
    valid_files = []
    if not files:
        errors.append("No files were uploaded.")
    else:
        for file in files:
            if validate_file_extension(file):
                valid_files.append(file)
            else:
                errors.append(f"File {sanitize_filename(os.path.basename(file))} has an unsupported extension.")
    
    sanitized["files"] = valid_files
    
    # Validate plan type
    is_valid_plan, sanitized_plan = validate_plan_type(plan_type)
    if not is_valid_plan:
        errors.append(f"Invalid plan type: {plan_type}. Using default: {sanitized_plan}")
    sanitized["plan_type"] = sanitized_plan
    
    # Validate word limit
    is_valid_limit, sanitized_limit = validate_word_limit(word_limit)
    if not is_valid_limit:
        errors.append(f"Invalid word limit: {word_limit}. Using: {sanitized_limit}")
    sanitized["word_limit"] = sanitized_limit
    
    # Validate JSON path
    is_valid_json_path, sanitized_json_path = validate_json_path(json_path)
    if not is_valid_json_path and json_path:
        errors.append(f"Invalid JSON path format: {json_path}. Using: {sanitized_json_path}")
    sanitized["json_path"] = sanitized_json_path
    
    return len(errors) == 0, sanitized, errors

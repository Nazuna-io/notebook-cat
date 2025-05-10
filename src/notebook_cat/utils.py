"""
Utility functions for the notebook-cat tool.
"""
import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Set, Tuple, Any

def sanitize_filename(filename: Optional[str]) -> str:
    """
    Sanitize a filename to prevent path traversal and injection.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: The sanitized filename
    """
    if not filename:
        return "file"  # Default fallback for empty or None input
    
    # Get only the basename to prevent path traversal
    basename = os.path.basename(filename)
    
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[^a-zA-Z0-9_\-.]', '_', basename)
    
    # Ensure the filename is not empty after sanitization
    if not sanitized:
        sanitized = "file"
    
    return sanitized

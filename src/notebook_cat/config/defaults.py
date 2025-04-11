# Default configuration values for NotebookLM
import sys
import os
from pathlib import Path

# Try to import from the root config file
try:
    # Add project root to sys.path if not already there
    project_root = Path(__file__).parents[3]  # Go up 3 levels to reach project root
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Import from the root config
    from config import WORD_LIMIT, DEFAULT_SOURCE_LIMIT, PLUS_SOURCE_LIMIT
except ImportError:
    # Fallback to default values if root config is not available
    print("Warning: Could not import from root config.py. Using default values.")
    WORD_LIMIT = 248000  # Maximum word count per source file (with 20k word cushion)
    DEFAULT_SOURCE_LIMIT = 50  # Default source count limit (Free plan)
    PLUS_SOURCE_LIMIT = 300  # Source count limit for Plus plan

# File extension patterns to match
SUPPORTED_EXTENSIONS = {
    'txt': '*.txt',  # Text files
    'json': '*.json',  # JSON files
    'md': '*.md',  # Markdown files
}

# Resume processing
RESUME_MARKER_FILE = '.notebook_cat_resume'  # File to track resume state

# Supported JSON fields to extract text from
# These are common field names that might contain text in JSON files
JSON_TEXT_FIELDS = [
    'text',
    'content',
    'transcript',
    'value',
    'description',
    'body'
]

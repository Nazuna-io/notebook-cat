# Default configuration values for NotebookLM

# NotebookLM limits
WORD_LIMIT = 480000  # Maximum word count per source file (with 20k word cushion)
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

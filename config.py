"""
Main configuration file for Notebook Cat.
Adjust these settings to customize the behavior of the application.
"""

# NotebookLM word limit settings
# Maximum number of words per source file
WORD_LIMIT = 380000  # Includes a 20k word cushion

# Source count limits for different plans
DEFAULT_SOURCE_LIMIT = 50  # Free plan
PLUS_SOURCE_LIMIT = 300    # Plus plan

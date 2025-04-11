"""
Test the configuration file setup.
This test verifies that the defaults.py file correctly imports settings from the root config.py.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Test importing from config.py directly
from config import WORD_LIMIT as ROOT_WORD_LIMIT
from config import DEFAULT_SOURCE_LIMIT as ROOT_DEFAULT_SOURCE_LIMIT
from config import PLUS_SOURCE_LIMIT as ROOT_PLUS_SOURCE_LIMIT

# Test importing through the defaults.py
from src.notebook_cat.config.defaults import WORD_LIMIT, DEFAULT_SOURCE_LIMIT, PLUS_SOURCE_LIMIT

# Verify that values match
assert ROOT_WORD_LIMIT == WORD_LIMIT, f"Word limit mismatch: {ROOT_WORD_LIMIT} != {WORD_LIMIT}"
assert ROOT_DEFAULT_SOURCE_LIMIT == DEFAULT_SOURCE_LIMIT, f"Default source limit mismatch"
assert ROOT_PLUS_SOURCE_LIMIT == PLUS_SOURCE_LIMIT, f"Plus source limit mismatch"

# Verify that the correct values are being used
assert WORD_LIMIT == 380000, f"Incorrect word limit: {WORD_LIMIT}"
assert DEFAULT_SOURCE_LIMIT == 50, f"Incorrect default source limit: {DEFAULT_SOURCE_LIMIT}"
assert PLUS_SOURCE_LIMIT == 300, f"Incorrect plus source limit: {PLUS_SOURCE_LIMIT}"

print("Configuration test passed! The defaults.py file correctly imports from root config.py.")

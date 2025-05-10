#!/usr/bin/env python3
"""
Simple test to check if basic concatenation functionality works.
"""

import os
import sys
from pathlib import Path

# Add the project to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the core modules
from src.notebook_cat import core

def main():
    """Run a simple test of the core functionality."""
    
    print("Starting simple test...")
    
    # Define the input and output paths
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process the files
    print(f"Processing files from: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    core.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        source_limit=50,  # Default source limit
        json_path=None,
        max_files=None
    )
    
    # Check the results
    output_files = [f for f in os.listdir(output_dir) if f.startswith("notebooklm_source_")]
    
    print(f"Files created: {len(output_files)}")
    for f in output_files:
        print(f"  - {f}")
    
    print("Test completed successfully.")

if __name__ == "__main__":
    main()

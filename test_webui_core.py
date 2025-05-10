#!/usr/bin/env python3
"""
Standalone test script to verify the core functionality used by the web UI.
This script simulates the web UI processing but runs directly from the command line.
"""

import os
import sys
import tempfile
from pathlib import Path
import zipfile
import shutil
import time

# Add the project to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the core modules
from src.notebook_cat import core
from src.notebook_cat.config.defaults import WORD_LIMIT, DEFAULT_SOURCE_LIMIT, SUPPORTED_EXTENSIONS


def test_process_files_directly():
    """Test the core file processing functionality directly with the input files."""
    
    print("\n===== TESTING DIRECT FILE PROCESSING =====")
    
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
        source_limit=DEFAULT_SOURCE_LIMIT,
        json_path=None,
        max_files=None
    )
    
    # Check the results
    output_files = [f for f in os.listdir(output_dir) if f.startswith("notebooklm_source_")]
    
    print(f"Files created: {len(output_files)}")
    for f in output_files:
        print(f"  - {f}")
    
    # Create a ZIP of the output
    zip_path = os.path.join(output_dir, "notebook_cat_output.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                zipf.write(item_path, arcname=item)
    
    print(f"ZIP file created at: {zip_path}")
    
    return output_files


def test_process_files_with_temp_dirs():
    """Test the file processing with temporary directories (similar to web UI)."""
    
    print("\n===== TESTING WITH TEMPORARY DIRECTORIES =====")
    
    # Define the input path
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    
    # Create temporary directories
    temp_input_dir = tempfile.mkdtemp()
    temp_output_dir = tempfile.mkdtemp()
    
    print(f"Temporary input directory: {temp_input_dir}")
    print(f"Temporary output directory: {temp_output_dir}")
    
    try:
        # Copy the input files to the temp directory
        input_files = os.listdir(input_dir)
        for filename in input_files:
            src_file = os.path.join(input_dir, filename)
            dst_file = os.path.join(temp_input_dir, filename)
            shutil.copy2(src_file, dst_file)
        
        print(f"Copied {len(input_files)} files to temporary directory")
        
        # Process the files
        core.process_directory(
            input_dir=temp_input_dir,
            output_dir=temp_output_dir,
            source_limit=DEFAULT_SOURCE_LIMIT,
            json_path=None,
            max_files=None
        )
        
        # Check the results
        output_files = [f for f in os.listdir(temp_output_dir) if f.startswith("notebooklm_source_")]
        
        print(f"Files created: {len(output_files)}")
        for f in output_files:
            print(f"  - {f}")
        
        # Create a ZIP of the output
        zip_path = os.path.join(temp_output_dir, "notebook_cat_output.zip")
        print(f"Creating ZIP file at: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for item in os.listdir(temp_output_dir):
                item_path = os.path.join(temp_output_dir, item)
                if os.path.isfile(item_path):
                    print(f"  Adding to ZIP: {item}")
                    zipf.write(item_path, arcname=item)
        
        # Verify the ZIP was created
        if os.path.exists(zip_path):
            print(f"ZIP file successfully created: {os.path.getsize(zip_path)} bytes")
            
            # List the contents of the ZIP
            print("ZIP contents:")
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for item in zipf.namelist():
                    print(f"  - {item}")
        else:
            print("ERROR: ZIP file was not created!")
            
        return output_files
        
    except Exception as e:
        import traceback
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        return []
    finally:
        # Don't clean up the temp directories so we can inspect them
        print(f"Temporary directories are preserved for inspection:")
        print(f"  Input: {temp_input_dir}")
        print(f"  Output: {temp_output_dir}")


def simulation_function_similar_to_webui():
    """
    This function simulates what happens in the webui.py process_files function,
    but with more debugging output and explicit testing.
    """
    print("\n===== SIMULATING WEB UI FUNCTION =====")
    
    # Get the input files
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]
    
    print(f"Input files: {len(input_files)}")
    for f in input_files:
        print(f"  - {f}")
    
    # Create temporary directories
    temp_input_dir = tempfile.mkdtemp()
    temp_output_dir = tempfile.mkdtemp()
    
    print(f"Temporary input directory: {temp_input_dir}")
    print(f"Temporary output directory: {temp_output_dir}")
    
    try:
        temp_input_path = Path(temp_input_dir)
        temp_output_path = Path(temp_output_dir)
        
        # Copy uploaded files to the temporary input directory
        for file in input_files:
            file_path = Path(file)
            if file_path.suffix.lower()[1:] in SUPPORTED_EXTENSIONS:
                dst_path = temp_input_path / file_path.name
                print(f"Copying {file_path} to {dst_path}")
                shutil.copy2(file_path, dst_path)
        
        # Verify files were copied
        copied_files = list(temp_input_path.glob('*'))
        print(f"Files copied to temp dir: {len(copied_files)}")
        for f in copied_files:
            print(f"  - {f}")
        
        # Process the files
        core.process_directory(
            input_dir=str(temp_input_path),
            output_dir=str(temp_output_path),
            source_limit=DEFAULT_SOURCE_LIMIT,
            json_path=None,
            max_files=None
        )
        
        # Check if any output files were created
        output_files_list = []
        for item in os.listdir(temp_output_path):
            output_item_path = temp_output_path / item
            if item.startswith("notebooklm_source_") and item.endswith(".txt") and output_item_path.is_file():
                output_files_list.append(output_item_path)
                print(f"Found output file: {output_item_path}")
        
        if not output_files_list:
            print("Error: No output files were created.")
            return []
        
        # Create a zip file of all outputs
        zip_path = Path(temp_output_dir) / "notebook_cat_output.zip"
        print(f"Creating ZIP file at: {zip_path}")
        
        try:
            with zipfile.ZipFile(str(zip_path), 'w') as zipf:
                # First add the summary file if it exists
                summary_path = temp_output_path / "notebook_cat_summary.txt"
                if summary_path.exists():
                    print(f"Adding summary file to ZIP: {summary_path}")
                    zipf.write(summary_path, arcname=summary_path.name)
                
                # Then add all output files
                for i, file_path in enumerate(output_files_list):
                    if file_path.is_file():
                        print(f"Adding output file to ZIP: {file_path}")
                        zipf.write(file_path, arcname=file_path.name)
        except Exception as e:
            print(f"Error creating ZIP file: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        # Check if zip file was created and exists
        if not zip_path.exists():
            print(f"ZIP file not found at {str(zip_path)}")
            # Create a simple text file as a fallback
            fallback_file = temp_output_path / "output_files.txt"
            with open(fallback_file, 'w') as f:
                f.write("Error: Failed to create ZIP archive. Here are the files that were processed:\n\n")
                for output_file in output_files_list:
                    f.write(f"- {output_file.name}\n")
            return [str(fallback_file)]
        
        print(f"ZIP file created at: {str(zip_path)}")
        print(f"ZIP file size: {os.path.getsize(str(zip_path))} bytes")
        
        # List ZIP contents
        print("ZIP contents:")
        with zipfile.ZipFile(str(zip_path), 'r') as zipf:
            for item in zipf.namelist():
                print(f"  - {item}")
                
        return [str(zip_path)]
            
    except Exception as e:
        import traceback
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        return []


if __name__ == "__main__":
    print("Starting tests...")
    
    # Test 1: Direct file processing
    test_process_files_directly()
    
    # Test 2: Processing with temporary directories
    test_process_files_with_temp_dirs()
    
    # Test 3: Simulation of web UI function
    simulation_function_similar_to_webui()
    
    print("\nAll tests completed. Check the output above for any errors.")

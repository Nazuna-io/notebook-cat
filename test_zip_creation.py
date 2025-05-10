#!/usr/bin/env python3
"""
Test script specifically focused on the ZIP file creation issue.
This creates a very simple test to verify ZIP file creation works.
"""

import os
import sys
import zipfile
import tempfile
import time

def test_zip_creation():
    """Test creating a ZIP file in a temporary directory."""
    
    print("\n===== TESTING ZIP CREATION =====")
    
    # Create a temporary directory with timestamp to ensure uniqueness
    temp_dir = "/tmp/notebook-cat-zip-test-" + str(int(time.time()))
    os.makedirs(temp_dir, exist_ok=True)
    os.chmod(temp_dir, 0o777)  # Ensure full permissions
    
    print(f"Created temporary directory: {temp_dir}")
    
    # Create a few test files in the temp directory
    test_files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"test_file_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"This is test file {i} content.\nLine 2 of test file {i}.")
        test_files.append(file_path)
        print(f"Created test file: {file_path}")
    
    # Create a ZIP file
    zip_path = os.path.join(temp_dir, "test_output.zip")
    print(f"Creating ZIP file at: {zip_path}")
    
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in test_files:
                file_name = os.path.basename(file_path)
                zipf.write(file_path, arcname=file_name)
                print(f"Added file to ZIP: {file_path}")
        
        # Verify the ZIP file was created
        if os.path.exists(zip_path):
            print(f"SUCCESS: ZIP file created: {zip_path}")
            
            # List the contents of the ZIP
            print("ZIP contents:")
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for item in zipf.namelist():
                    print(f"  - {item}")
            
            print(f"ZIP file size: {os.path.getsize(zip_path)} bytes")
            return True
        else:
            print(f"ERROR: ZIP file not created: {zip_path}")
            return False
            
    except Exception as e:
        import traceback
        print(f"ERROR creating ZIP: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_zip_creation()
    if success:
        print("\nZIP creation test PASSED")
        sys.exit(0)
    else:
        print("\nZIP creation test FAILED")
        sys.exit(1)

import pytest
from pathlib import Path
import tempfile
import os
import shutil

# Import from the installed package if possible, otherwise from source
try:
    from notebook_cat.webui import process_files
except ImportError:
    # Fall back to relative import for development
    from src.notebook_cat.webui import process_files

@pytest.fixture
def temp_files():
    """Create temporary test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a few test files
        file1 = tmpdir_path / "test1.txt"
        file2 = tmpdir_path / "test2.txt"
        file3 = tmpdir_path / "test3.json"
        
        with open(file1, "w", encoding="utf-8") as f:
            f.write("This is test file 1.")
        
        with open(file2, "w", encoding="utf-8") as f:
            f.write("This is test file 2 with more content.")
        
        with open(file3, "w", encoding="utf-8") as f:
            f.write('{"text": "This is a JSON test file."}')
        
        yield [str(file1), str(file2), str(file3)]

def test_process_files_basic(temp_files, monkeypatch):
    """Test basic file processing through the web UI function."""
    # Create a mock progress tracker for Gradio
    class MockProgress:
        def __init__(self):
            self.value = 0
            self.desc = ""
        
        def __call__(self, value=None, desc=None):
            if value is not None:
                self.value = value
            if desc is not None:
                self.desc = desc
            return self.value
    
    # Run the process_files function
    output_files, status, summary = process_files(
        files=temp_files,
        plan_type="free",
        progress=MockProgress()
    )
    
    # Check that we get output files
    assert len(output_files) > 0
    assert "Processing complete" in status
    assert "NOTEBOOK CAT - PROCESSING SUMMARY" in summary

def test_process_files_no_input():
    """Test behavior when no files are provided."""
    output_files, status, summary = process_files(
        files=[],
        plan_type="free",
        progress=lambda *args, **kwargs: None
    )
    
    assert len(output_files) == 0
    assert "No files were uploaded" in status
    assert summary == ""

# This test will be skipped in CI environments where a browser might not be available
@pytest.mark.skip(reason="UI test requires browser")
def test_create_ui():
    """Test that the UI can be created without errors."""
    from notebook_cat.webui import create_ui
    
    # Just test that the UI creation doesn't raise exceptions
    ui = create_ui()
    assert ui is not None

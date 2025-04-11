"""
Additional tests for the core functionality to improve test coverage.
"""
import pytest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.notebook_cat import core
from src.notebook_cat.config.defaults import JSON_TEXT_FIELDS, WORD_LIMIT

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

def test_extract_default_text_from_json_array_of_strings():
    """Test extracting text from a simple array of strings."""
    data = ["First item", "Second item", "Third item"]
    result = core.extract_default_text_from_json(data)
    assert "First item" in result
    assert "Second item" in result
    assert "Third item" in result
    assert result.count("\n\n") == 2  # Two newline pairs between three items

def test_extract_default_text_from_json_object_with_text_field():
    """Test extracting text from an object with a text field."""
    for field in JSON_TEXT_FIELDS:
        data = {field: f"This is text from the {field} field"}
        result = core.extract_default_text_from_json(data)
        assert f"This is text from the {field} field" == result

def test_extract_default_text_from_json_complex_object():
    """Test extracting text from a complex object without recognized text fields."""
    data = {
        "metadata": {"id": 123, "type": "document"},
        "stats": {"wordCount": 200, "characters": 1500}
    }
    result = core.extract_default_text_from_json(data)
    # Should convert to JSON string
    assert "metadata" in result
    assert "stats" in result

def test_extract_default_text_from_json_nested_objects():
    """Test extracting text from nested objects with text fields."""
    data = {
        "records": [
            {"text": "First record text"},
            {"text": "Second record text"}
        ]
    }
    result = core.extract_default_text_from_json(data)
    assert "First record text" in result
    assert "Second record text" in result

def test_extract_text_from_json_file_size_limit(temp_dir):
    """Test file size limit check in extract_text_from_json."""
    # Create a large JSON file that exceeds the limit
    json_path = temp_dir / "large.json"
    
    # Create a string that's larger than 50MB
    large_string = "x" * (60 * 1024 * 1024)  # 60MB string
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('{"text": "' + large_string[:1000] + '"}')  # Write first 1000 chars to make it valid JSON
    
    # Monkey patch the file size check - we don't want to actually create a huge file
    orig_stat = Path.stat
    try:
        def mock_stat(self):
            result = orig_stat(self)
            if self.name == "large.json":
                class MockStat:
                    st_size = 60 * 1024 * 1024  # Pretend it's 60MB
                return MockStat()
            return result
        
        Path.stat = mock_stat
        
        # Should return empty string due to size limit
        result = core.extract_text_from_json(json_path)
        assert result == ""
    finally:
        # Restore the original stat method
        Path.stat = orig_stat

def test_extract_text_from_json_invalid_json(temp_dir):
    """Test handling of invalid JSON files."""
    json_path = temp_dir / "invalid.json"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('{Not a valid JSON file')
    
    # Should handle the error gracefully
    result = core.extract_text_from_json(json_path)
    assert result == ""

def test_extract_text_from_json_with_invalid_path(temp_dir):
    """Test extract_text_from_json with an invalid JSON path."""
    data = {
        "user": {
            "name": "Test User",
            "metadata": {"age": 30}
        }
    }
    json_file = temp_dir / "test.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    # Test with an invalid path
    result = core.extract_text_from_json(json_file, json_path="user.invalid.field")
    assert result == ""

def test_sanitize_filename():
    """Test the filename sanitization function."""
    # Test with potentially dangerous characters
    dangerous = "file;with&dangerous<characters>.txt"
    safe = core.sanitize_filename(dangerous)
    assert ";" not in safe
    assert "&" not in safe
    assert "<" not in safe
    assert ">" not in safe
    
    # Test with safe characters
    safe_name = "safe_file-name.txt"
    result = core.sanitize_filename(safe_name)
    assert result == safe_name
    
    # Test with path traversal attempt
    traversal = "../../../etc/passwd"
    result = core.sanitize_filename(traversal)
    assert "/" not in result
    assert "\\" not in result

def test_process_directory_empty_dir(temp_dir):
    """Test processing an empty directory."""
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"
    input_dir.mkdir()
    
    # Should handle empty directory gracefully
    core.process_directory(str(input_dir), str(output_dir))
    
    # The function should return without error and without creating output files
    assert not any(output_dir.glob('*.txt'))

def test_save_load_resume_state_empty(temp_dir):
    """Test saving and loading an empty resume state."""
    core.save_resume_state(temp_dir, 0, set())
    
    # Verify file was created
    resume_file = temp_dir / core.RESUME_MARKER_FILE
    assert resume_file.exists()
    
    # Load the state
    groups, files = core.load_resume_state(temp_dir)
    assert groups == 0
    assert files == set()

def test_load_resume_state_nonexistent_file(temp_dir):
    """Test loading a resume state when the file doesn't exist."""
    # File doesn't exist
    groups, files = core.load_resume_state(temp_dir)
    assert groups == 0
    assert files == set()

def test_generate_summary_report_empty(temp_dir):
    """Test generating a summary report with empty data."""
    core.generate_summary_report(temp_dir, [], [], 0, 0)
    
    # Verify file was created
    summary_file = temp_dir / "notebook_cat_summary.txt"
    assert summary_file.exists()
    
    # Verify content
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Total files processed: 0" in content
    assert "Total words processed: 0" in content
    assert "Files successfully grouped: 0" in content
    assert "Files not grouped: 0" in content
    assert "Output sources created: 0" in content

def test_process_directory_with_resume(temp_dir):
    """Test process_directory with resume option."""
    # Set up directories
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create test files
    (input_dir / "file1.txt").write_text("This is file 1 content.")
    (input_dir / "file2.txt").write_text("This is file 2 content.")
    
    # Create a fake resume state
    fake_state = {
        'groups_processed': 1,
        'files_processed': [str(input_dir / "file1.txt")]
    }
    
    resume_file = output_dir / core.RESUME_MARKER_FILE
    with open(resume_file, 'w', encoding='utf-8') as f:
        json.dump(fake_state, f)
    
    # Run the process_directory function with resume option
    core.process_directory(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        resume=True
    )
    
    # Check that only file2.txt was processed
    # (since file1.txt was already marked as processed in the resume state)
    files_created = list(output_dir.glob("*.txt"))
    # There should be exactly one output file excluding the resume marker
    output_files = [f for f in files_created if f.name != core.RESUME_MARKER_FILE]
    assert len(output_files) == 1

def test_process_directory_dry_run(temp_dir):
    """Test process_directory with dry_run option."""
    # Set up directories
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create test files
    (input_dir / "file1.txt").write_text("This is file 1 with some content.")
    (input_dir / "file2.txt").write_text("This is file 2 with other content.")
    
    # Run the process_directory function with dry_run option
    core.process_directory(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        dry_run=True
    )
    
    # No output files should be created in dry run mode except the summary
    txt_files = list(output_dir.glob("notebooklm_source_*.txt"))
    assert len(txt_files) == 0
    
    # Summary file should still be created
    summary_file = output_dir / "notebook_cat_summary.txt"
    assert summary_file.exists()

def test_process_directory_with_max_files(temp_dir):
    """Test process_directory with max_files option."""
    # Set up directories
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create multiple test files
    for i in range(5):
        (input_dir / f"file{i}.txt").write_text(f"This is file {i} content.")
    
    # Run with max_files=2
    core.process_directory(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        max_files=2
    )
    
    # Check output - should be based on only processing 2 files
    output_files = list(output_dir.glob("notebooklm_source_*.txt"))
    assert len(output_files) > 0
    
    # Check content of summary file
    summary_file = output_dir / "notebook_cat_summary.txt"
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # Only 2 files should be processed due to max_files limit
    assert "Total files processed: 2" in content

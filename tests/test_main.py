"""
Tests for the main CLI functionality.
"""
import os
import sys
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Always use relative imports for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.notebook_cat import main
from src.notebook_cat.config.defaults import (
    DEFAULT_SOURCE_LIMIT,
    PLUS_SOURCE_LIMIT
)

@pytest.fixture
def temp_dirs():
    """Create temporary input and output directories."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create some test files in the input directory
        (Path(input_dir) / "file1.txt").write_text("This is file 1 content.")
        (Path(input_dir) / "file2.txt").write_text("This is file 2 content.")
        (Path(input_dir) / "file3.md").write_text("# Markdown file\nWith some content.")
        
        yield Path(input_dir), Path(output_dir)

@patch('sys.argv')
def test_main_basic_usage(mock_argv, temp_dirs, monkeypatch):
    """Test basic usage of the main function."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir)
    ][idx]
    
    # Create a mock for process_directory
    mock_process = MagicMock()
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process)
    
    # Run the main function
    main.main()
    
    # Check that process_directory was called with correct arguments
    mock_process.assert_called_once()
    call_args = mock_process.call_args[1]
    assert call_args['input_dir'] == str(Path(input_dir).absolute())
    assert call_args['output_dir'] == str(Path(output_dir).absolute())
    assert call_args['source_limit'] == DEFAULT_SOURCE_LIMIT
    assert call_args['dry_run'] is False
    assert call_args['resume'] is False
    assert 'txt' in call_args['file_extensions']
    assert 'md' in call_args['file_extensions']
    assert 'json' in call_args['file_extensions']
    assert call_args['max_files'] is None

@patch('sys.argv')
def test_main_plus_plan(mock_argv, temp_dirs, monkeypatch):
    """Test using the plus plan option."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--plus-plan"
    ][idx]
    
    # Create a mock for process_directory
    mock_process = MagicMock()
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process)
    
    # Run the main function
    main.main()
    
    # Check that process_directory was called with plus plan limit
    call_args = mock_process.call_args[1]
    assert call_args['source_limit'] == PLUS_SOURCE_LIMIT

@patch('sys.argv')
def test_main_custom_limit(mock_argv, temp_dirs, monkeypatch):
    """Test using a custom source limit."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--limit", "75"
    ][idx]
    
    # Create a mock for process_directory
    mock_process = MagicMock()
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process)
    
    # Run the main function
    main.main()
    
    # Check that process_directory was called with custom limit
    call_args = mock_process.call_args[1]
    assert call_args['source_limit'] == 75

@patch('sys.argv')
def test_main_specific_extensions(mock_argv, temp_dirs, monkeypatch):
    """Test using specific file extensions."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--extensions", "txt,md"
    ][idx]
    
    # Create a mock for process_directory
    mock_process = MagicMock()
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process)
    
    # Run the main function
    main.main()
    
    # Check that process_directory was called with correct extensions
    call_args = mock_process.call_args[1]
    assert 'txt' in call_args['file_extensions']
    assert 'md' in call_args['file_extensions']
    assert 'json' not in call_args['file_extensions']

@patch('sys.argv')
def test_main_dry_run(mock_argv, temp_dirs, monkeypatch):
    """Test using the dry run option."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--dry-run"
    ][idx]
    
    # Create a mock for process_directory
    mock_process = MagicMock()
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process)
    
    # Run the main function
    main.main()
    
    # Check that process_directory was called with dry_run=True
    call_args = mock_process.call_args[1]
    assert call_args['dry_run'] is True

@patch('sys.argv')
def test_main_json_path(mock_argv, temp_dirs, monkeypatch):
    """Test using a JSON path."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--json-path", "content.text"
    ][idx]
    
    # Create a mock for process_directory
    mock_process = MagicMock()
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process)
    
    # Run the main function
    main.main()
    
    # Check that process_directory was called with the correct JSON path
    call_args = mock_process.call_args[1]
    assert call_args['json_path'] == "content.text"

@patch('sys.argv')
def test_main_file_not_found_error(mock_argv, temp_dirs, capsys, monkeypatch):
    """Test handling of FileNotFoundError."""
    input_dir, output_dir = temp_dirs
    non_existent_dir = str(Path(input_dir) / "non_existent")
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        non_existent_dir,
        str(output_dir)
    ][idx]
    
    # Create a mock that raises FileNotFoundError
    def mock_process_directory(*args, **kwargs):
        raise FileNotFoundError(f"No such file or directory: '{non_existent_dir}'")
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process_directory)
    
    # Run the main function and expect a sys.exit
    with pytest.raises(SystemExit) as e:
        main.main()
    
    # Check the exit code
    assert e.value.code == 1
    
    # Check that the appropriate error message was printed
    captured = capsys.readouterr()
    assert "Error: File or directory not found" in captured.out

@patch('sys.argv')
def test_main_permission_error(mock_argv, temp_dirs, capsys, monkeypatch):
    """Test handling of PermissionError."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir)
    ][idx]
    
    # Create a mock that raises PermissionError
    def mock_process_directory(*args, **kwargs):
        raise PermissionError("Permission denied")
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process_directory)
    
    # Run the main function and expect a sys.exit
    with pytest.raises(SystemExit) as e:
        main.main()
    
    # Check the exit code
    assert e.value.code == 1
    
    # Check that the appropriate error message was printed
    captured = capsys.readouterr()
    assert "Error: Permission denied" in captured.out

@patch('sys.argv')
def test_main_generic_error(mock_argv, temp_dirs, capsys, monkeypatch):
    """Test handling of generic exceptions."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir)
    ][idx]
    
    # Create a mock that raises a generic exception
    def mock_process_directory(*args, **kwargs):
        raise ValueError("Some error")
    
    # Apply the mock to the main module
    monkeypatch.setattr("src.notebook_cat.main.core.process_directory", mock_process_directory)
    
    # Run the main function and expect a sys.exit
    with pytest.raises(SystemExit) as e:
        main.main()
    
    # Check the exit code
    assert e.value.code == 1
    
    # Check that the appropriate error message was printed
    captured = capsys.readouterr()
    assert "An error occurred during processing: ValueError" in captured.out

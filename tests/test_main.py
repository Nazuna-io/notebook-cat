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
def test_main_basic_usage(mock_argv, temp_dirs):
    """Test basic usage of the main function."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir)
    ][idx]
    
    # Run the main function
    with patch('src.notebook_cat.core.process_directory') as mock_process:
        main.main()
        
        # Check that process_directory was called with correct arguments
        mock_process.assert_called_once()
        call_args = mock_process.call_args[1]
        assert call_args['input_dir'] == str(input_dir)
        assert call_args['output_dir'] == str(output_dir)
        assert call_args['source_limit'] == DEFAULT_SOURCE_LIMIT
        assert call_args['dry_run'] is False
        assert call_args['resume'] is False
        assert 'txt' in call_args['file_extensions']
        assert 'md' in call_args['file_extensions']
        assert 'json' in call_args['file_extensions']
        assert call_args['max_files'] is None

@patch('sys.argv')
def test_main_plus_plan(mock_argv, temp_dirs):
    """Test using the plus plan option."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--plus-plan"
    ][idx]
    
    # Run the main function
    with patch('src.notebook_cat.core.process_directory') as mock_process:
        main.main()
        
        # Check that process_directory was called with plus plan limit
        call_args = mock_process.call_args[1]
        assert call_args['source_limit'] == PLUS_SOURCE_LIMIT

@patch('sys.argv')
def test_main_custom_limit(mock_argv, temp_dirs):
    """Test using a custom source limit."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--limit", "75"
    ][idx]
    
    # Run the main function
    with patch('src.notebook_cat.core.process_directory') as mock_process:
        main.main()
        
        # Check that process_directory was called with custom limit
        call_args = mock_process.call_args[1]
        assert call_args['source_limit'] == 75

@patch('sys.argv')
def test_main_specific_extensions(mock_argv, temp_dirs):
    """Test using specific file extensions."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--extensions", "txt,md"
    ][idx]
    
    # Run the main function
    with patch('src.notebook_cat.core.process_directory') as mock_process:
        main.main()
        
        # Check that process_directory was called with correct extensions
        call_args = mock_process.call_args[1]
        assert 'txt' in call_args['file_extensions']
        assert 'md' in call_args['file_extensions']
        assert 'json' not in call_args['file_extensions']

@patch('sys.argv')
def test_main_dry_run(mock_argv, temp_dirs):
    """Test using the dry run option."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--dry-run"
    ][idx]
    
    # Run the main function
    with patch('src.notebook_cat.core.process_directory') as mock_process:
        main.main()
        
        # Check that process_directory was called with dry_run=True
        call_args = mock_process.call_args[1]
        assert call_args['dry_run'] is True

@patch('sys.argv')
def test_main_json_path(mock_argv, temp_dirs):
    """Test using a JSON path."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir),
        "--json-path", "content.text"
    ][idx]
    
    # Run the main function
    with patch('src.notebook_cat.core.process_directory') as mock_process:
        main.main()
        
        # Check that process_directory was called with the correct JSON path
        call_args = mock_process.call_args[1]
        assert call_args['json_path'] == "content.text"

@patch('sys.argv')
def test_main_file_not_found_error(mock_argv, temp_dirs, capsys):
    """Test handling of FileNotFoundError."""
    input_dir, output_dir = temp_dirs
    non_existent_dir = str(Path(input_dir) / "non_existent")
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        non_existent_dir,
        str(output_dir)
    ][idx]
    
    # Mock process_directory to raise FileNotFoundError
    with patch('src.notebook_cat.core.process_directory', 
               side_effect=FileNotFoundError(f"No such file or directory: '{non_existent_dir}'")):
        # Run the main function and expect a sys.exit
        with pytest.raises(SystemExit) as e:
            main.main()
        
        # Check the exit code
        assert e.value.code == 1
        
        # Check that the appropriate error message was printed
        captured = capsys.readouterr()
        assert "Error: File or directory not found" in captured.out

@patch('sys.argv')
def test_main_permission_error(mock_argv, temp_dirs, capsys):
    """Test handling of PermissionError."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir)
    ][idx]
    
    # Mock process_directory to raise PermissionError
    with patch('src.notebook_cat.core.process_directory', 
               side_effect=PermissionError("Permission denied")):
        # Run the main function and expect a sys.exit
        with pytest.raises(SystemExit) as e:
            main.main()
        
        # Check the exit code
        assert e.value.code == 1
        
        # Check that the appropriate error message was printed
        captured = capsys.readouterr()
        assert "Error: Permission denied" in captured.out

@patch('sys.argv')
def test_main_generic_error(mock_argv, temp_dirs, capsys):
    """Test handling of generic exceptions."""
    input_dir, output_dir = temp_dirs
    
    # Set up mock command line arguments
    mock_argv.__getitem__.side_effect = lambda idx: [
        "notebook-cat",
        str(input_dir),
        str(output_dir)
    ][idx]
    
    # Mock process_directory to raise a generic exception
    with patch('src.notebook_cat.core.process_directory', 
               side_effect=ValueError("Some error")):
        # Run the main function and expect a sys.exit
        with pytest.raises(SystemExit) as e:
            main.main()
        
        # Check the exit code
        assert e.value.code == 1
        
        # Check that the appropriate error message was printed
        captured = capsys.readouterr()
        assert "An error occurred during processing: ValueError" in captured.out

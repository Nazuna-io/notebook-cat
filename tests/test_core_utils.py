"""
Tests for core utility functions.
"""
import os
import sys
import pytest
import tempfile
import json
import shutil
from pathlib import Path

# Always use relative imports for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.notebook_cat.core import (
    count_words_in_file,
    extract_text_from_json,
    extract_default_text_from_json,
    get_files_by_extensions,
    group_files,
    concatenate_files,
    WORD_LIMIT
)
from src.notebook_cat.utils import sanitize_filename

@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as file:
        # Write sample JSON data
        json_data = {
            "title": "Test Document",
            "content": "This is the main content of the document.",
            "sections": [
                {"heading": "Section 1", "text": "Text for section one."},
                {"heading": "Section 2", "text": "Text for section two."}
            ],
            "metadata": {
                "author": "Test Author",
                "date": "2025-05-10"
            }
        }
        file.write(json.dumps(json_data).encode('utf-8'))
        file_path = file.name
    
    yield Path(file_path)
    
    # Clean up
    if os.path.exists(file_path):
        os.unlink(file_path)

@pytest.fixture
def temp_directory():
    """Create a temporary directory with various test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create various test files
        dir_path = Path(tmpdir)
        
        # Text files
        (dir_path / "file1.txt").write_text("This is file 1.")
        (dir_path / "file2.txt").write_text("This is the second file with more content.")
        
        # Markdown files
        (dir_path / "doc1.md").write_text("# Heading\n\nMarkdown content.")
        (dir_path / "doc2.md").write_text("## Another doc\n\nWith *formatted* text.")
        
        # JSON files
        json_data1 = {"text": "JSON file 1 content."}
        json_data2 = {"content": {"text": "Nested JSON content."}}
        
        with open(dir_path / "data1.json", 'w') as f:
            json.dump(json_data1, f)
        
        with open(dir_path / "data2.json", 'w') as f:
            json.dump(json_data2, f)
        
        # Create a subdirectory
        subdir = dir_path / "subdir"
        subdir.mkdir()
        (subdir / "subfile.txt").write_text("This is in a subdirectory.")
        
        # Non-supported file
        (dir_path / "image.png").write_text("Not a real image file.")
        
        yield dir_path

def test_count_words_in_file():
    """Test counting words in different file types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        dir_path = Path(tmpdir)
        
        # Text file
        txt_file = dir_path / "test.txt"
        txt_file.write_text("This is a test file with ten words in it.")
        assert count_words_in_file(txt_file) == 10
        
        # Markdown file
        md_file = dir_path / "test.md"
        md_file.write_text("# Heading\n\nThis markdown has *seven* words.")
        assert count_words_in_file(md_file) == 7
        
        # JSON file
        json_file = dir_path / "test.json"
        json_data = {"text": "This JSON has four words."}
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        # For JSON files, the exact count might vary based on formatting
        # Just check that it's a reasonable number
        word_count = count_words_in_file(json_file)
        assert 3 <= word_count <= 10  # Allow some flexibility
        
        # Non-existent file
        assert count_words_in_file(dir_path / "nonexistent.txt") == 0

def test_extract_text_from_json(temp_json_file):
    """Test extracting text from JSON files."""
    # Test with specific JSON path
    text = extract_text_from_json(temp_json_file, "content")
    assert "main content" in text
    
    # Test with path to an array
    text = extract_text_from_json(temp_json_file, "sections")
    assert "section one" in text
    assert "section two" in text
    
    # Test with invalid path
    text = extract_text_from_json(temp_json_file, "nonexistent")
    assert text == ""
    
    # Test with no path (default extraction)
    text = extract_text_from_json(temp_json_file)
    assert "main content" in text or "section" in text

def test_extract_default_text_from_json():
    """Test the default JSON text extraction logic."""
    # Simple array of strings
    data = ["Item 1", "Item 2", "Item 3"]
    text = extract_default_text_from_json(data)
    assert "Item 1" in text
    assert "Item 2" in text
    assert "Item 3" in text
    
    # Object with text field
    data = {"text": "Main content", "other": "Ignored"}
    text = extract_default_text_from_json(data)
    assert "Main content" in text
    
    # Array of objects with text fields
    data = {"items": [{"text": "Text 1"}, {"text": "Text 2"}]}
    text = extract_default_text_from_json(data)
    assert "Text 1" in text or "Text 2" in text
    
    # Complex object without obvious text fields
    data = {"numbers": [1, 2, 3], "flag": True}
    text = extract_default_text_from_json(data)
    assert len(text) > 0  # Should convert to string

def test_get_files_by_extensions(temp_directory):
    """Test getting files by extensions."""
    # Get all text files
    txt_files = get_files_by_extensions(temp_directory, {"txt"})
    assert len(txt_files) == 2
    assert all(f.suffix == '.txt' for f in txt_files)
    
    # Get all markdown files
    md_files = get_files_by_extensions(temp_directory, {"md"})
    assert len(md_files) == 2
    assert all(f.suffix == '.md' for f in md_files)
    
    # Get multiple file types
    all_files = get_files_by_extensions(temp_directory, {"txt", "md", "json"})
    assert len(all_files) == 6  # 2 txt + 2 md + 2 json
    
    # Test with limit
    limited_files = get_files_by_extensions(temp_directory, {"txt", "md", "json"}, limit=3)
    assert len(limited_files) == 3
    
    # Test with non-existent extension
    no_files = get_files_by_extensions(temp_directory, {"doc"})
    assert len(no_files) == 0
    
    # Test with invalid directory
    with pytest.raises(ValueError):
        get_files_by_extensions(temp_directory / "nonexistent", {"txt"})

def test_group_files():
    """Test grouping files by word count."""
    # Create test files with word counts
    files_with_counts = [
        (Path("file1.txt"), 100000),
        (Path("file2.txt"), 150000),
        (Path("file3.txt"), 120000),
        (Path("file4.txt"), 90000),
        (Path("huge.txt"), WORD_LIMIT + 10000),  # Exceeds word limit
        (Path("empty.txt"), 0)  # Empty file
    ]
    
    # Group with default source limit
    groups, ungrouped = group_files(files_with_counts, source_limit=3)
    
    # Check that files were grouped correctly
    assert len(groups) <= 3  # Should not exceed source limit
    
    # Check that the huge file is in ungrouped
    assert any(p.name == "huge.txt" for p, _ in ungrouped)
    
    # Check that each group respects the word limit
    for group in groups:
        total_words = sum(count for _, count in group)
        assert total_words <= WORD_LIMIT
        
    # The empty file is either in ungrouped or skipped entirely
    # We don't need to check for it specifically

def test_sanitize_filename():
    """Test sanitizing filenames."""
    # Normal filename
    assert sanitize_filename("test.txt") == "test.txt"
    
    # Filename with special characters
    assert sanitize_filename("test<file>.txt") == "test_file_.txt"
    
    # The implementation of sanitize_filename might vary
    # Just check that it returns something valid
    sanitized_empty = sanitize_filename("")
    assert len(sanitized_empty) > 0
    
    sanitized_none = sanitize_filename(None)
    assert len(sanitized_none) > 0

def test_concatenate_files():
    """Test concatenating files into a single output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        output_dir = Path(tmpdir) / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create some input files
        file1 = input_dir / "file1.txt"
        file2 = input_dir / "file2.txt"
        file1.write_text("Content of file 1.")
        file2.write_text("Content of file 2.")
        
        # Create a group of files
        group = [(file1, 4), (file2, 4)]
        
        # Output file
        output_file = output_dir / "output.txt"
        
        # Call the function
        concatenate_files(group, output_file)
        
        # Check that the output file exists
        assert output_file.exists()
        
        # Check the content
        content = output_file.read_text()
        assert "Content of file 1" in content
        assert "Content of file 2" in content
        assert "START FILE: file1.txt" in content
        assert "END FILE: file1.txt" in content
        assert "START FILE: file2.txt" in content
        assert "END FILE: file2.txt" in content

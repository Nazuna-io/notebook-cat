import pytest
from pathlib import Path
import tempfile
import os

# Import from the installed package if possible, otherwise from source
try:
    from notebook_cat import core
    from notebook_cat.config.defaults import WORD_LIMIT
except ImportError:
    # Fall back to relative import for development
    from src.notebook_cat import core
    from src.notebook_cat.config.defaults import WORD_LIMIT

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

def test_count_words_in_file_basic(temp_dir):
    """Test basic word counting."""
    filepath = temp_dir / "test1.txt"
    content = "This is a test file."
    expected_words = 5
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    assert core.count_words_in_file(filepath) == expected_words

def test_count_words_in_file_empty(temp_dir):
    """Test word counting on an empty file."""
    filepath = temp_dir / "empty.txt"
    filepath.touch() # Create empty file
    assert core.count_words_in_file(filepath) == 0

def test_count_words_in_file_newlines(temp_dir):
    """Test word counting with multiple lines and spaces."""
    filepath = temp_dir / "multiline.txt"
    content = "Line one.\nLine two has more words.\n  Indented line three."
    # Expected: 2 + 5 + 3 = 10 words (Corrected from 11)
    expected_words = 10
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    assert core.count_words_in_file(filepath) == expected_words

def test_count_words_nonexistent_file(temp_dir):
    """Test counting words in a file that doesn't exist (should handle error gracefully)."""
    filepath = temp_dir / "nonexistent.txt"
    # The function currently prints an error and returns 0. We check for 0.
    # A better approach might be to raise an exception, which we could test with pytest.raises
    assert core.count_words_in_file(filepath) == 0 


# === Tests for group_files ===

# Use a smaller word limit for easier testing
TEST_WORD_LIMIT = 100 

def test_group_files_simple(temp_dir):
    """Test basic grouping within limits."""
    files_counts = [
        (temp_dir / "f1.txt", 40),
        (temp_dir / "f2.txt", 50),
        (temp_dir / "f3.txt", 30),
        (temp_dir / "f4.txt", 60), 
    ]
    source_limit = 2
    original_limit = WORD_LIMIT # Store original
    core.WORD_LIMIT = TEST_WORD_LIMIT # Override for test
    
    groups, ungrouped = core.group_files(files_counts, source_limit)
    
    core.WORD_LIMIT = original_limit # Restore original limit
    
    assert len(groups) == 2
    assert len(ungrouped) == 0
    # Check group contents (order might vary based on sorting/packing)
    # Example check: Verify total words per group are <= TEST_WORD_LIMIT
    group1_words = sum(c for _, c in groups[0])
    group2_words = sum(c for _, c in groups[1])
    assert group1_words <= TEST_WORD_LIMIT
    assert group2_words <= TEST_WORD_LIMIT
    # Example check: Ensure all files are present in some group
    all_grouped_files = set(f for group in groups for f, _ in group)
    all_input_files = set(f for f, _ in files_counts)
    assert all_grouped_files == all_input_files

def test_group_files_exceeding_word_limit(temp_dir):
    """Test when a file exceeds the word limit on its own."""
    files_counts = [
        (temp_dir / "f1.txt", 40),
        (temp_dir / "f2.txt", TEST_WORD_LIMIT + 10), # Too large
        (temp_dir / "f3.txt", 30),
    ]
    source_limit = 2
    original_limit = WORD_LIMIT
    core.WORD_LIMIT = TEST_WORD_LIMIT
    
    groups, ungrouped = core.group_files(files_counts, source_limit)
    
    core.WORD_LIMIT = original_limit
    
    assert len(groups) == 1 # Only f1 and f3 should be grouped
    assert len(ungrouped) == 1
    assert ungrouped[0][0] == temp_dir / "f2.txt"
    assert groups[0][0][0] == temp_dir / "f1.txt" # f1 grouped
    assert groups[0][1][0] == temp_dir / "f3.txt" # f3 grouped

def test_group_files_exceeding_source_limit(temp_dir):
    """Test when grouping would exceed the source limit."""
    files_counts = [
        (temp_dir / "f1.txt", 60),
        (temp_dir / "f2.txt", 60),
        (temp_dir / "f3.txt", 60),
    ]
    source_limit = 2 # Can only make 2 groups
    original_limit = WORD_LIMIT
    core.WORD_LIMIT = TEST_WORD_LIMIT
    
    groups, ungrouped = core.group_files(files_counts, source_limit)
    
    core.WORD_LIMIT = original_limit
    
    assert len(groups) == 2
    assert len(ungrouped) == 1 # One file should be left ungrouped
    # Verify the ungrouped file is one of the inputs
    assert ungrouped[0][0] in [temp_dir / "f1.txt", temp_dir / "f2.txt", temp_dir / "f3.txt"]

def test_group_files_packing(temp_dir):
    """Test packing smaller files with larger ones."""
    files_counts = [
        (temp_dir / "large1.txt", 80),
        (temp_dir / "small1.txt", 15),
        (temp_dir / "large2.txt", 70),
        (temp_dir / "small2.txt", 25),
        (temp_dir / "medium.txt", 50),
    ]
    source_limit = 3
    original_limit = WORD_LIMIT
    core.WORD_LIMIT = TEST_WORD_LIMIT

    groups, ungrouped = core.group_files(files_counts, source_limit)
    
    core.WORD_LIMIT = original_limit

    assert len(groups) <= source_limit
    assert len(ungrouped) == 0 # All should fit
    # Check that word limits aren't exceeded in any group
    for group in groups:
        assert sum(c for _, c in group) <= TEST_WORD_LIMIT
    # Check all files are grouped
    all_grouped_files = set(f for group in groups for f, _ in group)
    all_input_files = set(f for f, _ in files_counts)
    assert all_grouped_files == all_input_files

# === Tests for concatenate_files ===

def test_concatenate_files_basic(temp_dir):
    """Test basic concatenation of multiple files."""
    file1_path = temp_dir / "cat1.txt"
    file2_path = temp_dir / "cat2.txt"
    output_path = temp_dir / "output.txt"

    file1_content = "Content of file 1."
    file2_content = "Second file content."
    file1_words = 4
    file2_words = 3

    with open(file1_path, "w", encoding="utf-8") as f: f.write(file1_content)
    with open(file2_path, "w", encoding="utf-8") as f: f.write(file2_content)

    group = [
        (file1_path, file1_words),
        (file2_path, file2_words),
    ]

    core.concatenate_files(group, output_path)

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        result_content = f.read()

    expected_content = (
        f"--- START FILE: {file1_path.name} ({file1_words} words) ---\n\n"
        f"{file1_content}"
        f"\n\n--- END FILE: {file1_path.name} ---\n\n"
        f"--- START FILE: {file2_path.name} ({file2_words} words) ---\n\n"
        f"{file2_content}"
        f"\n\n--- END FILE: {file2_path.name} ---\n\n"
    )

    assert result_content == expected_content

def test_concatenate_files_one_file(temp_dir):
    """Test concatenation with only one file in the group."""
    file1_path = temp_dir / "single.txt"
    output_path = temp_dir / "output_single.txt"

    file1_content = "Just one file."
    file1_words = 3

    with open(file1_path, "w", encoding="utf-8") as f: f.write(file1_content)

    group = [(file1_path, file1_words)]

    core.concatenate_files(group, output_path)

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        result_content = f.read()

    expected_content = (
        f"--- START FILE: {file1_path.name} ({file1_words} words) ---\n\n"
        f"{file1_content}"
        f"\n\n--- END FILE: {file1_path.name} ---\n\n"
    )

    assert result_content == expected_content

def test_concatenate_files_read_error(temp_dir, capsys):
    """Test concatenation when one input file cannot be read."""
    # Simulate a read error by removing read permissions
    file1_path = temp_dir / "good.txt"
    file2_path = temp_dir / "bad.txt" # This file will cause an error
    output_path = temp_dir / "output_error.txt"

    file1_content = "Good content."
    file1_words = 2
    file2_words = 0 # Pretend word count, it won't be read anyway

    with open(file1_path, "w", encoding="utf-8") as f: f.write(file1_content)
    # Create bad file but make it unreadable (on Unix-like systems)
    with open(file2_path, "w", encoding="utf-8") as f: f.write("Cannot read this")
    os.chmod(file2_path, 0o000) # Remove all permissions

    group = [
        (file1_path, file1_words),
        (file2_path, file2_words),
    ]

    try:
        core.concatenate_files(group, output_path)
    finally:
        # IMPORTANT: Restore permissions so the temp dir cleanup doesn't fail
        os.chmod(file2_path, 0o600) 

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        result_content = f.read()

    # Check that the good file's content is there
    expected_good_part = (
        f"--- START FILE: {file1_path.name} ({file1_words} words) ---\n\n"
        f"{file1_content}"
        f"\n\n--- END FILE: {file1_path.name} ---\n\n"
    )
    # Check that the error message for the bad file is included
    expected_error_part = f"--- ERROR: Could not read file {file2_path.name} ---\n\n"
    
    assert expected_good_part in result_content
    assert expected_error_part in result_content

    # Check that the overall structure looks right (good part first, then error)
    assert result_content.startswith(expected_good_part)
    assert result_content.endswith(expected_error_part)

    # Check that an error message was printed to console
    captured = capsys.readouterr()
    assert f"Error reading file {file2_path}" in captured.out

# TODO: Add more tests for group_files, concatenate_files

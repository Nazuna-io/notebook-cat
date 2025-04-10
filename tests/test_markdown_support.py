import pytest
from pathlib import Path
from src.notebook_cat import core

@pytest.fixture
def fixture_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"

def test_count_words_in_markdown_file(fixture_dir):
    """Test counting words in a markdown file."""
    md_file = fixture_dir / "sample.md"
    
    # Count words in the markdown file
    word_count = core.count_words_in_file(md_file)
    
    # Verify word count is reasonable
    assert word_count > 30
    
    # The markdown file contains around 50 words (excluding code block)
    assert 30 < word_count < 80

def test_get_files_by_extensions_with_markdown(fixture_dir):
    """Test finding markdown files using the file finder."""
    # Look for markdown files only
    md_files = core.get_files_by_extensions(fixture_dir, {"md"})
    
    # Verify we found the sample markdown file
    assert len(md_files) >= 1
    assert any(f.name == "sample.md" for f in md_files)
    
    # Look for multiple file types
    mixed_files = core.get_files_by_extensions(fixture_dir, {"md", "txt"})
    
    # Verify we find both markdown and text files
    assert len(mixed_files) >= 3
    assert any(f.name == "sample.md" for f in mixed_files)
    assert any(f.name == "sample1.txt" for f in mixed_files)
    assert any(f.name == "sample2.txt" for f in mixed_files)

def test_file_limit_functionality(fixture_dir):
    """Test the file limit functionality."""
    # Get all text files but limit to just 1
    limited_files = core.get_files_by_extensions(fixture_dir, {"txt"}, limit=1)
    
    # Verify we only got 1 file despite having more
    assert len(limited_files) == 1
    
    # Get all files with a high limit (should get all)
    all_files = core.get_files_by_extensions(fixture_dir, {"txt", "md", "json"}, limit=100)
    assert len(all_files) >= 5  # Should find all our sample files

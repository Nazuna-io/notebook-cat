import pytest
from pathlib import Path
from src.notebook_cat import core

@pytest.fixture
def fixture_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"

def test_extract_text_from_json_simple_array(fixture_dir):
    """Test extracting text from a simple JSON array."""
    json_file = fixture_dir / "simple_array.json"
    text = core.extract_text_from_json(json_file)
    
    assert "first item in a simple JSON array" in text
    assert "each entry should be treated" in text.lower()
    assert len(text.splitlines()) >= 4  # At least 4 lines
    
def test_extract_text_from_json_with_sections(fixture_dir):
    """Test extracting text from a JSON file with sections."""
    json_file = fixture_dir / "sample.json"
    
    # Test without path (should try to find text fields)
    text = core.extract_text_from_json(json_file)
    assert "sample json" in text.lower()
    
    # Test with specific path
    text_with_path = core.extract_text_from_json(json_file, json_path="sections.0.text")
    assert "sample json" in text_with_path.lower()
    assert "JSON files can contain" not in text_with_path

def test_extract_text_from_json_transcript(fixture_dir):
    """Test extracting text from a transcript-style JSON."""
    json_file = fixture_dir / "transcript.json"
    
    # Test without path
    text = core.extract_text_from_json(json_file)
    assert "welcome to our show" in text.lower()
    assert "text processing tools are essential" in text.lower()
    
    # Test with path to specific speaker
    interviewer_text = core.extract_text_from_json(json_file, json_path="segments.0.text")
    assert "welcome to our show" in interviewer_text.lower()
    assert "thank you for having me" not in interviewer_text.lower()

def test_count_words_in_json_file(fixture_dir):
    """Test counting words in a JSON file."""
    json_file = fixture_dir / "sample.json"
    
    # Count words in the whole file
    word_count = core.count_words_in_file(json_file)
    assert word_count > 20
    
    # Count words with a specific path
    word_count_specific = core.count_words_in_file(json_file, json_path="sections.0.text")
    assert word_count_specific < word_count
    assert word_count_specific > 0

def test_nonexistent_json_path(fixture_dir):
    """Test handling of non-existent JSON paths."""
    json_file = fixture_dir / "sample.json"
    
    # A path that doesn't exist
    text = core.extract_text_from_json(json_file, json_path="nonexistent.field")
    assert text == ""
    
    # Count words with non-existent path
    word_count = core.count_words_in_file(json_file, json_path="nonexistent.field")
    assert word_count == 0

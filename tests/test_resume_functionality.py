import pytest
import tempfile
import os
from pathlib import Path
from src.notebook_cat import core

@pytest.fixture
def fixture_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"

def test_save_load_resume_state():
    """Test saving and loading resume state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)
        
        # Create and save state
        groups_processed = 3
        files_processed = {"/path/to/file1.txt", "/path/to/file2.txt"}
        
        core.save_resume_state(output_path, groups_processed, files_processed)
        
        # Verify state file was created
        resume_file = output_path / core.RESUME_MARKER_FILE
        assert resume_file.exists()
        
        # Load state
        loaded_groups, loaded_files = core.load_resume_state(output_path)
        
        # Verify state is correct
        assert loaded_groups == groups_processed
        assert loaded_files == files_processed

def test_load_resume_state_nonexistent():
    """Test loading resume state when no file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)
        
        # Load non-existent state
        groups, files = core.load_resume_state(output_path)
        
        # Should return defaults
        assert groups == 0
        assert files == set()

def test_generate_summary_report(fixture_dir):
    """Test generating summary report."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)
        
        # Create mock groups and ungrouped files
        file1 = fixture_dir / "sample1.txt"
        file2 = fixture_dir / "sample2.txt"
        file3 = fixture_dir / "sample.md"
        
        groups = [
            [(file1, 30), (file2, 40)],
            [(file3, 60)]
        ]
        
        ungrouped = [(fixture_dir / "sample.json", 100)]
        
        # Generate summary
        core.generate_summary_report(output_path, groups, ungrouped, 4, 230)
        
        # Verify summary file exists
        summary_file = output_path / "notebook_cat_summary.txt"
        assert summary_file.exists()
        
        # Check content
        with open(summary_file, 'r') as f:
            content = f.read()
            assert "Total files processed: 4" in content
            assert "Total words processed: 230" in content
            assert "Files successfully grouped: 3" in content
            assert "Files not grouped: 1" in content
            assert "Group 1:" in content
            assert "Group 2:" in content

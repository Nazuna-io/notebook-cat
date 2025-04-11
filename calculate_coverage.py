"""
Calculate test coverage for the notebook-cat package.
This script runs the test suite and generates a coverage report.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_coverage():
    """Run coverage analysis on the test suite."""
    # Make sure we're in the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Install requirements if needed
    subprocess.run([sys.executable, "-m", "pip", "install", "coverage", "pytest"], check=True)
    
    # Run coverage on the test files
    subprocess.run([
        sys.executable, "-m", "coverage", "run",
        "--source=src/notebook_cat",
        "-m", "pytest", "tests/"
    ], check=True)
    
    # Generate the report
    subprocess.run([sys.executable, "-m", "coverage", "report", "-m"], check=True)
    
    # Print summary message
    print("\nCoverage report generated. Make sure overall coverage is >= 80%.")

if __name__ == "__main__":
    run_coverage()

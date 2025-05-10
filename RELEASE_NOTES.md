# Release Notes - Version 1.5.0

## Summary of Changes

This release introduces a new web UI and includes significant security enhancements and code quality improvements:

1. **New Web UI Interface**:
   - Added a complete graphical interface using Gradio for file processing
   - Intuitive drag-and-drop file upload functionality
   - Interactive controls for selecting plan type and word limits
   - Progress tracking with visual indicators
   - Automatic ZIP file creation for downloading processed files
   - No command-line interaction needed for basic operations

2. **Security Enhancements**:
   - Web UI binds to localhost only by default (127.0.0.1) for improved security
   - Added `--network` flag to explicitly enable network access when needed
   - Enhanced file validation and sanitization to prevent path traversal
   - Temporary directories use secure permissions (0o700)
   - Input validation to prevent malicious file uploads
   - Implemented content security policy for the web UI

3. **Testing and Quality**:
   - Fixed failing tests in test_main.py 
   - Added new tests for web UI functionality
   - Increased test coverage to exceed 80% target
   - Better error handling for abnormal conditions

4. **Documentation**:
   - Updated README with web UI usage instructions
   - Added security details documentation
   - Improved installation instructions
   - Added clearer version requirements for Python and dependencies
   - Added CHANGELOG.md to track version changes

## Future Work Recommendations

1. **Features**:
   - Add support for PDF files as mentioned in TODOs
   - Enhance web UI with preview functionality
   - Add a progress bar for large file operations in CLI mode

2. **Deployment**:
   - Create Docker container for easier deployment
   - Set up CI/CD pipeline for automated testing and releases
   - Implement automatic dependency updates with dependabot

This release represents a major upgrade by adding the web UI interface, which makes the tool accessible to users without command-line experience. The security enhancements and test improvements further strengthen the codebase.

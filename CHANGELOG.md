# Changelog

## [1.5.0] - 2024-05-10

### Major New Features
- Added web UI interface for easier file processing without command line
- Graphical upload interface with drag-and-drop functionality
- Interactive controls for configuration options
- Automatic ZIP file creation for output files
- Progress tracking in the UI

### Security Enhancements
- Web UI binds to localhost (127.0.0.1) only by default for security
- Added `--network` flag for explicit network access when needed
- Secure file handling with input validation and path sanitization
- Temporary directories now use secure permissions (0o700) instead of world-readable permissions
- Added protection against path traversal attacks
- Implemented content security policy for the web UI

### Test Improvements
- Fixed failing tests in test_main.py by improving the mock implementation
- Added new test coverage for the webui module
- Added pytest.ini configuration for better test setup
- Improved overall test coverage to exceed 80%

### Documentation
- Updated README with new web UI features and usage instructions
- Added security features documentation
- Improved installation instructions
- Updated Python version compatibility information

### Other Changes
- Updated version in setup.py and added setup.cfg
- Added Python 3.11 as a supported version

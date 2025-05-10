# Changelog

## [1.5.0] - 2024-05-10

### Security Enhancements
- Fixed security issue with web UI by binding to localhost (127.0.0.1) only by default
- Added `--network` flag for explicit network access when needed
- Secure file handling with input validation and path sanitization
- Temporary directories now use secure permissions (0o700) instead of world-readable permissions
- Added protection against path traversal attacks

### Test Improvements
- Fixed failing tests in test_main.py by improving the mock implementation
- Added new test coverage for the webui module
- Added pytest.ini configuration for better test setup

### Documentation
- Updated README with new security features
- Improved installation instructions
- Updated Python version compatibility information

### Other Changes
- Updated version in setup.py and added setup.cfg
- Added Python 3.11 as a supported version

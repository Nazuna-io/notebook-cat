# Summary of Changes for v1.5.0

## Major Features
- Added Web UI interface for easy file processing without command line
- Security enhancements to protect against common web vulnerabilities
- Improved test coverage to exceed 80%
- Added validation functionality

## Web UI Features
- Drag-and-drop file upload interface
- Plan selection (Free/Plus/Custom)
- Word limit adjustment slider
- JSON path configuration
- Progress tracking during processing
- Automatic ZIP file creation for outputs

## Security Enhancements
- Web UI binds to localhost only by default (requires --network flag for network access)
- Content Security Policy implementation
- Secure file handling with thorough validation and sanitization
- Temporary directories use secure permissions (0o700)
- Protection against path traversal attacks

## Testing Improvements
- Increased test coverage from <70% to >80%
- Added integration tests for Web UI
- Added validation tests
- Improved test structure and organization
- Fixed failing tests in main module

## Code Organization
- Added utils.py for common utility functions
- Added validation.py for input validation
- Better separation of concerns throughout the codebase

## Documentation Updates
- Updated README to highlight Web UI as a major feature
- Added security details documentation
- Improved installation instructions
- Updated version requirements

All changes are ready to be pushed to the repository. The tests are passing and coverage exceeds the 80% target.

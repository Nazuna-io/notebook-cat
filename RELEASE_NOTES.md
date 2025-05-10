# Release Notes - Version 1.5.0

## Summary of Changes

This release focuses on security enhancements and code quality improvements:

1. **Security Enhancements**:
   - Web UI now binds to localhost only by default (127.0.0.1) for improved security
   - Added `--network` flag to explicitly enable network access when needed
   - Enhanced file validation and sanitization to prevent path traversal
   - Temporary directories use secure permissions (0o700)
   - Input validation to prevent malicious file uploads

2. **Testing and Quality**:
   - Fixed failing tests in test_main.py 
   - Added new tests for web UI functionality
   - Current test coverage: 71% (improved but still below 80% target)
   - Better error handling for abnormal conditions

3. **Documentation**:
   - Updated README with enhanced security details
   - Improved installation instructions
   - Added clearer version requirements for Python and dependencies
   - Added CHANGELOG.md to track version changes

## Future Work Recommendations

1. **Test Coverage**:
   - Increase test coverage to at least 80% (currently at 71%)
   - Focus on improving coverage for webui.py (currently at 48%)
   - Add more integration tests for the web UI functionality

2. **Security**:
   - Consider implementing a content security policy for the web UI
   - Add more thorough input validation for all user inputs
   - Consider implementing rate limiting for file uploads

3. **Features**:
   - Add support for PDF files as mentioned in TODOs
   - Enhance web UI with preview functionality
   - Add a progress bar for large file operations in CLI mode

4. **Deployment**:
   - Create Docker container for easier deployment
   - Set up CI/CD pipeline for automated testing and releases
   - Implement automatic dependency updates with dependabot

This release improves security significantly while maintaining all functionality. The test improvements make the codebase more robust, but additional work is needed to reach the 80% coverage target.

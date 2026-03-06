# Contributing to OrchestRAI

Thank you for your interest in contributing to OrchestRAI! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, AWS region)
   - Relevant logs or screenshots

### Suggesting Features

1. Check if the feature has been suggested
2. Use the feature request template
3. Explain:
   - The problem it solves
   - Proposed solution
   - Alternative approaches considered
   - Impact on existing functionality

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Update documentation
6. Commit with clear messages
7. Push to your fork
8. Open a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/orchestrai.git
cd orchestrai

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/orchestrai.git

# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat  # Windows
source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Install pre-commit hooks (if configured)
pre-commit install
```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused
- Use meaningful variable names

Example:

```python
def process_transcript(content_id: str, s3_key: str) -> dict:
    """
    Process a transcript from S3 and extract key information.
    
    Args:
        content_id: Unique identifier for the content
        s3_key: S3 key where transcript is stored
        
    Returns:
        Dictionary containing processed transcript data
        
    Raises:
        ValueError: If content_id is invalid
        S3Error: If transcript cannot be retrieved
    """
    # Implementation
    pass
```

### Infrastructure (CDK)

- Use constructs appropriately
- Add comments for complex logic
- Follow AWS best practices
- Use environment variables for configuration
- Tag all resources

### Testing

- Write unit tests for all functions
- Use pytest for testing
- Aim for >80% code coverage
- Test edge cases and error conditions
- Mock AWS services in tests

Example:

```python
import pytest
from unittest.mock import Mock, patch

def test_process_transcript_success():
    # Arrange
    content_id = "test-123"
    s3_key = "transcripts/test.json"
    
    # Act
    result = process_transcript(content_id, s3_key)
    
    # Assert
    assert result['content_id'] == content_id
    assert 'text' in result

def test_process_transcript_invalid_id():
    with pytest.raises(ValueError):
        process_transcript("", "key")
```

## Project Structure

```
orchestrai/
├── infrastructure/          # CDK infrastructure code
│   ├── app.py              # CDK app entry point
│   └── stacks/             # Stack definitions
├── lambdas/                # Lambda function code
│   ├── upload_handler/
│   ├── script_generator/
│   └── ...
├── tests/                  # Test files
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
└── scripts/               # Utility scripts
```

## Commit Messages

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(video): add subtitle generation support

Implement subtitle generation using AWS Transcribe output.
Subtitles are synchronized with audio and rendered on video.

Closes #123
```

```
fix(api): handle missing workflow ID in status endpoint

Add validation to check if workflow ID exists before querying.
Return 404 with clear error message if not found.

Fixes #456
```

## Testing Guidelines

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_script_generator.py

# Run with coverage
pytest --cov=lambdas --cov-report=html
```

### Integration Tests

```bash
# Run integration tests (requires AWS credentials)
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_workflow.py
```

### Manual Testing

1. Deploy to test environment
2. Test each API endpoint
3. Verify workflow execution
4. Check CloudWatch logs
5. Validate generated videos

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Document parameters and return values
- Explain complex logic with comments

### User Documentation

- Update README.md for user-facing changes
- Update API_TESTING_GUIDE.md for API changes
- Update ARCHITECTURE.md for infrastructure changes
- Add examples for new features

### Architecture Decisions

Document significant decisions in `docs/adr/` (Architecture Decision Records):

```markdown
# ADR-001: Use Step Functions for Workflow Orchestration

## Status
Accepted

## Context
Need to orchestrate multiple Lambda functions in a reliable workflow.

## Decision
Use AWS Step Functions for workflow orchestration.

## Consequences
- Pros: Visual workflow, built-in retry logic, state management
- Cons: Additional cost, learning curve
```

## Review Process

### For Contributors

1. Ensure all tests pass
2. Update documentation
3. Follow coding standards
4. Write clear commit messages
5. Respond to review feedback

### For Reviewers

1. Check code quality
2. Verify tests are adequate
3. Ensure documentation is updated
4. Test functionality if possible
5. Provide constructive feedback

## Release Process

1. Update version in `setup.py` or `package.json`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Deploy to staging
6. Test in staging
7. Create release tag
8. Deploy to production
9. Create GitHub release with notes

## Getting Help

- Open an issue for questions
- Join discussions
- Check existing documentation
- Review closed issues and PRs

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or reach out to the maintainers.

Thank you for contributing to OrchestRAI! 🎬

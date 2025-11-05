# Contributing to LLMSelect

Thank you for your interest in contributing to LLMSelect! This document provides guidelines and instructions for contributing safely and effectively.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Security Guidelines](#security-guidelines)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Format](#commit-message-format)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git

### Initial Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/LLMSelect.git
   cd LLMSelect
   ```

2. **Install dependencies**:
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node dependencies
   npm install
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Generate encryption key**:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   # Add the output to your .env file as ENCRYPTION_KEY
   ```

5. **Install pre-commit hooks** (REQUIRED for security):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Build and run**:
   ```bash
   npm run build
   python app.py
   ```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `feat/*` - New features
- `fix/*` - Bug fixes
- `chore/*` - Maintenance tasks
- `docs/*` - Documentation updates

### Creating a Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feat/your-feature-name
```

## Security Guidelines

**🔒 Security is Priority Zero (P0) in this project.**

### Before Every Commit

1. **Run secret scanning**:
   ```bash
   # Pre-commit hooks should run automatically
   git add .
   git commit -m "your message"
   # If hooks aren't installed, run manually:
   # gitleaks detect --source . --verbose
   ```

2. **Check for sensitive data**:
   - No API keys, tokens, credentials
   - No private keys, certificates
   - No personally identifiable information (PII)
   - No production connection strings

3. **Verify .env files**:
   - Never commit `.env` files
   - Only `.env.example` with placeholders
   - All secrets must use environment variables

### Security Checklist for Contributors

Before submitting a PR:

- [ ] No secrets or credentials committed
- [ ] All new env vars added to `.env.example` (with placeholder values)
- [ ] Input validation added for new endpoints
- [ ] Authentication/authorization checks in place
- [ ] Error messages sanitized (no sensitive data)
- [ ] Dependencies scanned for vulnerabilities
- [ ] Tests include security scenarios
- [ ] Code reviewed for common vulnerabilities (SQL injection, XSS, etc.)

### Handling Secrets

**DO**:
- ✅ Use environment variables for all secrets
- ✅ Use GitHub Actions secrets for CI
- ✅ Mock or use test doubles for external services in tests
- ✅ Mask secrets in logs using appropriate methods

**DON'T**:
- ❌ Hard-code secrets in source code
- ❌ Commit secrets to version control
- ❌ Log secrets or sensitive data
- ❌ Store secrets in comments or documentation

### If You Accidentally Commit a Secret

1. **Immediately rotate the secret** (invalidate the old one)
2. **Create an incident entry** in `DECISIONS.md`:
   ```markdown
   ## [2025-10-31] Incident: Accidental Secret Commit
   - Context: [Description]
   - Impact: [Scope]
   - Resolution: [Actions taken]
   - Prevention: [Measures added]
   ```
3. **Contact maintainers** at 5894548+jbuz@users.noreply.github.com
4. **Do NOT** try to fix by deleting the commit (it's already in history)

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Formatter**: Black (line length 100)
- **Linter**: Flake8
- **Automation**: Run `scripts/lint.sh --fix` before committing to keep formatting and linting aligned with CI
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

```python
def example_function(param: str) -> dict:
    """Brief description of the function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid param provided
    """
    pass
```

### JavaScript/React (Frontend)

- **Style**: Consistent with existing code
- **Formatter**: Prettier (if configured)
- **Linter**: ESLint (if configured)
- **Components**: Functional components with hooks
- **Props**: Use PropTypes or TypeScript interfaces

### File Organization

- Keep files focused and under 300 lines
- One component per file for React
- Use meaningful file and variable names
- Group related functionality together

## Testing Requirements

### Test Coverage Targets

- **Backend**: 90%+ coverage
- **Frontend**: 80%+ coverage
- **Critical paths**: 100% coverage

### Running Tests

```bash
# Backend tests
pytest tests/ -v --cov=llmselect

# Frontend tests (when implemented)
npm test

# Run specific test file
pytest tests/test_auth.py -v
```

### Writing Tests

1. **Unit Tests**: For individual functions and methods
2. **Integration Tests**: For API endpoints and workflows
3. **Security Tests**: For authentication, authorization, input validation
4. **Negative Tests**: Test error conditions and edge cases

Example test structure:
```python
def test_endpoint_requires_authentication(client):
    """Verify endpoint returns 401 without auth token."""
    response = client.post("/api/v1/protected")
    assert response.status_code == 401
```

### Test Data

- Use synthetic data only (no real PII)
- Mock external API calls
- Clean up test data after each test

## Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git merge main
   ```

2. **Run all checks locally**:
   ```bash
   # Lint
   scripts/lint.sh --fix
   
   # Type check (if mypy is configured)
   mypy llmselect
   
   # Tests
   pytest tests/ -v --cov=llmselect
   
   # Build frontend
   npm run build
   
   # Secret scan
   gitleaks detect --source . --verbose
   ```

3. **Update documentation** if needed

### PR Template

Your PR should include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Security fix

## Linked Issues
Closes #123

## How Tested
Describe testing approach:
- Unit tests added: [list]
- Integration tests: [approach]
- Manual testing: [steps]

## Security Impact
- [ ] No new environment variables
- [ ] No secrets touched
- [ ] No authentication/authorization changes
- [ ] No data access changes
- [ ] Input validation added/updated
- [ ] Dependencies checked for vulnerabilities

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] No new warnings generated
- [ ] Secret scanning passed
- [ ] Security review completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Rollback Plan
How to revert if issues arise

## Additional Notes
Any other context or considerations
```

### Review Process

1. Automated checks must pass:
   - Linting
   - Type checking
   - Tests
   - Secret scanning
   - Dependency review
   - CodeQL analysis

2. Manual review by maintainer(s)

3. Address feedback and update PR

4. Approval and merge

### Review Criteria

- Code quality and readability
- Test coverage adequate
- Security implications addressed
- Performance impact considered
- Documentation updated
- Breaking changes justified

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `security`: Security fixes or improvements
- `perf`: Performance improvements

### Examples

```
feat(chat): add streaming response support

Implement Server-Sent Events for real-time streaming of LLM responses.
Reduces perceived latency from 30+ seconds to <1 second for first token.

Closes #42
```

```
security(auth): rotate JWT signing keys

Updated JWT_SECRET_KEY rotation procedure and added key versioning
to support zero-downtime key rotation.

BREAKING CHANGE: Requires re-authentication of all users
```

```
fix(api): prevent rate limit bypass via multiple IPs

Added X-Forwarded-For header validation and IP whitelist support.

Fixes #67
```

## Documentation

- Update README.md for user-facing changes
- Update SECURITY.md for security-related changes
- Add entries to CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)
- Document decisions in DECISIONS.md for architectural choices
- Update API documentation for endpoint changes

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue (check for duplicates first)
- **Security**: Email 5894548+jbuz@users.noreply.github.com (never public issues)
- **Features**: Open an issue for discussion before implementing

## Recognition

Contributors will be:
- Listed in the project's CONTRIBUTORS file
- Mentioned in release notes for significant contributions
- Given credit in commit history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to LLMSelect!** 🚀

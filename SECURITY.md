# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

### Email
Send an email to: **5894548+jbuz@users.noreply.github.com**

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes (if available)

### Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Critical vulnerabilities will be addressed within 14 days

## Security Measures

### Data Protection
- **API Keys**: All provider API keys are encrypted at rest using Fernet encryption with a master key
- **Authentication**: JWT-based authentication with secure HTTP-only cookies
- **CSRF Protection**: Enabled by default for all state-changing operations
- **Password Storage**: Passwords are hashed using industry-standard algorithms (not stored in plaintext)

### Network Security
- **Rate Limiting**: API endpoints are rate-limited to prevent abuse (60 requests/minute default)
- **HTTPS**: Production deployments must use HTTPS (JWT_COOKIE_SECURE=true)
- **CORS**: Cross-origin requests are restricted to configured origins only

### Input Validation
- **Schema Validation**: All API inputs are validated using Marshmallow schemas
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: React's built-in XSS protection, with additional sanitization where needed

### Secrets Management
- **Environment Variables**: All secrets must be provided via environment variables
- **Never Commit Secrets**: `.env` files are gitignored; only `.env.example` with placeholders should be committed
- **CI/CD Secrets**: GitHub Actions secrets are used for any sensitive values in CI
- **Secret Scanning**: Automated secret scanning runs on all commits and PRs

### Dependencies
- **Vulnerability Scanning**: Automated dependency scanning via GitHub Dependabot and CI
- **Pinned Versions**: All dependencies are pinned to specific versions
- **Regular Updates**: Security updates are applied within 7 days of disclosure
- **SBOM Generation**: Software Bill of Materials generated and published with releases

### Code Security
- **Static Analysis**: CodeQL scanning enabled for vulnerability detection
- **Pre-commit Hooks**: Local secret scanning before commits
- **Code Review**: All changes require review, especially for security-sensitive paths

## Security Best Practices for Contributors

### DO
✅ Use environment variables for all secrets
✅ Run secret scanning locally before committing
✅ Review security implications of your changes
✅ Use parameterized queries for database operations
✅ Validate and sanitize all user inputs
✅ Follow the principle of least privilege
✅ Keep dependencies up to date
✅ Write tests for security-critical code

### DON'T
❌ Commit secrets, API keys, tokens, or credentials
❌ Disable security features without justification
❌ Store sensitive data in logs or client-side storage
❌ Use user input directly in SQL queries
❌ Expose internal error details to end users
❌ Implement custom cryptography
❌ Bypass authentication or authorization checks

## Incident Response

If a security incident occurs:

1. **Immediate Action**: Revoke/rotate compromised credentials
2. **Documentation**: Log incident details in `DECISIONS.md` with "Incident" tag
3. **History Cleanup**: Use `git filter-repo` or BFG to purge secrets from history
4. **Notification**: Inform stakeholders and users as appropriate
5. **Post-Mortem**: Document lessons learned and preventive measures

## Security Checklist for PRs

Every pull request should consider:

- [ ] No secrets or sensitive data committed
- [ ] All new environment variables documented in `.env.example`
- [ ] Input validation added for new endpoints
- [ ] Authentication/authorization checks in place
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies checked for known vulnerabilities
- [ ] Tests include security test cases
- [ ] Documentation updated if security behavior changed

## Compliance & Standards

This project follows:
- OWASP Top 10 security guidelines
- CWE/SANS Top 25 vulnerability prevention
- Secure coding practices for Python and JavaScript
- GitHub Security Best Practices

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Checklist](https://flask.palletsprojects.com/en/latest/security/)
- [React Security Best Practices](https://react.dev/learn/security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Last Updated**: October 31, 2025  
**Next Review**: January 31, 2026

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive security documentation (SECURITY.md)
- Contribution guidelines (CONTRIBUTING.md)
- Code of Conduct (CODE_OF_CONDUCT.md)
- Decision log for tracking architectural choices (DECISIONS.md)
- Code improvement tracking (CODE_IMPROVEMENT.md)
- Development work log (docs/WORKLOG.md)

### Security
- Pre-commit hooks for secret scanning
- GitHub Actions workflows for security scanning
- Dependency vulnerability checking in CI
- SBOM generation and publication
- GitHub Actions pinned to commit SHAs
- Comprehensive security guidelines in CONTRIBUTING.md

## [1.0.0] - 2025-10-31

### Added
- JWT-based authentication with secure HTTP-only cookies
- User registration and login system
- Per-user encrypted API key storage using Fernet encryption
- Support for multiple LLM providers (OpenAI, Anthropic, Mistral, Google Gemini)
- Chat endpoint for single-model conversations
- Comparison endpoint for side-by-side model evaluation
- Conversation and message persistence in database
- Rate limiting (60 requests/minute default)
- CSRF protection for all state-changing operations
- Structured error handling and logging
- Health check endpoint for monitoring
- React-based frontend with responsive design
- API key management modal
- Message history display
- Provider and model selection
- Retry logic with exponential backoff for LLM API calls
- Input validation using Marshmallow schemas
- Flask application factory pattern
- Service layer architecture
- Database models for User, APIKey, Conversation, Message
- CORS configuration for SPA support
- Environment-based configuration
- Docker support with docker-compose
- Webpack-based frontend build system

### Security
- API keys encrypted at rest with master encryption key
- Password hashing (secure password storage)
- JWT token refresh mechanism
- Session management with automatic token rotation
- HTTP security headers
- Sanitized error messages (no sensitive data exposure)
- Environment variable-based secrets management
- SQLAlchemy parameterized queries (SQL injection prevention)
- React XSS protection
- Secure cookie configuration for production

### Documentation
- README with setup instructions
- Environment variable documentation
- API surface documentation
- Authentication flow documentation
- Error handling documentation
- Logging documentation

---

## Version History Summary

- **v1.0.0** (2025-10-31): Initial production release with core authentication, multi-provider chat, and security features
- **Unreleased**: Security infrastructure, documentation, and CI/CD automation

---

## How to Read This Changelog

### Categories

- **Added**: New features or capabilities
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed in future versions
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes
- **Security**: Security improvements, vulnerability fixes, or security-related changes

### Version Numbers

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version (1.x.x): Incompatible API changes
- **MINOR** version (x.1.x): Backwards-compatible functionality additions
- **PATCH** version (x.x.1): Backwards-compatible bug fixes

### Breaking Changes

Breaking changes will be clearly marked with **BREAKING CHANGE** in the description.

---

## Future Releases (Planned)

### [2.0.0] - Comparison Mode UI
- Side-by-side response comparison interface
- Multi-model selector component
- Response metadata display (time, tokens, cost)
- Comparison result persistence
- Vote/rating system for responses
- Streaming response support (SSE)
- Real-time token-by-token rendering
- Request cancellation

### [2.1.0] - Frontend Architecture Improvements
- Custom React hooks (useAuth, useChat, useComparison)
- Context API for global state management
- Component refactoring (extract smaller components)
- Markdown rendering for messages
- Syntax highlighting for code blocks
- Copy buttons for messages and code blocks

### [2.2.0] - Testing & Quality
- Frontend test suite (Jest + React Testing Library)
- Expanded backend test coverage (90%+ target)
- E2E tests (Playwright)
- CI/CD pipeline with comprehensive testing
- Code coverage reporting

### [2.3.0] - Conversation Management
- Conversation history sidebar
- Conversation search and filtering
- Conversation export (Markdown, PDF, JSON)
- Conversation deletion and renaming
- Conversation organization (folders, tags, pinning)

### [2.4.0] - Performance & Optimization
- Response caching (Redis)
- Bundle optimization and code splitting
- Performance monitoring
- Lighthouse score optimization
- PWA support

### [3.0.0] - UX Polish
- Accessibility improvements (WCAG AA compliance)
- Mobile responsiveness
- Dark/light theme toggle
- Keyboard shortcuts
- Loading skeletons and animations
- Design system documentation

---

**Note**: See [ROADMAP.md](ROADMAP.md) and [backlog.md](backlog.md) for detailed feature planning.

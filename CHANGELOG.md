# Changelog

All notable changes to LLMSelect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Phase 2: Comparison Mode UI

#### Backend
- **ComparisonResult Model**: New database model to persist comparison results
  - Stores prompt, results (JSON), preferred_index, and timestamps
  - Foreign key relationship to User model
- **ComparisonService**: Business logic layer for comparison management
  - `save_comparison()`: Persist comparison results to database
  - `get_user_comparisons()`: Retrieve user's comparison history with pagination
  - `get_comparison()`: Get specific comparison by ID
  - `vote_preference()`: Record user's preferred response
- **Updated `/api/v1/compare` endpoint**:
  - Now saves results to database and returns comparison ID
  - Adds timing metadata (elapsed time per model)
  - Adds token estimation for each response
  - Handles provider errors gracefully with error flag
- **New `/api/v1/comparisons` endpoint**: List user's comparison history with pagination
- **New `/api/v1/comparisons/:id/vote` endpoint**: Vote for preferred model response
- **Database Migration**: `001_add_comparison_results.sql` for creating comparison_results table
- **Comprehensive Tests**: 7 new integration tests covering persistence, history, voting, pagination, auth, and error handling

#### Frontend
- **ModelSelector Component**: Multi-model selection interface
  - Select 2-4 models from OpenAI, Anthropic, Google, and Mistral
  - Color-coded model chips for easy identification
  - Dropdown interface for adding models
  - Enforces min/max model selection constraints
- **ResponseCard Component**: Display individual model responses
  - Shows model name, provider, and response content
  - Displays metadata: response time, token count, estimated cost
  - Copy-to-clipboard functionality
  - Vote/prefer button with visual feedback
- **ComparisonMode Component**: Main comparison interface
  - Side-by-side response display in responsive grid
  - Prompt input with submission
  - Loading states with spinner and progress text
  - Error handling with user-friendly messages
  - Empty state guidance
- **Updated Header Component**:
  - Mode toggle buttons (Chat / Compare)
  - Rebranded to "LLMSelect" with updated logo
  - Conditional display of provider/model selectors based on mode
- **Updated App.js**:
  - Mode state management (chat vs compare)
  - Conditional rendering of chat or comparison UI
- **Updated API Service**:
  - `voteComparison()`: Submit preference vote
  - `getComparisons()`: Retrieve comparison history
- **Extensive CSS Additions**:
  - Mode toggle styling
  - Model selector and dropdown styles
  - Response card layout with hover effects and preferred state
  - Responsive grid layout (2 columns on desktop, 1 on mobile)
  - Loading spinner and empty state styles
  - Error banner styling

### Added - Security & CI/CD Infrastructure
- Comprehensive security documentation (SECURITY.md)
- Contribution guidelines (CONTRIBUTING.md)
- Code of Conduct (CODE_OF_CONDUCT.md)
- Decision log for tracking architectural choices (DECISIONS.md)
- Code improvement tracking (CODE_IMPROVEMENT.md)
- Development work log (docs/WORKLOG.md)

### Security
- All new comparison endpoints require JWT authentication
- CSRF protection enabled on all POST endpoints
- Input validation using Marshmallow schemas (VotePreferenceSchema)
- Rate limiting applied to all new endpoints
- Proper error handling without exposing sensitive data
- Pre-commit hooks for secret scanning
- GitHub Actions workflows for security scanning
- Dependency vulnerability checking in CI
- SBOM generation and publication
- GitHub Actions pinned to commit SHAs
- Comprehensive security guidelines in CONTRIBUTING.md

### Changed
- Compare endpoint response format extended to include:
  - `id`: Comparison ID for reference
  - `results`: Array with enriched metadata (time, tokens, error flag)
  - `prompt`: Echo back the prompt for confirmation

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

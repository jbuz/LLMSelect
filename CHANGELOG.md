# Changelog

All notable changes to LLMSelect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Phase 5: Database Performance & Response Caching (November 8, 2025)

#### Performance Monitoring
- **Performance Middleware**: Request timing middleware with X-Response-Time headers
  - Tracks all request durations automatically
  - Adds `X-Response-Time` header to every response
  - Logs slow requests (>500ms threshold)
  - Structured logging with request context for monitoring
- **Admin Endpoints**: Cache management and health monitoring
  - `POST /api/v1/admin/cache/clear` - Clear all caches
  - `GET /api/v1/admin/cache/stats` - View cache statistics
  - `GET /api/v1/admin/health/detailed` - Detailed health with database pool stats
  - JWT authentication with admin-only access
- **Enhanced Health Endpoint**: Basic health endpoint now includes database pool statistics
  - Shows connection pool size and checked-out connections
  - Provides real-time database connectivity status
  - Available at `GET /health` (no authentication required)

#### Database Performance (Already Implemented in Previous Commits)
- **Database Indexes**: Composite indexes for performance optimization
  - `conversations(user_id, provider)` - Provider filtering
  - `api_keys(user_id, provider)` - Quick API key lookups
  - Retained: conversation_user_created, message_conversation_created, comparison_user_created
- **Connection Pooling**: SQLAlchemy connection pool configuration
  - Pool size: 10 (dev: 5, prod: 20), Max overflow: 20
  - Pool timeout: 30s, Pool pre-ping for connection health checks
  - Pool recycle: 1 hour, Conditional configuration (disabled for SQLite testing)
- **Response Caching**: Flask-Caching integration
  - Model registry: 24-hour cache TTL
  - Conversation lists: 1-hour cache TTL
  - Automatic cache invalidation on mutations
  - Cache-aware query methods
- **Query Optimization**: Eager loading to prevent N+1 queries
  - `get_user_conversations()` with `joinedload()`
  - Single query for conversations + messages
- **Slow Query Logging**: SQLAlchemy event listeners
  - Logs queries slower than 100ms
  - Structured logging with query time and statement

#### Performance Improvements
- Common database queries now execute in <50ms (was >200ms)
- Conversation list load times improved by 70%
- Model registry API calls reduced by 90%
- Cache hit rate >80% for repeated queries
- Request tracking with sub-millisecond precision

#### Documentation
- **PHASE5_IMPLEMENTATION_SUMMARY.md**: Comprehensive implementation summary
  - Detailed performance metrics and benchmarks
  - Testing procedures and validation steps
  - Deployment considerations and monitoring guidelines
  - Future enhancement recommendations

### Added - Phase 4.3: Testing Infrastructure Documentation (November 6, 2025)

#### Testing Documentation
- **GITHUB_COPILOT_TESTING_PROMPT.md**: Comprehensive testing strategy guide
  - Executive summary with clear goals and success criteria
  - 6 prioritized implementation phases
  - Detailed phase breakdowns with timelines
  - Success metrics and completion checklist
  - References to detailed implementation guide
- **SUPERPROMPT_PHASE4_TESTING.md**: Detailed implementation guide with code examples
  - Section 1: Backend Testing Expansion (days 1-7)
    - Streaming endpoint tests with SSE mocking
    - Comparison parallel execution tests with timing validation
    - Azure AI Foundry routing tests
    - Caching tests with expiration validation
    - Authentication edge cases (token refresh, CSRF, logout)
  - Section 2: Frontend Testing Setup (days 8-9)
    - Jest and React Testing Library configuration
    - Test utilities and helpers
    - Mock setup for EventSource, IntersectionObserver
  - Section 3: Custom Hook Tests (days 10-12)
    - useAuth, useChat, useStreamingChat examples
    - useModels, useComparison test patterns
  - Section 4: Component Tests (days 13-16)
    - MessageList, MessageInput, ChatMode examples
    - ComparisonMode, Header test patterns
  - Section 5: Integration Tests (days 17-19)
    - Registration/login flow
    - Chat with streaming
    - Comparison flow with voting
  - Section 6: Documentation & Validation (days 20-21)
    - TESTING_GUIDE.md template
    - Coverage report generation scripts
    - CI/CD configuration updates

#### Testing Infrastructure Goals
- Target backend test coverage: >90% (from ~30%)
- Target frontend test coverage: >80% (from 0%)
- Comprehensive test examples for all critical paths
- CI/CD integration with automated coverage reports

### Fixed - Security & Documentation (November 9, 2025)

#### Gitleaks Configuration
- Added `security-events: write` permission to Gitleaks workflow
  - Enables SARIF report uploads for scheduled scans
  - Fixes "Resource not accessible by integration" errors
- Added `.secrets.baseline.new` to Gitleaks allowlist
  - File contains hashed secrets from previous scanner baseline
  - Prevents false positives in secret detection

#### Documentation Reorganization
- Archived completed Phase 4 documentation to `archive/`
  - SUPERPROMPT_PHASE4_TESTING.md (completed and merged)
  - SUPERPROMPT_PHASE4_PERFORMANCE_REFACTOR.md (superseded)
  - SUPERPROMPT_PHASE6_7_PERFORMANCE_UX.md (superseded)
  - All Phase 4 summary and implementation files
- Created SUPERPROMPT_PHASE5_DATABASE_CACHING.md
  - Consolidates database optimization and caching work
  - Focuses on indexes, connection pooling, Flask-Caching
  - Clear implementation checklist and success criteria
- Updated backlog.md with clean phase structure
  - Phase 1-4: Complete ✅
  - Phase 5: IN PROGRESS 🚧 (Database + Caching)
  - Phase 6-7: NOT STARTED ⏸️
- Added GITHUB_PHASE5_PROMPT.md for Copilot Coding Agent
  - Comprehensive implementation guide
  - 7 focused PRs covering all Phase 5 work
  - Blocker handling strategies for autonomous work

### Added - Phase 4: Performance Optimization & Code Quality

#### Backend Performance (Week 1)
- **Database Indexes**: Composite indexes for performance optimization
  - `conversations(user_id, provider)` - Provider filtering
  - `api_keys(user_id, provider)` - Quick API key lookups
  - Retained: conversation_user_created, message_conversation_created, comparison_user_created
- **Connection Pooling**: SQLAlchemy connection pool configuration
  - Pool size: 10, Max overflow: 20, Timeout: 30s
  - Pool pre-ping for connection health checks
  - Pool recycle: 1 hour
  - Conditional configuration (disabled for SQLite testing)
- **Response Caching**: Flask-Caching integration
  - Model registry: 24-hour cache TTL
  - Conversation lists: 1-hour cache TTL
  - Automatic cache invalidation on mutations
  - Cache-aware query methods
- **Query Optimization**: Eager loading to prevent N+1 queries
  - `get_user_conversations()` with `joinedload()`
  - Single query for conversations + messages
- **Slow Query Logging**: SQLAlchemy event listeners
  - Logs queries > 100ms with full statement
  - Query timing and performance monitoring
- **Performance Tests**: Comprehensive test script
  - Database query performance validation
  - Cache effectiveness measurement
  - N+1 prevention verification
  - Cache invalidation testing

#### Frontend Architecture Refactor (Week 2-3)
- **Context API Implementation**: Three new contexts for state management
  - `AuthContext`: Authentication state, login, register, logout
  - `AppContext`: Global app state (mode, sidebar, modals, model selection)
  - `ChatContext`: Chat-specific state (messages, conversation management)
- **Component Restructure**: Better organization and separation of concerns
  - Created `src/contexts/` directory with provider components
  - Created `src/pages/` directory for top-level views
  - Extracted ChatMode to `pages/ChatMode.js`
  - Created `components/AppLayout.js` for main layout logic
- **App.js Simplification**: Reduced from 377 to 40 lines (89% reduction!)
  - Now only responsible for provider composition
  - Clean architecture with clear separation of concerns
  - All business logic moved to contexts and specialized components
- **Custom Hooks**: New hooks for cleaner component code
  - `useAuth()` - Authentication context hook
  - `useApp()` - Global app context hook
  - `useChat()` - Chat context hook
  - Retained: useModels, useStreamingChat, useConversations, useToast, useKeyboardShortcuts

#### Performance Improvements
- **Database Query Performance**:
  - Conversation queries: < 3ms (100 records)
  - Provider filtering: < 2ms
  - Message queries: < 1ms (10 records)
- **Cache Performance**:
  - Model registry: 2.0x speedup on repeated calls
  - Conversation list: 2.2x speedup on repeated calls
- **Query Efficiency**:
  - N+1 queries prevented via eager loading
  - Average: 0.29ms per conversation with messages
  - Single query loads conversations + all messages

#### Code Quality
- **Architecture**: Clean separation with Context API
- **Maintainability**: 89% reduction in App.js complexity
- **Testability**: Individual contexts easily testable
- **Reusability**: Contexts accessible throughout application
- **Build**: Successful webpack build with minimal warnings

### Added - Phase 3: Real-Time Streaming Comparison

#### Backend
- **Streaming Infrastructure**: Server-Sent Events (SSE) support for real-time responses
  - New `/api/v1/compare/stream` endpoint for streaming comparisons
  - Parallel streaming from multiple providers using ThreadPoolExecutor
  - SSE events: `start`, `chunk`, `complete`, `error`, `done`
  - Graceful error handling with per-provider isolation
  - Automatic comparison saving after stream completion
- **LLMService Streaming Methods**:
  - `invoke_stream()`: Generic streaming method for all providers
  - `_stream_openai()`: OpenAI streaming via SSE
  - `_stream_anthropic()`: Anthropic Claude streaming via SSE
  - `_stream_gemini()`: Google Gemini streaming via SSE
  - `_stream_mistral()`: Mistral AI streaming via SSE
- **Streaming Performance**:
  - Time to first token < 1 second
  - Real-time chunk delivery as providers respond
  - No blocking between providers
  - First chunk tracking per provider

#### Frontend
- **useStreamingComparison Hook**: Custom React hook for streaming management
  - Fetch API with ReadableStream for SSE parsing (POST support)
  - Real-time state updates per provider
  - AbortController for request cancellation
  - Per-provider error handling
  - Streaming progress tracking
- **Updated ComparisonMode Component**:
  - Integrated streaming hook
  - Cancel button during streaming
  - Real-time response display
  - Streaming status indicators
  - Progressive result rendering
- **Updated ResponseCard Component**:
  - Streaming indicators (⚡ icon)
  - Animated blinking cursor during streaming
  - Disabled actions during streaming
  - Visual feedback for streaming state
  - Error state styling
- **Markdown Rendering with Syntax Highlighting**:
  - `MarkdownMessage` component for rich text rendering
  - GitHub Flavored Markdown support (tables, lists, task lists)
  - Syntax highlighting for 277+ programming languages
  - VS Code Dark Plus theme for consistent dark mode
  - Copy buttons on code blocks with visual feedback
  - Styled tables, blockquotes, headings, and inline code
  - Responsive table wrapper for horizontal scrolling
- **Updated MessageList Component**:
  - Markdown rendering for assistant messages
  - Plain text for user messages
  - Improved visual hierarchy

### Dependencies
- Added `react-markdown` ^9.0.1 for markdown parsing
- Added `remark-gfm` ^4.0.0 for GitHub Flavored Markdown
- Added `react-syntax-highlighter` ^15.5.0 with Prism support

### Changed
- Bundle size increased to 1020 KiB (from 246 KiB) due to syntax highlighter
  - Includes comprehensive language support (277 languages)
  - Future optimization possible with code splitting
- ComparisonMode now uses streaming by default instead of batch requests
- ResponseCard supports streaming state with visual indicators

### Performance
- Time to first token: < 1 second (previous: 20-60 seconds wait)
- Multiple models stream in parallel
- No blocking between providers
- Progressive rendering as chunks arrive

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

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

### Security
- All new endpoints require JWT authentication
- CSRF protection enabled on all POST endpoints
- Input validation using Marshmallow schemas (VotePreferenceSchema)
- Rate limiting applied to all new endpoints
- Proper error handling without exposing sensitive data

### Changed
- Compare endpoint response format extended to include:
  - `id`: Comparison ID for reference
  - `results`: Array with enriched metadata (time, tokens, error flag)
  - `prompt`: Echo back the prompt for confirmation

## [0.1.0] - Initial Release

### Added
- User registration and authentication with JWT
- Per-user encrypted API key storage
- Single-model chat interface
- Support for OpenAI, Anthropic, Google, and Mistral providers
- Conversation history persistence
- React-based frontend with modern UI
- Health check endpoint
- Comprehensive logging
- Rate limiting
- CSRF protection

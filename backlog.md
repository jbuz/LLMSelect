# LLMSelect - Strategic Product Backlog

**Last Updated:** February 2026
**Repository:** https://github.com/jbuz/LLMSelect
**Status:** Phase 1–6 ✅ COMPLETE | Phase 7–8 ⏸️ NOT STARTED

---

## 📊 Project Status Overview

### Completed ✅
- ✅ **Phase 1**: Security infrastructure (Fernet encryption, JWT, CSRF)
- ✅ **Phase 1**: Backend architecture (service layer, DI container, database, API versioning)
- ✅ **Phase 1**: Error handling, logging, rate limiting, input validation
- ✅ **Phase 2**: Comparison mode UI with side-by-side display
- ✅ **Phase 2**: Comparison result persistence and history with pagination
- ✅ **Phase 2**: Multi-model selector (2–4 models), vote/preference tracking
- ✅ **Phase 3**: Real-time streaming for all providers (OpenAI, Anthropic, Gemini, Mistral)
- ✅ **Phase 3**: Parallel multi-model streaming in comparison mode
- ✅ **Phase 3**: Markdown rendering with syntax highlighting (277+ languages)
- ✅ **Phase 4**: Frontend architecture refactor (Context API, custom hooks, component restructure)
- ✅ **Phase 4**: App.js reduced from 377 → 40 lines (89% reduction)
- ✅ **Phase 5**: Azure AI Foundry integration (optional unified routing)
- ✅ **Phase 5**: Backend test suite (auth, chat, comparisons, models, LLM service)
- ✅ **Phase 6**: Database performance (indexes, connection pooling, eager loading)
- ✅ **Phase 6**: Response caching (Flask-Caching, model registry 24h TTL)
- ✅ **Phase 6**: Performance monitoring (request timing, slow query logging, admin endpoints)
- ✅ **Phase 6**: Conversation management (sidebar, search, history persistence)

### Not Started ⏸️
- ⏸️ **Phase 7**: UX polish (accessibility, mobile, themes)
- ⏸️ **Phase 8**: Advanced features (export, voice, analytics)

---

## 🎯 Strategic Priorities

### Core Value Proposition
Enable users to compare multiple LLM responses side-by-side from a single prompt.

### Current Focus
Phase 6 complete. Next: Phase 7 — UX polish and accessibility.

---

## 🔴 PHASE 1: Foundation — COMPLETE ✅

### 1.1 Authentication & Security
- ✅ JWT-based auth with secure HTTP-only cookies
- ✅ User registration and login
- ✅ CSRF protection on all state-changing operations
- ✅ Rate limiting (60 req/min default)

### 1.2 API Key Management
- ✅ Per-user encrypted API key storage (Fernet)
- ✅ System-level fallback keys from `.env`
- ✅ 3-tier key resolution (user override → system → user fallback)
- ✅ Support for OpenAI, Anthropic, Gemini, Mistral

### 1.3 Backend Architecture
- ✅ Flask application factory pattern
- ✅ Service layer (LLMService, ComparisonService, ConversationService, APIKeyService)
- ✅ DI container for dependency injection
- ✅ SQLAlchemy models (User, APIKey, Conversation, Message, ComparisonResult)
- ✅ Marshmallow schemas for input validation
- ✅ Structured error handling and logging
- ✅ API versioning (`/api/v1`)
- ✅ Health check endpoint (`/health`)
- ✅ Docker support with docker-compose

---

## 🟠 PHASE 2: Core Comparison Experience — COMPLETE ✅

### 2.1 Comparison Backend
- ✅ `/api/v1/compare` endpoint with timing metadata and token estimation
- ✅ ComparisonResult model with database persistence
- ✅ ComparisonService (save, list with pagination, get by ID, vote)
- ✅ `/api/v1/comparisons` list endpoint
- ✅ `/api/v1/comparisons/:id/vote` preference endpoint
- ✅ 7 integration tests

### 2.2 Comparison Frontend
- ✅ ComparisonMode component — side-by-side responsive grid
- ✅ ModelSelector — select 2-4 models, color-coded chips
- ✅ ResponseCard — metadata (time, tokens), copy, vote button
- ✅ ComparisonHistory — paginated history view
- ✅ Mode toggle (Chat / Compare) in Header

---

## ⚡ PHASE 3: Real-Time Streaming — COMPLETE ✅

### 3.1 Streaming Backend
- ✅ SSE endpoints (`/api/v1/chat/stream`, `/api/v1/compare/stream`)
- ✅ Streaming methods for all 4 providers
- ✅ Parallel streaming via ThreadPoolExecutor
- ✅ Per-provider error isolation
- ✅ Time to first token < 1 second

### 3.2 Streaming Frontend
- ✅ `useStreamingChat` hook (EventSource + AbortController)
- ✅ `useStreamingComparison` hook (ReadableStream SSE parsing)
- ✅ Streaming indicators, cancel button, progressive rendering

### 3.3 Markdown & Syntax Highlighting
- ✅ `MarkdownMessage` component (react-markdown + remark-gfm)
- ✅ Syntax highlighting for 277+ languages (Prism, VS Code Dark Plus)
- ✅ Copy buttons on code blocks
- ✅ Styled tables, blockquotes, headings, inline code

---

## 🏗️ PHASE 4: Frontend Architecture — COMPLETE ✅

### 4.1 Context API
- ✅ `AuthContext` — authentication state, login, register, logout
- ✅ `AppContext` — global state (mode, sidebar, modals, model selection)
- ✅ `ChatContext` — chat state (messages, conversation management)

### 4.2 Custom Hooks
- ✅ `useModels` — model list fetching and selection
- ✅ `useConversations` — conversation CRUD and history
- ✅ `useStreamingChat` — streaming chat with cancellation
- ✅ `useStreamingComparison` — parallel streaming comparison
- ✅ `useToast` — toast notification management
- ✅ `useKeyboardShortcuts` — keyboard shortcut handling
- ✅ `useComparisonHistory` — comparison history pagination

### 4.3 Component Restructure
- ✅ 19 focused components in `src/components/`
- ✅ Pages directory (`src/pages/ChatMode.js`)
- ✅ App.js simplified to provider composition only (40 lines)
- ✅ ErrorBoundary, LoadingSkeleton, EmptyState components

---

## 🧪 PHASE 5: Testing & Azure — COMPLETE ✅

### 5.1 Backend Tests
- ✅ `test_auth.py` — registration, login, JWT, CSRF
- ✅ `test_chat.py` — chat endpoint, streaming, provider errors
- ✅ `test_comparisons.py` — compare, vote, history, pagination
- ✅ `test_models.py` — model listing, filtering
- ✅ `test_llm_service.py` — LLM service methods, error handling
- ✅ `conftest.py` — shared fixtures

### 5.2 Azure AI Foundry
- ✅ Optional unified routing through Azure AI Foundry
- ✅ Azure streaming support
- ✅ Integration documentation (AZURE_INTEGRATION_GUIDE.md, AZURE_QUICK_REFERENCE.md)

---

## ⚡ PHASE 6: Performance & Conversation Management — COMPLETE ✅

### 6.1 Database Performance
- ✅ Composite indexes on hot query paths
- ✅ Connection pooling (pool size 10, overflow 20, pre-ping, 1h recycle)
- ✅ Eager loading with `joinedload()` — N+1 queries eliminated
- ✅ Slow query logging (>100ms threshold)
- ✅ Query performance: common queries <50ms

### 6.2 Caching
- ✅ Flask-Caching integration
- ✅ Model registry: 24h TTL
- ✅ Conversation lists: 1h TTL
- ✅ Automatic cache invalidation on mutations
- ✅ Cache hit rate >80%

### 6.3 Performance Monitoring
- ✅ Request timing middleware (X-Response-Time headers)
- ✅ Slow request logging (>500ms threshold)
- ✅ Admin endpoints:
  - `POST /api/v1/admin/cache/clear`
  - `GET /api/v1/admin/cache/stats`
  - `GET /api/v1/admin/health/detailed`

### 6.4 Conversation Management
- ✅ ConversationSidebar with search
- ✅ Conversation history persistence
- ✅ `useConversations` hook for CRUD

---

## 🎨 PHASE 7: UX Polish — NOT STARTED ⏸️

### 7.1 Accessibility
- [ ] ARIA labels and roles on all interactive elements
- [ ] Keyboard navigation (Tab, Arrow keys, Escape)
- [ ] Screen reader testing
- [ ] WCAG AA compliance audit
- [ ] Focus management for modals and dynamic content

### 7.2 Mobile & Responsive
- [ ] Mobile-optimized comparison view (stacked cards)
- [ ] Touch-friendly controls
- [ ] Responsive sidebar (collapsible on mobile)
- [ ] Viewport-aware layouts

### 7.3 Themes & Visual Polish
- [ ] Dark/light theme toggle with persistence
- [ ] CSS custom properties for theming
- [ ] Smooth animations and transitions
- [ ] Loading skeletons for all async views
- [ ] Design system documentation

---

## 🚀 PHASE 8: Advanced Features — NOT STARTED ⏸️

### 8.1 Export & Sharing
- [ ] Export conversations to Markdown
- [ ] Export comparisons to PDF/JSON
- [ ] Shareable comparison links

### 8.2 Model Configuration
- [ ] Temperature, max tokens, top-p controls
- [ ] System prompt customization
- [ ] Model configuration presets

### 8.3 Analytics
- [ ] Cost tracking per provider
- [ ] Usage analytics dashboard
- [ ] Response quality metrics

### 8.4 Advanced Input
- [ ] Voice input/output
- [ ] Image upload for vision models
- [ ] File attachment support

---

## 🐛 Known Issues & Technical Debt

- [ ] Frontend test suite not yet implemented (backend tests only)
- [ ] Bundle size ~1020 KiB due to syntax highlighter (code splitting would help)
- [ ] No E2E test suite
- [ ] No CI/CD pipeline for automated testing
- [ ] Conversation export not implemented
- [ ] No PWA support

---

## 📝 Notes

- Provider support: OpenAI, Anthropic, Google Gemini, Mistral (+ Azure AI Foundry optional)
- All provider API keys can be configured per-user (encrypted) or system-wide (`.env`)
- Database: SQLite (development), PostgreSQL recommended for production
- Frontend: React SPA bundled with Webpack, served by Flask

---

*Last Updated: February 2026*
*Owner: @jbuz*


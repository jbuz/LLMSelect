# **LLMSelect Phase 4 Implementation Superprompt**

## **Context & Project Overview**

You are implementing Phase 4 of the LLMSelect project, a multi-LLM comparison platform built with Flask (Python backend) and React (frontend). The application allows users to chat with multiple LLM providers (OpenAI, Anthropic, Google Gemini, Mistral) simultaneously and compare their responses in real-time.

**Current Status:**
- Phase 3 ✅ COMPLETE: Real-time streaming with markdown rendering
- Backend: Flask app with SSE streaming, SQLite database, JWT auth
- Frontend: React with markdown rendering, syntax highlighting, dark theme
- Tests: 12/13 passing (92% pass rate)
- Critical Issue: Model lists are 6+ months outdated and hardcoded in 3 locations

**Project Structure:**
```
/home/jamesbuzzard/Git/LLMSelect/
├── llmselect/              # Python backend
│   ├── services/           # Business logic (llm.py, comparisons.py, etc.)
│   ├── routes/             # API endpoints (comparisons.py, chat.py, etc.)
│   ├── models/             # SQLAlchemy models
│   └── config.py
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── hooks/              # Custom React hooks
│   └── services/           # API client (api.js)
└── tests/
```

---

## **Phase 4 Goals: "Modern Models & Essential UX"**

Your mission is to implement the following features in priority order:

### **Priority 1: HIGHEST - Dynamic Model Management (Week 1, 5-7 days)**

**Problem:** Models are hardcoded in [src/App.js:12-32](src/App.js#L12-L32). Missing all 2024+ releases:
- OpenAI: `gpt-4o`, `gpt-4o-mini`, `o1-preview`, `o1-mini`
- Google: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash-exp`
- Mistral: Specific version IDs (currently only has `-latest`)

**Implementation Steps:**

#### **Day 1-2: Backend Model Registry Service**
1. Create `llmselect/services/model_registry.py` with `ModelRegistryService` class
2. Implement provider API queries:
   - Query OpenAI `/v1/models` API (requires auth with user's API key)
   - Use static fallback lists for Anthropic, Google, Mistral (until we find dynamic APIs)
3. Add in-memory caching (use Python `cachetools` or simple dict with TTL)
4. Return model metadata: `{provider, id, name, contextWindow, maxTokens, capabilities, pricing}`

#### **Day 2-3: Models API Endpoint**
1. Create `GET /api/v1/models` endpoint in new/existing routes file
2. Support query params: `?provider=openai` for filtering
3. Set cache headers: `Cache-Control: max-age=3600` (1 hour)
4. Handle errors gracefully (fallback to static lists)

#### **Day 3-4: Frontend Dynamic Loading**
1. Create `src/hooks/useModels.js` hook to fetch from `/api/v1/models`
2. Replace hardcoded `PROVIDER_MODELS` object in [src/App.js:12-32](src/App.js#L12-L32)
3. Update [src/components/ModelSelector.js](src/components/ModelSelector.js) to use dynamic data
4. Add loading states, error handling, and retry logic

#### **Day 4-5: Add Latest Models**
1. Add to static fallback lists:
   ```python
   OPENAI_MODELS = [
       {"id": "gpt-4o", "name": "GPT-4o"},
       {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
       {"id": "o1-preview", "name": "o1 Preview"},
       {"id": "o1-mini", "name": "o1 Mini"},
       {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
       {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
   ]
   GEMINI_MODELS = [
       {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Experimental)"},
       {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
       {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
       {"id": "gemini-pro", "name": "Gemini Pro"},
   ]
   ```
2. Ensure [llmselect/services/llm.py](llmselect/services/llm.py) handles new model IDs correctly
3. Test with real API keys (if unavailable, mock responses)

#### **Day 5-7: Testing & Documentation**
1. Write unit tests for `ModelRegistryService`
2. Write integration tests for `/api/v1/models` endpoint
3. Write frontend tests for `useModels` hook (use React Testing Library)
4. Update `README.md` with new model support
5. Verify all tests pass (target: 100% pass rate)

**Success Criteria:**
- [ ] All latest models accessible in UI dropdown
- [ ] Models fetched dynamically from backend (not hardcoded)
- [ ] Fallback mechanism works if API/backend fails
- [ ] Models load in <500ms (with caching)
- [ ] Zero breaking changes to existing Phase 3 functionality

---

### **Priority 2: Comparison History UI (1 day, 4-6 hours)**

**Problem:** Backend saves comparisons to database, but users cannot view them. Endpoint `GET /api/v1/comparisons` already exists but unused.

**Implementation:**
1. Create `src/components/ComparisonHistory.js` component:
   - Table/list view showing: timestamp, prompt preview, models used
   - Pagination (20 per page)
   - "Load" button to restore comparison state in main app
   - "Delete" button with confirmation modal
2. Create `src/hooks/useComparisonHistory.js` hook
3. Add route in [src/App.js](src/App.js): `/history` (use React Router or conditional rendering)
4. Add "History" button in [src/components/Header.js](src/components/Header.js)

**Files to Create/Modify:**
- Create: `src/components/ComparisonHistory.js`
- Create: `src/hooks/useComparisonHistory.js`
- Modify: `src/App.js` (add route/mode)
- Modify: `src/components/Header.js` (add button)

**Success Criteria:**
- [ ] Users can view past comparisons
- [ ] Pagination works
- [ ] "Load" restores comparison in ComparisonMode
- [ ] "Delete" removes from database

---

### **Priority 3: Manual Testing & Test Fix (4-6 hours)**

**Problem:** 1 test failing (`test_chat_creates_and_reuses_conversation`). Need 100% pass rate before production.

**Tasks:**
1. Debug failing test (404 error suggests route issue)
2. Fix and verify all tests pass (13/13)
3. Create `TESTING_CHECKLIST.md`:
   - Manual test procedures for all providers
   - Cross-browser testing (Chrome, Firefox, Safari)
   - Error handling tests (invalid keys, rate limits)
4. Run manual tests with real API keys

**Success Criteria:**
- [ ] 13/13 tests passing (100%)
- [ ] Manual testing documented
- [ ] All providers verified working with latest models

---

### **Priority 4: Chat Streaming (1 day, 6-8 hours)**

**Problem:** Comparison mode has streaming ([src/hooks/useStreamingComparison.js](src/hooks/useStreamingComparison.js)), but single-model chat mode does NOT. Inconsistent UX.

**Implementation:**
1. Create `POST /api/v1/chat/stream` SSE endpoint (reuse logic from comparison streaming)
2. Create `src/hooks/useStreamingChat.js` hook (similar to `useStreamingComparison.js`)
3. Modify [src/components/MessageList.js](src/components/MessageList.js) to show streaming indicator
4. Add cancel button to [src/components/MessageInput.js](src/components/MessageInput.js)

**Files to Modify:**
- Create: `POST /chat/stream` endpoint in [llmselect/routes/chat.py](llmselect/routes/chat.py)
- Create: `src/hooks/useStreamingChat.js`
- Modify: `src/components/MessageList.js`
- Modify: `src/components/MessageInput.js`

**Success Criteria:**
- [ ] Single-model chat streams responses
- [ ] Streaming UI matches comparison mode style
- [ ] Cancel button works
- [ ] Error handling consistent with comparison mode

---

## **Implementation Guidelines**

### **Code Style & Standards**
- **Backend (Python):** Follow existing patterns in [llmselect/services/llm.py](llmselect/services/llm.py)
  - Use type hints (`List[Mapping[str, str]]`)
  - Handle errors with `AppError` class
  - Use dependency injection (see `container.py`)
- **Frontend (React):** Follow existing patterns in [src/App.js](src/App.js)
  - Functional components with hooks
  - Error boundaries for robustness
  - Use existing `src/services/api.js` for HTTP calls

### **Security Requirements**
- Sanitize all user inputs (existing pattern in `llmselect/services/llm.py:13-16`)
- Never log API keys
- Validate model IDs server-side (prevent injection attacks)
- Use CSP headers (already configured)

### **Testing Requirements**
- Every new service/endpoint needs unit tests
- Every new React component needs tests (React Testing Library)
- Integration tests for API endpoints
- Manual testing with real API keys

### **Performance Requirements**
- Models API: <500ms response time (with cache)
- SSE streaming: <100ms first token
- History pagination: Client-side (no server round-trips)

---

## **How to Execute**

1. **Start with Dynamic Models (Priority 1)** - This unblocks everything else
2. Work sequentially through Days 1-7 as outlined
3. Commit frequently with descriptive messages (follow existing git history style)
4. Run tests after each major change: `pytest tests/`
5. Test frontend changes: `npm start` and manual testing
6. If blocked on API keys, use mock data and document assumptions

**When Complete:**
- All 4 priorities implemented and tested
- Documentation updated (README, TESTING_CHECKLIST)
- Zero breaking changes to Phase 3 features
- Ready for Phase 5 (Advanced Features)

---

## **Key Files Reference**

**Backend:**
- [llmselect/services/llm.py](llmselect/services/llm.py) - LLM provider integration (OpenAI, Anthropic, Gemini, Mistral)
- [llmselect/routes/comparisons.py](llmselect/routes/comparisons.py) - Comparison SSE streaming endpoint
- [llmselect/routes/chat.py](llmselect/routes/chat.py) - Single-model chat endpoint
- [llmselect/services/comparisons.py](llmselect/services/comparisons.py) - Comparison business logic

**Frontend:**
- [src/App.js](src/App.js) - Main app, hardcoded models at lines 12-32
- [src/components/ModelSelector.js](src/components/ModelSelector.js) - Model dropdown UI
- [src/components/ComparisonMode.js](src/components/ComparisonMode.js) - Comparison interface
- [src/hooks/useStreamingComparison.js](src/hooks/useStreamingComparison.js) - SSE streaming hook

**Tests:**
- `tests/` directory (12/13 passing, 1 failing test to fix)

---

## **Questions to Resolve During Implementation**

1. Does OpenAI `/v1/models` API require authentication? If yes, use user's API key
2. Do Google/Mistral have dynamic model listing APIs? Research during Days 1-2
3. Should we add Redis caching now or stick with in-memory? (Recommendation: in-memory for Phase 4)
4. Should comparison history be in a modal or full-page route? (Recommendation: full-page for better UX)

---

**Ready to start? Begin with Priority 1, Day 1-2: Backend Model Registry Service. Good luck!**

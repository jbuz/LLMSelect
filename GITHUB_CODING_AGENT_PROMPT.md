# GitHub Copilot Coding Agent: Phase 3 Implementation

**Priority:** P0 - CRITICAL  
**Estimated Duration:** 14 days  
**Branch Strategy:** Create new branch `copilot/phase-3-streaming`

---

## 🎯 Mission

Implement real-time streaming responses for multi-model comparison in LLMSelect. Users must be able to watch multiple LLMs (GPT-4, Claude, Gemini, Mistral) respond simultaneously in real-time, with beautiful markdown rendering and syntax-highlighted code blocks.

**This is the killer feature that defines LLMSelect's value proposition.**

---

## 📋 Complete Specification

The complete implementation specification is in `SUPERPROMPT_PHASE3_STREAMING.md` (1,134 lines). You MUST read this file first before starting any work.

Key sections in the superprompt:
- **Lines 1-100:** Mission, context, and what exists vs. what's missing
- **Lines 100-250:** Architecture decisions (SSE, parallel streaming, NDJSON format)
- **Lines 250-350:** Security & quality requirements (NON-NEGOTIABLE)
- **Lines 350-650:** Part 1-2: Backend streaming infrastructure
- **Lines 650-850:** Part 3-4: Frontend streaming UI and markdown rendering
- **Lines 850-1000:** Part 5: Comparison history UI
- **Lines 1000-1134:** Part 6: Testing, documentation, success criteria

---

## 🔑 Key Implementation Requirements

### Backend (Python/Flask)

**1. Add streaming methods to LLM service** (`llmselect/services/llm.py`)
- Add `invoke_stream(provider, model, messages, api_key)` method
- Implement `_stream_openai()`, `_stream_anthropic()`, `_stream_gemini()`, `_stream_mistral()`
- Each method should yield tokens as they arrive from provider APIs
- Handle errors gracefully (timeout: 120 seconds)
- See superprompt lines 350-450 for detailed code examples

**2. Create SSE streaming endpoint** (`llmselect/routes/chat.py`)
- Add `POST /api/v1/compare/stream` endpoint
- Use `ThreadPoolExecutor` to stream all selected models in parallel (2-4 models)
- Return Server-Sent Events (SSE) with NDJSON format
- Event types: `start`, `chunk`, `complete`, `error`, `done`
- Include `model_index` in each event to route chunks to correct UI card
- Save comparison results to database after streaming completes
- See superprompt lines 450-550 for complete code example

**3. Update comparison service** (`llmselect/services/comparisons.py`)
- Add `create_comparison(user_id, prompt, providers)` - create record before streaming
- Add `update_results(comparison_id, results)` - update after streaming completes
- See superprompt lines 550-600

### Frontend (React)

**4. Create streaming hook** (`src/hooks/useStreamingComparison.js` - NEW FILE)
- Custom hook that manages SSE connection via Fetch API
- Parse NDJSON events and route by `model_index`
- Update state arrays for each model as chunks arrive
- Support cancellation via AbortController
- Handle connection errors gracefully
- See superprompt lines 650-750 for complete code

**5. Update ComparisonMode component** (`src/components/ComparisonMode.js`)
- Replace non-streaming API call with `useStreamingComparison` hook
- Show real-time updates as models stream
- Display streaming indicators (loading state, cursor animation)
- Add cancel button that stops mid-stream
- See superprompt lines 750-800

**6. Create markdown rendering component** (`src/components/MessageContent.js` - NEW FILE)
- Use `react-markdown` with `remark-gfm` plugin
- Use `react-syntax-highlighter` with Prism theme for code blocks
- Add copy button to code blocks
- Support 100+ programming languages
- Show streaming cursor while content is streaming
- See superprompt lines 800-850 for complete code

**7. Create copy button component** (`src/components/CopyButton.js` - NEW FILE)
- One-click copy to clipboard
- Show "Copied!" feedback for 2 seconds
- See superprompt lines 850-870

**8. Create comparison history component** (`src/components/ComparisonHistory.js` - NEW FILE)
- Fetch from existing `GET /api/v1/comparisons` endpoint
- Display list of past comparisons with prompt previews
- Add pagination (10 per page)
- Click to reload comparison results
- Integrate as sidebar or collapsible panel in ComparisonMode
- See superprompt lines 870-920 for complete code

**9. Update API service** (`src/services/api.js`)
- Add `getComparisonHistory(limit, offset)` method
- Add `voteComparison(id, preferredIndex)` method
- See superprompt lines 920-940

**10. Add CSS styling** (`src/styles.css`)
- Streaming cursor animation
- Code block styling with header
- Copy button styling
- Comparison history panel styling
- Streaming indicators
- See superprompt lines 940-1000 for all CSS

### Dependencies

**11. Install npm packages**
```bash
npm install react-markdown remark-gfm react-syntax-highlighter
```

### Testing & Documentation

**12. Create manual testing checklist** (`TESTING_CHECKLIST.md` - NEW FILE)
- Comprehensive UX/UI test cases
- Streaming functionality (1-4 models, cancellation, errors)
- Markdown rendering (formatting, tables, lists)
- Code blocks (syntax highlighting, copy buttons)
- Comparison history (display, pagination, reload)
- Browser compatibility (Chrome, Firefox, Safari, Edge)
- See superprompt lines 1000-1080 for complete checklist template

**13. Execute manual testing**
- Run through entire TESTING_CHECKLIST.md
- Document any bugs found and fix them
- Take screenshots of key features
- Ensure 90%+ of checklist passes

**14. Update documentation**
- Update `CHANGELOG.md` - change "(Planned)" to actual implementation notes
- Update `README.md` - add streaming capabilities section
- Add inline code comments for complex streaming logic

---

## ⚠️ Critical Requirements (NON-NEGOTIABLE)

### Security
- ✅ JWT authentication required on streaming endpoint
- ✅ CSRF token validation
- ✅ Rate limiting enforced (may need tuning for streaming)
- ✅ Stream timeout after 120 seconds
- ✅ No API keys or secrets in event stream
- ✅ Proper connection cleanup (no memory leaks)

### Code Quality
- ✅ Black formatting for all Python code (max line length 100)
- ✅ Type hints on all new Python functions
- ✅ PropTypes for all React components
- ✅ No console errors or warnings
- ✅ Follow existing patterns (service layer, dependency injection)
- ✅ Graceful degradation (partial failures don't break page)
- ✅ Run `scripts/lint.sh` (or `scripts/lint.sh --fix`) before opening a PR; CI uses the same settings

### Error Handling
- ✅ If one model fails, others continue streaming
- ✅ Show clear error messages in failing model's card
- ✅ Connection lost? Show partial responses + error banner
- ✅ Timeout? Show what was received before timeout

---

## 📊 Success Criteria (Definition of Done)

Phase 3 is complete when ALL of these are true:

- [ ] Multiple models (2-4) stream responses simultaneously in real-time
- [ ] Time to first token < 1 second for all providers
- [ ] Markdown renders correctly (bold, italic, lists, tables, links)
- [ ] Code blocks have syntax highlighting for 100+ languages
- [ ] Copy buttons work on all code blocks
- [ ] Comparison history UI displays with pagination
- [ ] Click on history item reloads that comparison
- [ ] Request cancellation works (button stops streaming, cleans up)
- [ ] Errors handled gracefully (one model fails → others continue)
- [ ] Manual testing checklist 90%+ complete (documented in TESTING_CHECKLIST.md)
- [ ] No console errors or warnings in browser
- [ ] No Python errors in backend logs
- [ ] CHANGELOG.md updated with actual implementation
- [ ] README.md updated with streaming features
- [ ] All code formatted correctly (Black for Python)
- [ ] CI/CD passes (existing tests still pass)

---

## 🗺️ Implementation Strategy

### Week 1: Core Streaming (Days 1-6)

**Day 1-2: Backend Streaming**
1. Read `SUPERPROMPT_PHASE3_STREAMING.md` lines 350-600
2. Review existing code:
   - `llmselect/services/llm.py` - current LLM service
   - `llmselect/routes/chat.py` - existing `/api/v1/compare` endpoint
3. Implement streaming methods in LLM service (4 providers)
4. Test each provider's streaming manually with curl/Python script

**Day 3-4: SSE Endpoint**
1. Add `POST /api/v1/compare/stream` endpoint
2. Implement ThreadPoolExecutor parallel streaming
3. Test with 2, then 3, then 4 models
4. Verify NDJSON event format
5. Test error scenarios (missing API key, invalid model)

**Day 5-6: Frontend Streaming**
1. Read superprompt lines 650-800
2. Create `useStreamingComparison` hook
3. Update `ComparisonMode` to use streaming
4. Test end-to-end streaming (backend → frontend)
5. Add cancel button functionality

### Week 2: Polish & Testing (Days 7-14)

**Day 7-8: Markdown Rendering**
1. Install dependencies (react-markdown, remark-gfm, react-syntax-highlighter)
2. Create `MessageContent` component
3. Create `CopyButton` component
4. Update `ResponseCard` and `MessageList` to use new components
5. Test with various markdown features
6. Add CSS styling for code blocks

**Day 9-10: Comparison History**
1. Create `ComparisonHistory` component
2. Integrate into `ComparisonMode`
3. Test pagination and click-to-reload
4. Add CSS styling for history panel

**Day 11-13: Testing**
1. Create `TESTING_CHECKLIST.md` (use template from superprompt)
2. Execute all test cases systematically
3. Document results
4. Fix any bugs found
5. Re-test failed cases
6. Take screenshots of features

**Day 14: Documentation & Finalization**
1. Update `CHANGELOG.md` with actual implementation
2. Update `README.md` with streaming capabilities
3. Add inline comments for complex code
4. Verify CI/CD passes
5. Final smoke test of all features
6. Open pull request

---

## 📚 Required Reading

**MUST READ BEFORE STARTING:**
1. `SUPERPROMPT_PHASE3_STREAMING.md` (entire file - 1,134 lines)
2. `DECISIONS.md` (ADRs 007-011 for context on architectural decisions)
3. `archive/SUPERPROMPT_PHASE2_COMPLETE.md` (understand Phase 2 patterns)

**Helpful References:**
- `llmselect/services/llm.py` - existing LLM service patterns
- `llmselect/routes/chat.py` - existing comparison endpoint
- `src/components/ComparisonMode.js` - current UI to enhance
- `backlog.md` (lines 150-300) - Phase 3 original requirements

---

## 🚨 Common Pitfalls to Avoid

1. **Don't stream sequentially** - All models must stream in parallel (ThreadPoolExecutor)
2. **Don't forget model_index** - Events must include `model_index` to route to correct card
3. **Don't break on partial failure** - One model error shouldn't stop others
4. **Don't skip connection cleanup** - Must close EventSource and abort fetch on cancel
5. **Don't forget CSRF tokens** - Streaming endpoint needs CSRF validation
6. **Don't skip manual testing** - Automated tests deferred to Phase 4, must test manually
7. **Don't modify existing endpoints** - Keep `/api/v1/compare` working, add new `/stream` endpoint
8. **Don't skip markdown security** - Use react-markdown (XSS-safe), not dangerouslySetInnerHTML

---

## 🤝 Communication

While implementing:
- **Add inline comments** for complex streaming logic (event parsing, ThreadPoolExecutor)
- **Document decisions** - If you make implementation choices, note them in code comments
- **Update CHANGELOG.md** - Track what you actually implemented (not just plans)
- **Create TESTING_CHECKLIST.md** - Use template from superprompt, document results
- **Take screenshots** - Visual proof that streaming works

---

## 🎬 Getting Started

**Step 1:** Read the complete specification
```bash
cat SUPERPROMPT_PHASE3_STREAMING.md
```

**Step 2:** Review architectural decisions
```bash
cat DECISIONS.md | grep -A 30 "ADR-007\|ADR-008\|ADR-009\|ADR-010\|ADR-011"
```

**Step 3:** Create feature branch
```bash
git checkout -b copilot/phase-3-streaming
```

**Step 4:** Start with backend streaming (Part 1)
- Open `llmselect/services/llm.py`
- Add `invoke_stream()` method
- Implement 4 provider-specific streaming methods
- Test each one manually

**Step 5:** Follow the superprompt part-by-part
- Part 1: Backend streaming (Days 1-3)
- Part 2: Frontend streaming (Days 4-6)
- Part 3: Markdown rendering (Days 7-8)
- Part 4: Comparison history (Days 9-10)
- Part 5: Testing & polish (Days 11-13)
- Part 6: Documentation (Day 14)

**Step 6:** When complete, open PR with this description:
```
Phase 3: Real-Time Streaming Comparison

Implements parallel streaming for multi-model comparison with markdown rendering.

Features:
- Multi-model parallel streaming (2-4 models simultaneously)
- Server-Sent Events (SSE) with NDJSON format
- Markdown rendering with syntax highlighting (100+ languages)
- Comparison history UI with pagination
- Request cancellation support
- Graceful error handling

Technical:
- Backend: ThreadPoolExecutor for parallel streaming
- Frontend: EventSource with multiplexed events
- Libraries: react-markdown, remark-gfm, react-syntax-highlighter
- Security: JWT auth, CSRF tokens, rate limiting, timeouts

Testing:
- Manual testing checklist (TESTING_CHECKLIST.md)
- 90%+ test cases passed
- No console errors or warnings

Closes #[issue-number]
```

---

## ✅ Final Checklist Before Opening PR

- [ ] All 16 success criteria met (see Definition of Done section above)
- [ ] TESTING_CHECKLIST.md created and 90%+ complete
- [ ] CHANGELOG.md updated with actual implementation
- [ ] README.md updated with streaming features
- [ ] No console errors in browser
- [ ] No Python errors in backend
- [ ] Black formatting applied to all Python files
- [ ] CI/CD passes (run `pytest` to verify)
- [ ] Screenshots taken of key features
- [ ] All provider streaming tested (OpenAI, Anthropic, Gemini, Mistral)

---

**Ready to build the killer feature! 🚀**

Start by reading `SUPERPROMPT_PHASE3_STREAMING.md` completely, then follow the 6-part implementation plan. The superprompt has all the code examples, patterns, and details you need.

Good luck!

# GitHub Copilot Coding Agent Prompt - Phase 4

Copy and paste this prompt to invoke the GitHub Copilot coding agent:

---

**Implement Phase 4: Performance Optimization & Code Quality**

Please implement Phase 4 of the LLMSelect project following the comprehensive specification in `SUPERPROMPT_PHASE4_PERFORMANCE_REFACTOR.md`.

**Context:**
- Phases 1-3 are complete: security infrastructure, comparison mode UI with streaming, markdown rendering
- Azure AI Foundry integration is complete
- Current performance baseline: 2-3s page load, no caching, no database indexes
- Backend tests: 12/13 passing (92%), Frontend tests: 0%
- App.js is 261 lines and needs refactoring

**Phase 4 Goals:**
1. **Database & Backend Performance** - Add indexes, connection pooling, query optimization
2. **Response Caching** - Implement Flask-Caching for model registry and conversations
3. **Frontend Architecture Refactor** - Extract custom hooks, implement Context API, simplify App.js to <50 lines
4. **Testing Infrastructure** - Expand backend to >80% coverage, add frontend tests to >60%
5. **Conversation Management UI** - Build sidebar with search, rename, delete functionality

**Implementation Order:**
1. Week 1: Database indexes → Connection pooling → Caching → Query optimization
2. Week 2-3: Extract hooks (useAuth, useChat, useComparison, useModels, useApiKeys) → Context API → Component restructure
3. Week 3-4: Expand test coverage (streaming, caching, performance tests) → Jest + React Testing Library setup
4. Week 4: ConversationSidebar component with search/rename/delete

**Success Criteria:**
- Page load < 1s (from 2-3s)
- Database queries < 50ms (with indexes)
- App.js < 50 lines (from 261)
- Backend test coverage >80%, Frontend >60%
- No N+1 query issues
- Conversation sidebar fully functional

**Key Files to Reference:**
- Implementation guide: `SUPERPROMPT_PHASE4_PERFORMANCE_REFACTOR.md` (1,700+ lines with complete code examples)
- Project status: `backlog.md`
- Current architecture: `README.md`, `llmselect/`, `src/`

**Please:**
- Follow the 21-day implementation checklist in the SUPERPROMPT
- Commit frequently with clear messages (reference Git commit guide)
- Test after each major change
- Update CHANGELOG.md with progress
- Ask questions if anything is unclear

Start with Part 1 (Database & Backend Performance) as it provides the biggest immediate impact.

---

**Alternative Short Prompt (if character limit):**

Implement Phase 4 performance optimization following `SUPERPROMPT_PHASE4_PERFORMANCE_REFACTOR.md`: (1) Add database indexes & caching, (2) Extract React hooks & Context API, (3) Expand test coverage to >80%/60%, (4) Build conversation sidebar. Goals: <1s page load, <50 lines App.js, no N+1 queries. Start with database indexes for immediate wins.

---

**For Pull Request Creation:**

When ready to create a PR, use:
- Branch name: `phase4-performance-refactor`
- PR title: `Phase 4: Performance Optimization & Code Quality`
- PR description: Reference `SUPERPROMPT_PHASE4_PERFORMANCE_REFACTOR.md` and list completed items from the checklist

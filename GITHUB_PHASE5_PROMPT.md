# GitHub Copilot Coding Agent - Phase 5 Implementation Prompt

**Phase:** 5 - Database Performance & Response Caching  
**Branch Strategy:** Create feature branches, open PRs, move to next if blocked  
**Documentation:** Update all reference docs as you progress  
**Date:** November 9, 2025

---

## 🎯 Mission

Implement **Phase 5: Database Performance & Response Caching** as detailed in `SUPERPROMPT_PHASE5_DATABASE_CACHING.md`. Work through all tasks systematically, create PRs for each major section, and continue forward momentum even when blocked.

## 📋 Core Instructions

### Working Style
1. **Read the superprompt first**: Study `SUPERPROMPT_PHASE5_DATABASE_CACHING.md` in full before starting
2. **Work incrementally**: Implement one subsection at a time, test it, commit it
3. **Create focused PRs**: When a logical unit is complete, open a PR and move to the next
4. **Handle blockers**: If you hit an issue that requires review/external input:
   - Document the blocker clearly in the PR description
   - Mark PR as "Ready for Review" with clear next steps
   - Move to the next independent task
   - Do NOT stop and wait - keep making progress
5. **Update documentation**: Keep reference docs current as you implement

### Implementation Order

**Part 1: Database Optimization** (PR #1)
- Create `migrations/002_add_performance_indexes.sql`
- Update/create `scripts/run_migrations.py`
- Run migrations and verify indexes
- Test query performance improvements
- Update `CHANGELOG.md` with database changes

**Part 2: Connection Pooling** (PR #2)
- Update `llmselect/config.py` with connection pool settings
- Update `llmselect/extensions.py` if needed
- Add pool stats to health endpoint
- Test connection pool under load
- Update `CHANGELOG.md`

**Part 3: Query Optimization** (PR #3)
- Add slow query logging to `llmselect/extensions.py`
- Optimize `llmselect/services/conversations.py` with eager loading
- Implement cursor-based pagination
- Add tests for N+1 query prevention
- Update `CHANGELOG.md`

**Part 4: Flask-Caching Setup** (PR #4)
- Add `Flask-Caching==2.1.0` to `requirements.txt`
- Configure cache in `llmselect/config.py`
- Initialize cache in `llmselect/extensions.py`
- Update `llmselect/__init__.py` to init cache
- Test cache in dev environment
- Update `CHANGELOG.md`

**Part 5: Model Registry Caching** (PR #5)
- Add caching to `llmselect/services/llm_service.py`
- Implement cache invalidation methods
- Add admin endpoint for cache clearing
- Test model registry caching
- Update `CHANGELOG.md`

**Part 6: Conversation Caching** (PR #6)
- Add caching to `llmselect/services/conversations.py`
- Implement cache invalidation on mutations
- Add cache headers to responses in routes
- Test conversation caching
- Update `CHANGELOG.md`

**Part 7: Performance Monitoring** (PR #7)
- Create `llmselect/middleware/performance.py`
- Add request timing middleware
- Add `X-Response-Time` headers
- Log slow requests (>500ms)
- Update `CHANGELOG.md`

**Final: Documentation & Testing** (PR #8 or add to last PR)
- Update `README.md` with performance improvements
- Update `LOCAL_SETUP.md` if needed
- Add performance testing script if not exists
- Update `backlog.md` to mark Phase 5 complete
- Create `PHASE5_IMPLEMENTATION_SUMMARY.md`

---

## 🚨 Critical Guidelines

### When You Encounter Blockers

**DO:**
- ✅ Document the blocker clearly in commit/PR
- ✅ Mark what's complete vs. what needs review
- ✅ Open the PR and mark as "Ready for Review"
- ✅ Move to the next independent task/PR
- ✅ Keep making progress on other items

**DON'T:**
- ❌ Stop work and wait for human intervention
- ❌ Leave code half-implemented without commits
- ❌ Skip documentation updates
- ❌ Abandon the PR without clear status

### Example Blocker Scenarios

**Scenario 1: Database Migration Fails**
```
Action: 
1. Document the error in PR description
2. Commit what works (e.g., the SQL file itself)
3. Add clear reproduction steps to PR
4. Mark PR for review: "Database migration script complete, needs testing on production DB"
5. Move to Part 2 (Connection Pooling) which doesn't depend on Part 1
```

**Scenario 2: Tests Fail After Implementation**
```
Action:
1. Document test failures in PR
2. If it's a minor fix, implement it
3. If it's a design issue, document options in PR description
4. Commit the implementation with failing test documented
5. Mark PR: "Implementation complete, test failures need architecture decision"
6. Move to next PR
```

**Scenario 3: Missing Dependency/Service**
```
Action:
1. Check if you can install/configure it yourself
2. If blocked by permissions, document requirements in PR
3. Commit the code that would use it (with feature flag if needed)
4. Mark PR: "Code ready, needs X dependency installed in environment"
5. Move to next PR that doesn't have this dependency
```

### Testing Requirements

For each PR, include:
- ✅ Manual testing steps in PR description
- ✅ Automated tests where applicable
- ✅ Before/After metrics if relevant (query times, cache hit rates)
- ✅ Any breaking changes clearly documented

---

## 📝 Documentation Updates

Update these files as you progress:

### CHANGELOG.md
Add entries under `## [Unreleased]` for each change:
```markdown
### Added
- Database indexes for conversations, messages, api_keys, comparison_results
- Connection pooling with SQLAlchemy (pool_size=20, max_overflow=20)
- Flask-Caching for model registry and conversation lists
- Slow query logging (>100ms)
- Request timing middleware with X-Response-Time header

### Changed
- Query patterns now use eager loading to eliminate N+1 queries
- Conversation pagination now uses cursor-based approach
- Model registry cached for 24 hours (reduces external API calls by 90%)

### Performance
- Common database queries now execute in <50ms (was >200ms)
- Conversation list load times improved by 70%
- Model registry API calls reduced by 90%
```

### backlog.md
When Phase 5 is complete:
```markdown
### Completed ✅
- ✅ **Phase 5**: Database performance optimization (indexes, connection pooling)
- ✅ **Phase 5**: Response caching (Flask-Caching, model registry, conversations)

### In Progress 🚧
- 🚧 **Phase 6**: Frontend architecture refactor (custom hooks, Context API)
```

### README.md (if applicable)
Add performance achievements to relevant sections:
- Mention caching capabilities
- Note performance improvements
- Update deployment requirements if needed

---

## 🎯 Success Criteria Checklist

By the end of Phase 5, verify:

**Database Performance:**
- [ ] All indexes created and active
- [ ] Connection pool configured (10-20 connections)
- [ ] Common queries execute in <50ms
- [ ] No N+1 query issues detected
- [ ] Slow query logging active and working

**Response Caching:**
- [ ] Flask-Caching installed and configured
- [ ] Model registry cached (24-hour TTL)
- [ ] Conversation lists cached (5-minute TTL)
- [ ] Cache hit rate >80% for repeated queries
- [ ] Cache invalidation working correctly

**Performance Monitoring:**
- [ ] Request timing middleware active
- [ ] X-Response-Time header in responses
- [ ] Slow requests logged (>500ms)
- [ ] Performance metrics captured

**Documentation:**
- [ ] CHANGELOG.md updated with all changes
- [ ] backlog.md updated to mark Phase 5 complete
- [ ] PHASE5_IMPLEMENTATION_SUMMARY.md created
- [ ] All code changes have clear commit messages

**Quality:**
- [ ] All PRs have clear descriptions
- [ ] Tests pass (or failures documented)
- [ ] No breaking changes to existing functionality
- [ ] Code follows project conventions

---

## 🚀 Getting Started

**Step 1:** Read the superprompt
```bash
# Open and read the full superprompt
cat SUPERPROMPT_PHASE5_DATABASE_CACHING.md
```

**Step 2:** Create your first feature branch
```bash
git checkout -b feature/phase5-database-indexes
```

**Step 3:** Start with Part 1 (Database Optimization)
- Create the migration file
- Create/update the migration script
- Test it locally
- Commit and open PR

**Step 4:** Continue through each part
- Open separate PRs for each major section
- Keep moving forward even if PRs are pending review
- Update documentation as you go

---

## 💡 Tips for Success

1. **Read First, Code Second**: Understand the full scope before starting
2. **Commit Often**: Small, focused commits are easier to review
3. **Test As You Go**: Don't wait until the end to test
4. **Document Blockers**: Clear documentation helps reviewers help you
5. **Keep Moving**: Don't let one blocker stop all progress
6. **Update Docs**: Documentation is part of the implementation, not an afterthought
7. **Clear PR Descriptions**: Explain what's done, what's pending, what's blocked

---

## 📞 Reporting Progress

In each PR description, include:

```markdown
## Phase 5 Progress: [Part Name]

**Status:** ✅ Complete | 🚧 In Progress | ⏸️ Blocked

**What's Implemented:**
- [x] Task 1
- [x] Task 2
- [ ] Task 3 (blocked by X)

**Testing:**
- Manual testing: [steps you performed]
- Automated tests: [test results]
- Performance metrics: [before/after numbers if applicable]

**Blockers/Decisions Needed:**
- [List any items that need review or decisions]

**Next Steps:**
- [What should be done after this PR]

**Documentation Updated:**
- [x] CHANGELOG.md
- [ ] README.md (not needed for this PR)
- [x] Code comments
```

---

## 🎬 Ready to Begin!

You have everything you need:
- ✅ Detailed superprompt: `SUPERPROMPT_PHASE5_DATABASE_CACHING.md`
- ✅ Clear implementation order
- ✅ Blocker handling strategy
- ✅ Documentation requirements
- ✅ Success criteria

**Your mission:** Implement Phase 5 with maximum forward momentum. Create PRs, handle blockers gracefully, keep documentation updated, and maintain progress even when individual items are blocked.

**Start now with:** Database indexes (Part 1) - Create the migration file and get that first PR open!

🚀 Let's optimize this application for production performance!

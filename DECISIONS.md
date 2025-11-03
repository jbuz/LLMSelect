# Decision Log

This document tracks significant decisions, architectural choices, incidents, and trade-offs made during development. All entries are append-only to maintain a complete history.

## Purpose

- Document decisions for future reference
- Track security incidents and responses
- Record trade-offs and their rationale
- Maintain reversibility context
- Enable team alignment

## Format

Each decision entry should include:
- **Date**: When the decision was made
- **Title**: Brief description
- **Context**: Why this decision was needed
- **Options Considered**: Alternative approaches
- **Choice**: Selected approach with rationale
- **Security Implications**: Any security-related impacts
- **Reversibility**: easy | moderate | hard
- **Impacted Files**: List of affected files
- **Follow-ups**: Any required future actions

---

# Architectural Decision Records (Phase 2)

## ADR-001: Database Model for Comparison Results

**Date**: 2025-10-31  
**Status**: Accepted  
**Context**: Need to persist multi-model comparison results for history and analytics

### Decision
Store comparison results as a single JSON column rather than normalizing into separate tables.

### Rationale
- **Flexibility**: Results structure may vary across providers (metadata, errors, etc.)
- **Simplicity**: Single query to retrieve full comparison
- **Performance**: Avoid multiple JOINs for a common read operation
- **Schema Evolution**: Easy to add new fields without migrations

### Structure
```python
class ComparisonResult(db.Model):
    id = Integer (PK)
    user_id = Integer (FK)
    prompt = Text
    results = JSON  # Array of {provider, model, response, time, tokens, error}
    preferred_index = Integer (nullable)
    created_at, updated_at = Timestamps
```

### Alternatives Considered
1. **Normalized Schema**: Separate `comparison_results` and `comparison_responses` tables
   - Rejected: Overhead for simple use case, no complex queries needed
2. **JSONB in PostgreSQL**: Use JSONB for indexing and querying
   - Deferred: SQLite for development, can migrate later if needed

### Consequences
- ✅ Fast reads for displaying comparisons
- ✅ Easy to extend with new metadata fields
- ⚠️ Cannot efficiently query by individual response properties
- ⚠️ Slightly more complex validation logic in application layer

---

## ADR-002: Response Metadata Collection

**Date**: 2025-10-31  
**Status**: Accepted  
**Context**: Users want to compare model performance (speed, efficiency)

### Decision
Measure and store response time and estimate token count for each model in comparison.

### Implementation
- Wrap LLM service calls with timing measurement
- Use simple heuristic for token estimation: `len(text) / 4`
- Store in results JSON: `{time: float, tokens: int}`

### Rationale
- **User Value**: Performance is a key comparison criterion
- **Simplicity**: Timing is trivial to measure accurately
- **Cost Awareness**: Token estimates help users understand costs
- **No External Deps**: Avoid tokenizer libraries for now

### Alternatives Considered
1. **Accurate Tokenization**: Use tiktoken, anthropic tokenizer, etc.
   - Rejected: Different tokenizers per provider, added complexity
   - May revisit if users request it
2. **Cost Calculation**: Estimate actual costs based on pricing
   - Deferred: Pricing changes frequently, hard to maintain
   - Left as optional field for future

### Consequences
- ✅ Lightweight and performant
- ✅ Good enough for comparison purposes
- ⚠️ Token estimates are approximate (~20% variance)
- ⚠️ No actual cost calculation (users must estimate)

---

## ADR-003: Frontend Component Architecture

**Date**: 2025-10-31  
**Status**: Accepted  
**Context**: Need to add comparison mode without disrupting existing chat interface

### Decision
Use mode-based conditional rendering in App.js rather than React Router or tabs.

### Structure
```
App.js (mode state: 'chat' | 'compare')
├─ Header (mode toggle)
├─ ChatMode (existing MessageList + MessageInput)
└─ ComparisonMode
   ├─ ModelSelector
   ├─ MessageInput
   └─ ResponseCard[] (grid)
```

### Rationale
- **Simplicity**: No routing library needed for 2 modes
- **State Preservation**: Chat history preserved when switching modes
- **User Experience**: Instant mode switching, no page reload
- **Low Risk**: Minimal changes to existing chat code

### Alternatives Considered
1. **React Router**: Separate routes for /chat and /compare
   - Rejected: Overkill for simple mode switching
   - May revisit if more pages added
2. **Tabs UI**: Tabs within single view
   - Rejected: Modes are distinct enough to warrant full-screen

### Consequences
- ✅ Simple implementation
- ✅ Fast mode switching
- ✅ No new dependencies
- ⚠️ URL doesn't reflect mode (can't bookmark comparison view)
- ⚠️ Both modes loaded into bundle (small overhead)

---

## ADR-004: Model Selection UI

**Date**: 2025-10-31  
**Status**: Accepted  
**Context**: Users need to select 2-4 models for comparison

### Decision
Use chip-based selector with color coding by provider.

### Features
- Selected models shown as colored chips
- "+" button opens dropdown to add models
- Remove button on each chip (if >= min selection)
- Enforces 2-4 model range

### Color Mapping
- OpenAI: Green (#10a37f)
- Anthropic: Orange (#d97757)
- Google: Blue (#4285f4)
- Mistral: Amber (#f2a73b)

### Rationale
- **Visual Clarity**: Colors help users quickly identify providers
- **Space Efficient**: Compact display of selected models
- **Intuitive**: Similar to tag selectors in modern UIs
- **Accessible**: Text labels in addition to colors

### Alternatives Considered
1. **Checkboxes**: List of all models with checkboxes
   - Rejected: Takes too much vertical space
2. **Drag & Drop**: Drag models into comparison area
   - Rejected: Unnecessary complexity for simple selection

### Consequences
- ✅ Clean, modern UI
- ✅ Easy to understand and use
- ✅ Scalable if more providers added
- ⚠️ Color blind users may have difficulty (mitigated by text labels)

---

## ADR-005: Error Handling in Parallel Comparisons

**Date**: 2025-10-31  
**Status**: Accepted  
**Context**: Comparisons run models in parallel; individual failures shouldn't block others

### Decision
Catch exceptions per provider and return error responses alongside successful ones.

### Implementation
```python
try:
    results.append({
        "provider": provider,
        "model": model,
        "response": llm_service.invoke(...),
        "time": elapsed,
        "tokens": estimate_tokens(response)
    })
except Exception as exc:
    results.append({
        "provider": provider,
        "model": model,
        "response": str(exc),
        "time": 0,
        "tokens": 0,
        "error": True  # Flag for frontend
    })
```

### Rationale
- **Resilience**: Partial results are better than total failure
- **User Experience**: Users see what worked and what failed
- **Debugging**: Error messages help users diagnose API key issues

### Alternatives Considered
1. **Fail Fast**: Abort comparison if any provider fails
   - Rejected: Too strict, frustrating for users
2. **Retry Logic**: Automatically retry failed requests
   - Deferred: Adds latency, better as future enhancement

### Consequences
- ✅ Robust handling of provider outages
- ✅ Clear error visibility
- ⚠️ Mixed success/error results may confuse users
- ⚠️ Need clear UI indication of errors (added error flag)

---

## ADR-006: Voting Mechanism

**Date**: 2025-10-31  
**Status**: Accepted  
**Context**: Users want to record which model's response they preferred

### Decision
Store single `preferred_index` (0-based) per comparison, mutable via POST endpoint.

### Implementation
- `preferred_index`: Integer column (nullable)
- `POST /api/v1/comparisons/:id/vote` with `{preferred_index: int}`
- Users can change their vote by submitting again

### Rationale
- **Simplicity**: Single preference is sufficient for most use cases
- **Flexibility**: Users can change their mind
- **Analytics**: Can analyze which models win most often (future)

### Alternatives Considered
1. **Multi-Vote**: Allow users to vote for multiple responses
   - Rejected: Complicates analytics, unclear use case
2. **Thumbs Up/Down**: Boolean per response
   - Rejected: Doesn't indicate relative preference
3. **Star Rating**: 1-5 stars per response
   - Deferred: More complex, can add later if needed

### Consequences
- ✅ Simple to implement and understand
- ✅ Clear analytics path
- ⚠️ No multi-dimensional feedback (e.g., accuracy vs creativity)
- ⚠️ No "neutral" option (users must skip voting)

---

# Security & Infrastructure Decisions

## [2025-10-31] Initial Security Infrastructure Setup

### Context
The repository is public and needs comprehensive security measures as Priority Zero. The codebase has good security foundations (JWT, CSRF, encryption) but lacks security automation, documentation, and CI gates.

### Options Considered
1. **Minimal approach**: Only add SECURITY.md and basic documentation
2. **Moderate approach**: Add docs + pre-commit hooks + basic CI scanning
3. **Comprehensive approach**: Full security stack with all gates and automation

### Choice
**Option 3: Comprehensive approach**

**Rationale**:
- Public repository requires maximum security rigor
- Problem statement explicitly requires P0 security focus
- Better to over-engineer security than under-engineer
- Early security investment prevents future incidents
- Compliance with industry best practices

**Security Implications**:
- ✅ Prevents secret leaks before they occur
- ✅ Catches vulnerabilities early in development
- ✅ Creates audit trail and accountability
- ✅ Enforces security review for all changes
- ✅ Provides transparency through SECURITY.md

### Reversibility
**Easy** - All additions are additive and can be disabled if needed

### Impacted Files
- Added: `SECURITY.md`
- Added: `CONTRIBUTING.md`
- Added: `CODE_OF_CONDUCT.md`
- Added: `DECISIONS.md` (this file)
- Planned: `CHANGELOG.md`, `CODE_IMPROVEMENT.md`, `docs/WORKLOG.md`
- Planned: `.github/workflows/*`
- Planned: `.pre-commit-config.yaml`
- Planned: `.github/CODEOWNERS`

### Follow-ups
- [ ] Create GitHub Actions workflows for security scanning
- [ ] Set up pre-commit hooks
- [ ] Add CODEOWNERS file
- [ ] Create remaining documentation files
- [ ] Test all security gates in CI

---

## [2025-10-31] Environment Variable Management

### Context
The codebase uses `.env` files for configuration, which is correct, but we need to ensure no secrets ever get committed.

### Options Considered
1. **Current state**: Rely on `.gitignore` only
2. **Pre-commit scanning**: Add gitleaks/trufflehog hooks
3. **Both CI and pre-commit**: Scan locally and in CI

### Choice
**Option 3: Both CI and pre-commit scanning**

**Rationale**:
- Defense in depth - multiple layers of protection
- Pre-commit catches issues before they reach remote
- CI scanning catches issues if hooks are bypassed
- Minimal performance impact (scanning is fast)
- Industry standard practice

**Security Implications**:
- ✅ Double protection against secret leaks
- ✅ Scanning covers both staged changes and history
- ✅ CI failures prevent merging compromised code
- ✅ Visible audit trail in CI logs

### Reversibility

### Reversibility
**Easy** - Can disable either layer independently

### Impacted Files
- Modified: `.gitignore` (already correct)
- Verified: `.env.example` (contains only placeholders)
- Added: `.pre-commit-config.yaml` (planned)
- Added: `.github/workflows/security-scan.yml` (planned)

### Follow-ups
- [ ] Install gitleaks in CI
- [ ] Configure pre-commit with gitleaks
- [ ] Document setup in CONTRIBUTING.md (done)
- [ ] Test secret detection with sample secrets

---

## [2025-10-31] GitHub Actions Security Hardening

### Context
GitHub Actions workflows will be created for CI/CD. Best practice is to pin actions to commit SHAs rather than tags to prevent supply chain attacks.

### Options Considered
1. **Pin to tags**: `uses: actions/checkout@v3`
2. **Pin to SHAs**: `uses: actions/checkout@abc123...`
3. **Pin to SHAs with comments**: Include tag in comment for readability

### Choice
**Option 3: Pin to SHAs with comments**

**Rationale**:
- Maximum security (tags can be moved, SHAs cannot)
- Comments maintain readability: `# v3.0.0`
- Prevents supply chain attacks via action hijacking
- Aligns with OSSF recommendations
- Dependabot can still update pinned SHAs

**Security Implications**:
- ✅ Protects against malicious action updates
- ✅ Provides immutable action references
- ✅ Audit trail shows exact action version
- ⚠️ Requires discipline to update periodically

### Reversibility
**Moderate** - Can revert to tags, but reduces security

### Impacted Files
- All files in `.github/workflows/` (to be created)

### Follow-ups
- [ ] Create workflows with SHA pinning
- [ ] Document SHA update process
- [ ] Set up Dependabot for GitHub Actions updates

---

## [2025-10-31] Dependency Management Strategy

### Context
Python and JavaScript dependencies need vulnerability scanning and version pinning.

### Options Considered
1. **Manual updates**: Check dependencies manually
2. **Dependabot only**: Auto-generated PRs for updates
3. **Dependabot + CI scanning**: Automated updates + vulnerability checks
4. **Add Renovate**: Alternative to Dependabot with more features

### Choice
**Option 3: Dependabot + CI scanning**

**Rationale**:
- Dependabot is native to GitHub (no extra setup)
- CI scanning catches vulnerabilities in all dependencies
- Combination provides both proactive and reactive protection
- Can enable auto-merge for security-only updates
- Renovate can be added later if needed

**Security Implications**:
- ✅ Automated vulnerability detection
- ✅ Fast response to security updates
- ✅ Audit trail of dependency changes
- ⚠️ Must review auto-merged updates periodically

### Reversibility
**Easy** - Can disable Dependabot or scanning independently

### Impacted Files
- Added: `.github/dependabot.yml` (planned)
- Added: `.github/workflows/dependency-review.yml` (planned)

### Follow-ups
- [ ] Enable Dependabot in repository settings
- [ ] Create dependabot.yml configuration
- [ ] Add dependency-review-action to CI
- [ ] Configure auto-merge rules for security updates

---

## [2025-10-31] SBOM Generation Approach

### Context
Problem statement requires SBOM (Software Bill of Materials) generation and publication.

### Options Considered
1. **Syft (Anchore)**: Industry standard, supports multiple formats
2. **CycloneDX**: Spec-focused approach
3. **SPDX**: Alternative standard
4. **GitHub native**: GitHub's built-in SBOM generation

### Choice
**Option 1: Syft**

**Rationale**:
- Most widely used in the industry
- Supports both Python and JavaScript ecosystems
- Multiple output formats (JSON, SPDX, CycloneDX)
- Easy to integrate in CI
- Active maintenance and community

**Security Implications**:
- ✅ Provides complete dependency visibility
- ✅ Enables supply chain security analysis
- ✅ Supports compliance requirements
- ✅ Helps with vulnerability tracking

### Reversibility
**Easy** - Can switch to alternative SBOM tool

### Impacted Files
- Added: `.github/workflows/sbom.yml` (planned)
- Generated: `sbom.json` as CI artifact

### Follow-ups
- [ ] Add Syft to CI workflow
- [ ] Configure SBOM generation on release
- [ ] Publish SBOM as release artifact
- [ ] Document SBOM location in README

---

## Template for Future Decisions

```markdown
## [YYYY-MM-DD] Decision Title

### Context
Why this decision was needed

### Options Considered
1. Option A: Description
2. Option B: Description
3. Option C: Description

### Choice
**Selected option with rationale**

**Security Implications**:
- ✅ Positive security impact
- ⚠️ Security consideration
- ❌ Security risk (if any)

### Reversibility
easy | moderate | hard - with explanation

### Impacted Files
- List of files affected

### Follow-ups
- [ ] Required actions
```

---

## Template for Incidents

```markdown
## [YYYY-MM-DD] Incident: Brief Description

### Context
What happened

### Impact
- Scope: Systems/data affected
- Severity: Critical | High | Medium | Low
- Users affected: Number/description

### Timeline
- HH:MM - Incident detected
- HH:MM - Response initiated
- HH:MM - Incident contained
- HH:MM - Resolution implemented
- HH:MM - Verification complete

### Root Cause
Technical explanation

### Resolution
- Immediate actions taken
- Secrets rotated (if applicable)
- History cleaned (if applicable)
- Systems restored

### Prevention
- New controls added
- Process changes
- Documentation updated

### Lessons Learned
Key takeaways
```

---

# Architectural Decision Records (Phase 3)

## ADR-006: Server-Sent Events for Streaming Comparisons

**Date**: 2025-11-02  
**Status**: Accepted  
**Context**: Users experience 20-60 second wait times for comparison results. Real-time streaming is needed for better UX.

### Decision
Implement Server-Sent Events (SSE) for streaming comparison results from multiple providers simultaneously.

### Implementation
- New endpoint: `POST /api/v1/compare/stream`
- Flask `stream_with_context()` for SSE generation
- ThreadPoolExecutor for parallel provider streaming
- SSE event types: `start`, `chunk`, `complete`, `error`, `done`
- Frontend uses Fetch API with ReadableStream (not EventSource for POST support)

### Alternatives Considered

1. **WebSockets**: 
   - Rejected: More complex, bidirectional communication unnecessary
   - Higher overhead for unidirectional data flow
   - Requires separate WebSocket server management

2. **HTTP Long Polling**:
   - Rejected: Inefficient, higher latency
   - Multiple request/response cycles
   - Not truly real-time

3. **HTTP/2 Server Push**:
   - Rejected: Limited browser support
   - Requires HTTP/2 infrastructure
   - Less control over data flow

4. **EventSource API**:
   - Rejected for initial implementation: Only supports GET requests
   - Would require passing prompt and models via query params or session
   - Fetch API with ReadableStream provides more flexibility

### Rationale

**Why SSE?**
- Simple unidirectional data flow (server → client)
- Native browser support via Fetch API
- HTTP/1.1 compatible (no infrastructure changes)
- Automatic reconnection possible
- Lower overhead than WebSockets
- Standard text/event-stream format

**Why Fetch over EventSource?**
- EventSource only supports GET requests
- POST needed for secure parameter passing
- Fetch API with ReadableStream gives full control
- Easier to add Authorization headers
- Better error handling capabilities

**Why Parallel Streaming?**
- No blocking between providers
- True sub-second time to first token
- Better user experience
- Efficient use of server resources

### Consequences

**Positive**:
- ✅ Sub-second time to first token
- ✅ Better perceived performance
- ✅ Parallel streaming from multiple providers
- ✅ Native browser support
- ✅ Graceful degradation on provider failures
- ✅ Simple server implementation

**Negative**:
- ⚠️ Keep-alive connections consume server resources
- ⚠️ Need proper cleanup on errors
- ⚠️ No support in Internet Explorer (acceptable tradeoff)
- ⚠️ Must manually parse SSE format (not using EventSource)

**Security**:
- ✅ JWT authentication required
- ✅ Rate limiting applied
- ✅ CSRF protection via JWT
- ✅ Input validation
- ✅ Error messages sanitized

### Implementation Notes

**Backend**:
```python
# SSE format: "data: {json}\n\n"
yield f"data: {json.dumps(event_data)}\n\n"
```

**Frontend**:
```javascript
// Parse SSE stream manually
const reader = response.body.getReader();
const decoder = new TextDecoder();
for await (const chunk of readStream(reader)) {
  if (line.startsWith('data: ')) {
    const data = JSON.parse(line.slice(6));
    handleEvent(data);
  }
}
```

### Performance Metrics
- **Time to first token**: < 1 second (target achieved)
- **Previous**: 20-60 seconds blocking wait
- **Improvement**: 20-60x faster perceived performance

### Reversibility
**Moderate**: 
- SSE endpoint can coexist with batch endpoint
- Frontend can fallback to batch mode
- No database schema changes
- Can remove if needed without data loss

### Follow-ups
- [ ] Add connection limit per user (prevent abuse)
- [ ] Add stream timeout (60 seconds max)
- [ ] Monitor connection count metrics
- [ ] Consider WebSocket upgrade for bidirectional features (future)
- [ ] Add stream resume capability (if connection drops)

---

## ADR-007: React-Markdown with Syntax Highlighting

**Date**: 2025-11-02  
**Status**: Accepted  
**Context**: LLM responses often contain markdown, code blocks, and formatted text. Plain text rendering provides poor UX.

### Decision
Use `react-markdown` with `react-syntax-highlighter` for rich message rendering in both chat and comparison modes.

### Implementation
- **react-markdown** ^9.0.1: Markdown parsing and rendering
- **remark-gfm** ^4.0.0: GitHub Flavored Markdown support
- **react-syntax-highlighter** ^15.5.0: Code highlighting with Prism
- **Theme**: VS Code Dark Plus for consistent dark mode
- **Languages**: 277+ language definitions included

### Alternatives Considered

1. **marked.js + highlight.js**:
   - Rejected: Manual HTML rendering (security risk)
   - Need to sanitize HTML output
   - Less React-friendly

2. **Custom markdown parser**:
   - Rejected: Reinventing the wheel
   - Missing edge cases
   - No GFM support out of box

3. **Monaco Editor for code blocks**:
   - Rejected: Too heavy (full editor)
   - Overkill for display-only
   - Large bundle size impact

4. **Server-side markdown rendering**:
   - Rejected: Less flexible
   - No copy buttons without extra work
   - Harder to customize styling

### Rationale

**Why react-markdown?**
- Well-maintained, popular library (11k+ stars)
- React-native rendering (no dangerouslySetInnerHTML)
- Plugin system for extensibility
- GFM support via remark-gfm
- Safe by default

**Why react-syntax-highlighter?**
- Wide language support (277 languages)
- Multiple themes available
- Prism backend (lighter than highlight.js full)
- Copy-paste friendly output
- Customizable styles

**Why Client-Side?**
- Real-time rendering during streaming
- No server round-trip needed
- Easier to customize per-user preferences (future)
- Better for progressive enhancement

### Consequences

**Positive**:
- ✅ Beautiful code rendering with syntax highlighting
- ✅ Support for tables, lists, task lists (GFM)
- ✅ Copy buttons on code blocks
- ✅ Safe HTML rendering (XSS protection)
- ✅ Consistent styling across app

**Negative**:
- ⚠️ Bundle size increased significantly (246 KB → 1020 KB)
- ⚠️ Includes 277 language definitions (could optimize)
- ⚠️ Initial render slightly slower (negligible in practice)
- ⚠️ No LaTeX math support (could add plugin if needed)

**Bundle Impact**:
- Previous: 246 KB
- Current: 1020 KB
- Increase: 774 KB (4.2x)
- Main contributors:
  - refractor (language definitions): 851 KB
  - react-markdown + plugins: ~100 KB
  - hastscript + utilities: ~75 KB

### Optimization Options (Future)

1. **Lazy Load Languages**:
   - Only load common languages by default
   - Load additional on-demand
   - Could reduce bundle to ~400 KB

2. **Code Splitting**:
   - Separate markdown component chunk
   - Load on first use
   - Better for users who don't use comparison mode

3. **Alternative Highlighter**:
   - Use lighter library (highlight.js minimal)
   - Trade coverage for size
   - Manual language loading

4. **Server-Side Pre-render**:
   - Render markdown server-side for initial load
   - Hydrate client-side for interactivity
   - More complex architecture

### Current Decision
Accept bundle size increase for comprehensive language support. Users get excellent UX out of the box. Can optimize later if needed based on usage metrics.

### Performance Metrics
- **Bundle size**: 1020 KB (gzipped: ~350 KB)
- **Time to Interactive**: No noticeable impact
- **Rendering performance**: Smooth on modern devices

### Security
- ✅ No dangerouslySetInnerHTML usage
- ✅ React components sanitize output
- ✅ XSS-safe by design
- ✅ No eval() or Function() usage

### Reversibility
**Easy**: 
- Can switch back to plain text rendering
- No database impact
- Frontend-only change
- Users might complain (downgrade UX)

### Follow-ups
- [ ] Monitor bundle size impact on mobile users
- [ ] Consider lazy loading for code highlighter
- [ ] Add LaTeX support if users request it (remark-math)
- [ ] Add copy button for entire messages (not just code)
- [ ] Consider server-side rendering for SEO (if needed)

---

**Note**: This file is append-only. Do not modify or delete existing entries. Always add new entries at the bottom.

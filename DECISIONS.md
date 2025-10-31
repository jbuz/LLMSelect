# Architectural Decision Records

This document tracks significant architectural and implementation decisions made during the development of LLMSelect.

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

## Future ADRs

### Candidates for Documentation
- Streaming response implementation (Phase 3)
- Frontend state management (Context vs Redux)
- Markdown/code rendering strategy
- Conversation sidebar design
- Export format selection (JSON/Markdown/PDF)

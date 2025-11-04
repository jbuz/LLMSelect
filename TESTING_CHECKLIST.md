# Testing Checklist for LLMSelect Phase 4

## Automated Testing

### Backend Tests
✅ All backend tests passing (22/22)

#### Model Registry Tests (7 tests)
- ✅ `test_get_all_models` - Retrieves all models from all providers
- ✅ `test_get_openai_models` - Filters OpenAI models only
- ✅ `test_get_anthropic_models` - Filters Anthropic models only
- ✅ `test_get_gemini_models` - Filters Gemini models only
- ✅ `test_get_mistral_models` - Filters Mistral models only
- ✅ `test_models_requires_auth` - Endpoint requires authentication
- ✅ `test_model_registry_caching` - Caching mechanism works correctly

#### Chat Tests (3 tests)
- ✅ `test_chat_creates_and_reuses_conversation` - Chat creates and reuses conversations
- ✅ `test_api_key_storage` - API keys are stored securely
- ✅ `test_chat_stream_endpoint` - SSE streaming endpoint works correctly

#### Comparison Tests (8 tests)
- ✅ `test_compare_saves_to_database` - Comparisons saved to database
- ✅ `test_get_comparison_history` - Can retrieve comparison history
- ✅ `test_vote_on_comparison` - Voting on comparisons works
- ✅ `test_vote_invalid_index` - Invalid votes are rejected
- ✅ `test_comparison_requires_auth` - Requires authentication
- ✅ `test_comparison_pagination` - Pagination works
- ✅ `test_comparison_with_error_handling` - Errors handled gracefully
- ✅ `test_delete_comparison` - Comparison deletion works

#### Auth Tests (2 tests)
- ✅ `test_registration_and_login_flow` - User registration and login
- ✅ `test_refresh_and_logout` - Token refresh and logout

#### LLM Service Tests (2 tests)
- ✅ `test_openai_request_sanitises_messages` - Messages are sanitized
- ✅ `test_provider_error_raises_app_error` - Provider errors handled

### Frontend Build
- ✅ Frontend builds successfully with webpack
- ⚠️  Bundle size warnings (expected, not critical)

## Manual Testing Checklist

### Phase 4 Dynamic Model Management

#### Model Loading
- [ ] Login to the application
- [ ] Navigate to chat mode
- [ ] Verify model dropdown shows latest models:
  - [ ] OpenAI: GPT-4o, GPT-4o Mini, o1-preview, o1-mini
  - [ ] Gemini: gemini-2.0-flash-exp, gemini-1.5-pro, gemini-1.5-flash
  - [ ] Anthropic: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
  - [ ] Mistral: Mistral Large, Medium, Small
- [ ] Verify models load without errors
- [ ] Check browser console for any errors

#### Comparison Mode
- [ ] Switch to comparison mode
- [ ] Click "Add Model" button
- [ ] Verify all latest models appear in dropdown
- [ ] Select multiple models (2-4)
- [ ] Verify selected models display with correct names
- [ ] Verify default selections include latest models

#### API Key Configuration
- [ ] Click "API Keys" in header
- [ ] Configure API keys for at least one provider
- [ ] Save keys successfully
- [ ] Verify keys are encrypted (not visible in network tab)

#### Single Model Chat
- [ ] Configure API key for OpenAI
- [ ] Select GPT-4o model
- [ ] Send a test message: "Hello, how are you?"
- [ ] Verify response streams in real-time ✨ **NEW**
- [ ] Verify streaming cursor appears during response ✨ **NEW**
- [ ] Check conversation is saved after streaming
- [ ] Refresh page and verify conversation persists

#### Chat Streaming Testing ✨ **NEW - Phase 4 Priority 4**
- [ ] Send a message and verify streaming starts immediately
- [ ] Confirm streaming cursor (▊) appears and blinks
- [ ] Verify message accumulates character by character
- [ ] Test cancel button appears during streaming
- [ ] Click cancel button mid-stream and verify it stops
- [ ] Verify time to first token < 1 second
- [ ] Test streaming with OpenAI (GPT-4o)
- [ ] Test streaming with Anthropic (Claude 3.5)
- [ ] Test streaming with Gemini (gemini-2.0-flash-exp)
- [ ] Test streaming with Mistral (mistral-large)
- [ ] Verify messages persist to database after streaming
- [ ] Check streaming error handling (invalid API key)
- [ ] Verify no memory leaks (check browser dev tools)

#### Comparison Mode Testing
- [ ] Configure API keys for 2+ providers
- [ ] Select 2 models from different providers
- [ ] Enter prompt: "Explain quantum computing in simple terms"
- [ ] Verify both models stream responses
- [ ] Check responses display correctly
- [ ] Vote on preferred response
- [ ] Verify vote is saved

### Cross-Browser Testing

#### Chrome/Edge (Chromium)
- [ ] All features work correctly
- [ ] No console errors
- [ ] UI renders properly
- [ ] Streaming works smoothly

#### Firefox
- [ ] All features work correctly
- [ ] No console errors
- [ ] UI renders properly
- [ ] Streaming works smoothly

#### Safari (if available)
- [ ] All features work correctly
- [ ] No console errors
- [ ] UI renders properly
- [ ] Streaming works smoothly

### Error Handling

#### Missing API Keys
- [ ] Try to chat without configuring API key
- [ ] Verify friendly error message appears
- [ ] Verify conversation ID is included in error

#### Invalid API Keys
- [ ] Configure invalid API key
- [ ] Try to send message
- [ ] Verify error is handled gracefully
- [ ] Check error message is user-friendly

#### Network Issues
- [ ] Disconnect network during model loading
- [ ] Verify error message appears
- [ ] Verify fallback behavior works
- [ ] Reconnect and verify recovery

#### Rate Limiting
- [ ] Send multiple rapid requests
- [ ] Verify rate limiting works
- [ ] Check error messages are clear

### Performance Testing

#### Model Loading Performance
- [ ] Measure time to load models on first visit
- [ ] Verify < 500ms with caching
- [ ] Check caching works (subsequent loads faster)
- [ ] Verify cache headers are set correctly

#### Chat Response Time
- [ ] Send message and measure first token time
- [ ] Verify streaming starts quickly
- [ ] Check full response completes in reasonable time

#### Comparison Performance
- [ ] Run comparison with 4 models
- [ ] Verify all streams start promptly
- [ ] Check no blocking/freezing occurs
- [ ] Verify comparison saves to database

### Security Testing

#### Authentication
- [ ] Try accessing models endpoint without auth
- [ ] Verify 401 Unauthorized response
- [ ] Try accessing with expired token
- [ ] Verify token refresh works

#### Input Validation
- [ ] Try sending empty messages
- [ ] Try sending extremely long messages
- [ ] Try invalid provider/model combinations
- [ ] Verify all inputs are validated

#### API Key Security
- [ ] Verify API keys are encrypted in database
- [ ] Check keys never appear in logs
- [ ] Verify keys not exposed in API responses
- [ ] Test key update/delete functionality

## Testing Commands

### Run All Backend Tests
```bash
cd /home/runner/work/LLMSelect/LLMSelect
python -m pytest tests/ -v
```

### Run Specific Test Suite
```bash
# Model registry tests
python -m pytest tests/test_models.py -v

# Chat tests
python -m pytest tests/test_chat.py -v

# Comparison tests
python -m pytest tests/test_comparisons.py -v
```

### Build Frontend
```bash
cd /home/runner/work/LLMSelect/LLMSelect
npm run build
```

### Run Development Server
```bash
# Backend
flask run

# Frontend (watch mode)
npm run dev
```

## Known Issues

### Non-Critical
- Bundle size warnings in webpack (expected, can optimize later)
- SQLAlchemy deprecation warnings (can update in future)

### Fixed in Phase 4
- ✅ Hardcoded model lists (now dynamic)
- ✅ Missing latest 2024 models (now included)
- ✅ test_chat_creates_and_reuses_conversation failing (now fixed)

## Test Results Summary

**Total Tests:** 22
**Passing:** 22 ✅
**Failing:** 0
**Pass Rate:** 100% 🎉

**Last Test Run:** 2025-11-04
**Status:** All tests passing

### Phase 4 Priority 4 - Chat Streaming ✨ **COMPLETED**
- ✅ Backend streaming endpoint (`POST /api/v1/chat/stream`)
- ✅ Frontend streaming hook (`useStreamingChat`)
- ✅ Streaming UI with animated cursor
- ✅ Cancel button functionality
- ✅ Message persistence after streaming
- ✅ Comprehensive test coverage
- ✅ CodeQL security scan (0 alerts)
- ✅ Code review feedback addressed

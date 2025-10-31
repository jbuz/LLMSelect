# LLMSelect - Strategic Product Backlog

**Last Updated:** October 31, 2025  
**Repository:** https://github.com/jbuz/LLMSelect  
**Status:** Phase 1 Complete ✅ | Phase 2 In Progress 🚧

---

## � Project Status Overview

### Completed ✅
- ✅ Security infrastructure (encryption, JWT, CSRF)
- ✅ Backend architecture (service layer, database, API versioning)
- ✅ Error handling and logging
- ✅ Basic authentication and API key management
- ✅ Rate limiting and input validation

### In Progress 🚧
- 🚧 Comparison mode UI implementation
- 🚧 Streaming response support
- 🚧 Frontend architecture improvements

### Not Started ⏸️
- ⏸️ Comprehensive testing suite
- ⏸️ Conversation management UI
- ⏸️ Mobile optimization
- ⏸️ Advanced features

---

## 🎯 Strategic Priorities

### **Core Value Proposition:**
Enable users to compare multiple LLM responses side-by-side from a single prompt with exceptional UX/UI.

### **Critical Gap:**
Backend comparison logic exists (`/api/v1/compare` endpoint) but frontend has no comparison mode UI.

---

## 🔴 PHASE 1: Foundation (COMPLETE ✅)

### ✅ 1. Security Infrastructure
**Priority:** P0 - Critical  
**Status:** COMPLETE  
**Duration:** 2-3 weeks  

**Completed Items:**
- ✅ Implement API key encryption at rest (Fernet)
- ✅ Add user authentication system (JWT with cookies)
- ✅ Implement rate limiting (Flask-Limiter)
- ✅ Add CSRF protection
- ✅ Input validation and sanitization
- ✅ Structured error responses

---

### ✅ 2. Backend Architecture
**Priority:** P0 - Critical  
**Status:** COMPLETE  
**Duration:** 2-3 weeks  

**Completed Items:**
- ✅ Refactor to application factory pattern
- ✅ Implement service layer (LLM, Conversations, API Keys)
- ✅ Add database models (User, APIKey, Conversation, Message)
- ✅ API versioning (`/api/v1`)
- ✅ Dependency injection via service container
- ✅ Health check endpoint

---

### ✅ 3. Error Handling & Logging
**Priority:** P0 - Critical  
**Status:** COMPLETE  
**Duration:** 1 week  

**Completed Items:**
- ✅ Comprehensive logging system
- ✅ Retry logic with exponential backoff
- ✅ Error boundaries in React
- ✅ Structured error responses
- ✅ Request/response logging

**Remaining:**
- [ ] Custom error pages (404, 500, etc.)
- [ ] Client-side error reporting (Sentry integration)

---

## 🟠 PHASE 2: Core Comparison Experience (IN PROGRESS 🚧)

### 🚧 4. Comparison Mode UI **[HIGHEST PRIORITY]**
**Priority:** P0 - CRITICAL  
**Status:** IN PROGRESS 🚧  
**Duration:** 2-3 weeks  
**Dependencies:** None  

**Why Critical:** This is the app's primary value proposition. Currently users can only chat with one model at a time, defeating the purpose of "LLMSelect".

**Tasks:**
- [ ] **Backend additions:**
  - [ ] Create `ComparisonResult` model to persist comparisons
  - [ ] Add `GET /api/v1/comparisons` endpoint (list user's comparison history)
  - [ ] Add `POST /api/v1/comparisons/:id/vote` endpoint (track preferred responses)
  - [ ] Update `/api/v1/compare` to save results to database
  
- [ ] **Frontend components:**
  - [ ] Create `ComparisonMode.js` main component
  - [ ] Create `ModelSelector.js` for multi-model selection
  - [ ] Create `ResponseCard.js` for individual model responses
  - [ ] Create `ResponseDiff.js` for highlighting differences
  - [ ] Add mode toggle in Header (Chat vs Compare)
  
- [ ] **UX features:**
  - [ ] Side-by-side response layout (2-4 models)
  - [ ] Synchronized scrolling between responses
  - [ ] Response metadata (time, tokens, cost)
  - [ ] Copy button per response
  - [ ] Vote buttons (👍/👎) per response
  - [ ] Drag-to-reorder model cards
  - [ ] Export comparison as PDF/Markdown

**Mockup:**
```
┌─────────────────────────────────────────────────┐
│ [💬 Chat] [⚖️ Compare ✓]                       │
├─────────────────────────────────────────────────┤
│ Selected: [GPT-4 ✕] [Claude 3.5 ✕] [+ Add]    │
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ Explain quantum computing in simple terms   ││
│ │                              [🔄 Compare ▶] ││
│ └─────────────────────────────────────────────┘│
│                                                 │
│ ┌──────────────────┬──────────────────────────┐│
│ │ GPT-4            │ Claude 3.5 Sonnet        ││
│ │ 🟢 1.2s · 245 tok│ 🟢 2.4s · 198 tok        ││
│ ├──────────────────┼──────────────────────────┤│
│ │ Quantum          │ Quantum computing is...  ││
│ │ computing...     │                          ││
│ │                  │                          ││
│ │ [📋] [👍] [👎]  │ [📋] [👍] [👎]          ││
│ └──────────────────┴──────────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

### 🚧 5. Streaming Responses
**Priority:** P0 - CRITICAL  
**Status:** NOT STARTED ⏸️  
**Duration:** 1 week  
**Dependencies:** None  

**Why Critical:** Without streaming, users wait 20-60 seconds staring at a blank screen. This creates a poor UX that makes the app feel broken.

**Tasks:**
- [ ] **Backend streaming:**
  - [ ] Add `POST /api/v1/chat/stream` SSE endpoint
  - [ ] Update `LLMService.invoke_stream()` for each provider
  - [ ] Implement token-by-token streaming for OpenAI
  - [ ] Implement streaming for Anthropic (Claude)
  - [ ] Implement streaming for Gemini
  - [ ] Implement streaming for Mistral
  
- [ ] **Frontend streaming:**
  - [ ] Create `useStreamingChat` custom hook
  - [ ] Implement EventSource connection
  - [ ] Add request cancellation (AbortController)
  - [ ] Show typing animation with real content
  - [ ] Handle connection errors and reconnection
  
- [ ] **Comparison streaming:**
  - [ ] Stream multiple models simultaneously
  - [ ] Show progress indicators per model
  - [ ] Handle partial failures gracefully

**Example Implementation:**
```python
# Backend
@bp.post("/chat/stream")
@jwt_required()
def chat_stream():
    def generate():
        for chunk in llm_service.invoke_stream(provider, model, messages, api_key):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
```

```javascript
// Frontend
const useStreamingChat = () => {
  const streamMessage = async (content) => {
    const eventSource = new EventSource('/api/v1/chat/stream');
    let fullResponse = '';
    
    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        eventSource.close();
        return;
      }
      
      const { chunk } = JSON.parse(event.data);
      fullResponse += chunk;
      setMessages(prev => [...prev.slice(0, -1), {
        role: 'assistant',
        content: fullResponse,
        streaming: true
      }]);
    };
  };
};
```

---

### 🚧 6. Message Rendering Improvements
**Priority:** P1 - High  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  
**Dependencies:** None  

**Tasks:**
- [ ] **Markdown rendering:**
  - [ ] Install `react-markdown` and `remark-gfm`
  - [ ] Add markdown parser to MessageList
  - [ ] Support tables, lists, links, images
  
- [ ] **Code highlighting:**
  - [ ] Install `react-syntax-highlighter`
  - [ ] Add language detection
  - [ ] Add copy button for code blocks
  - [ ] Add line numbers (optional)
  
- [ ] **Message actions:**
  - [ ] Add copy button per message
  - [ ] Add regenerate button
  - [ ] Add edit button (edit and resend)
  - [ ] Add delete button
  
- [ ] **Metadata display:**
  - [ ] Show message timestamp
  - [ ] Show token count
  - [ ] Show response time
  - [ ] Show model name

**Package additions:**
```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.5.0"
  }
}
```

---

## 🟡 PHASE 3: Frontend Architecture (WEEKS 4-5)

### 7. State Management & Component Refactor
**Priority:** P1 - High  
**Status:** NOT STARTED ⏸️  
**Duration:** 1-2 weeks  
**Dependencies:** None  

**Why Important:** Current App.js is 261 lines with complex state management. Extracting hooks and adding Context API will make the codebase maintainable.

**Tasks:**
- [ ] **Custom hooks:**
  - [ ] Create `useAuth` hook (login, logout, register, user state)
  - [ ] Create `useChat` hook (messages, sendMessage, clearChat)
  - [ ] Create `useComparison` hook (compare, results, history)
  - [ ] Create `useModels` hook (model list, selection)
  - [ ] Create `useApiKeys` hook (save, validate keys)
  
- [ ] **Context API:**
  - [ ] Create `AppContext` for global state
  - [ ] Create `AuthContext` for user/session
  - [ ] Create `ThemeContext` for dark/light mode
  
- [ ] **Component structure:**
  ```
  src/
    components/
      chat/
        ChatMode.js
        MessageList.js
        MessageItem.js
        MessageInput.js
      comparison/
        ComparisonMode.js
        ModelSelector.js
        ResponseCard.js
      common/
        Modal.js
        Button.js
        LoadingSpinner.js
    hooks/
      useAuth.js
      useChat.js
      useComparison.js
      useModels.js
    contexts/
      AppContext.js
  ```

**Example Hook:**
```javascript
// hooks/useChat.js
export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  const sendMessage = useCallback(async (content, provider, model) => {
    setIsLoading(true);
    try {
      const response = await chatApi.sendMessage({
        provider,
        model,
        messages: [...messages, { role: 'user', content }],
        conversationId
      });
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content },
        { role: 'assistant', content: response.data.response }
      ]);
      setConversationId(response.data.conversationId);
    } finally {
      setIsLoading(false);
    }
  }, [messages, conversationId]);
  
  return { messages, sendMessage, isLoading, conversationId };
};
```

---

### 8. TypeScript Migration (Optional)
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 1 week  
**Dependencies:** Component refactor (#7)  

**Tasks:**
- [ ] Add TypeScript configuration
- [ ] Convert components to `.tsx`
- [ ] Add type definitions for API responses
- [ ] Add prop types for components
- [ ] Add utility types

**Note:** This is optional but highly recommended for large applications.

---

## 🟢 PHASE 4: Testing & Quality (WEEKS 6-8)

### 9. Frontend Testing Suite
**Priority:** P1 - High  
**Status:** NOT STARTED ⏸️  
**Duration:** 1-2 weeks  
**Dependencies:** Component refactor (#7)  

**Current Coverage:** 0% ❌

**Tasks:**
- [ ] **Setup:**
  - [ ] Install Jest, React Testing Library, @testing-library/user-event
  - [ ] Configure test environment
  - [ ] Add test scripts to package.json
  
- [ ] **Component tests:**
  - [ ] MessageList component tests
  - [ ] MessageInput component tests
  - [ ] Header component tests
  - [ ] Modal component tests
  - [ ] ComparisonMode tests (when implemented)
  
- [ ] **Hook tests:**
  - [ ] useAuth tests
  - [ ] useChat tests
  - [ ] useComparison tests
  
- [ ] **Integration tests:**
  - [ ] Complete user flow tests
  - [ ] API integration tests (mocked)
  
- [ ] **Target:** 80%+ code coverage

**Example Test:**
```javascript
// components/__tests__/MessageList.test.js
import { render, screen } from '@testing-library/react';
import MessageList from '../MessageList';

describe('MessageList', () => {
  it('renders messages correctly', () => {
    const messages = [
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Hi!' }
    ];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi!')).toBeInTheDocument();
  });
  
  it('shows loading indicator', () => {
    render(<MessageList messages={[]} isLoading={true} />);
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });
});
```

---

### 10. Backend Test Coverage Expansion
**Priority:** P1 - High  
**Status:** IN PROGRESS 🚧  
**Duration:** 1 week  
**Dependencies:** None  

**Current Coverage:** ~30% (basic tests exist)  
**Target Coverage:** 90%+

**Tasks:**
- [ ] **Streaming tests:**
  - [ ] SSE endpoint tests
  - [ ] Stream error handling
  - [ ] Stream cancellation
  
- [ ] **Comparison tests:**
  - [ ] Multi-model comparison
  - [ ] Parallel execution tests
  - [ ] Timeout handling
  - [ ] Partial failure tests
  
- [ ] **Authentication tests:**
  - [ ] JWT token refresh
  - [ ] Session expiration
  - [ ] CSRF protection
  - [ ] Rate limiting enforcement
  
- [ ] **LLM service tests:**
  - [ ] Provider-specific tests
  - [ ] Retry logic tests
  - [ ] Response parsing tests
  - [ ] Error handling tests
  
- [ ] **Database tests:**
  - [ ] Conversation persistence
  - [ ] Message ordering
  - [ ] User isolation
  - [ ] API key encryption/decryption

**Example Test:**
```python
# tests/test_comparison.py
def test_compare_multiple_models(client, app, monkeypatch):
    """Test side-by-side comparison of multiple models"""
    register_and_login(client)
    
    responses = {"openai": "GPT response", "anthropic": "Claude response"}
    
    def fake_invoke(provider, model, messages, api_key):
        return responses[provider]
    
    monkeypatch.setattr(app.extensions["services"].llm, "invoke", fake_invoke)
    
    response = client.post("/api/v1/compare", json={
        "prompt": "Hello",
        "providers": [
            {"provider": "openai", "model": "gpt-4"},
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
        ]
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["openai"] == "GPT response"
    assert data["anthropic"] == "Claude response"
```

---

### 11. E2E Testing with Playwright
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  
**Dependencies:** Comparison UI (#4)  

**Tasks:**
- [ ] Install Playwright
- [ ] Configure test environment
- [ ] Write critical user flows:
  - [ ] User registration and login
  - [ ] API key configuration
  - [ ] Single model chat
  - [ ] Multi-model comparison
  - [ ] Conversation history
  - [ ] Settings management

**Example E2E Test:**
```javascript
// e2e/comparison.spec.js
import { test, expect } from '@playwright/test';

test('compare multiple models', async ({ page }) => {
  await page.goto('http://localhost:3044');
  
  // Login
  await page.click('text=Sign in');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'testpass');
  await page.click('button:has-text("Login")');
  
  // Switch to compare mode
  await page.click('button:has-text("Compare")');
  
  // Select models
  await page.click('text=Add model');
  await page.selectOption('select[name="provider"]', 'openai');
  
  // Send prompt
  await page.fill('textarea', 'Explain quantum computing');
  await page.click('button[type="submit"]');
  
  // Verify responses appear
  await expect(page.locator('.response-card').first()).toBeVisible();
});
```

---

## 🔵 PHASE 5: Conversation Management (WEEKS 7-8)

### 12. Conversation Sidebar & History
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 1 week  
**Dependencies:** None  

**Tasks:**
- [ ] **Backend:**
  - [ ] Add `GET /api/v1/conversations` endpoint
  - [ ] Add `DELETE /api/v1/conversations/:id` endpoint
  - [ ] Add `PATCH /api/v1/conversations/:id` endpoint (rename)
  - [ ] Add conversation search endpoint
  - [ ] Add pagination support
  
- [ ] **Frontend:**
  - [ ] Create ConversationSidebar component
  - [ ] Add conversation list with timestamps
  - [ ] Implement search/filter
  - [ ] Add "New conversation" button
  - [ ] Add conversation deletion
  - [ ] Add conversation renaming
  - [ ] Show active conversation indicator
  
- [ ] **UX:**
  - [ ] Collapsible sidebar (toggle)
  - [ ] Keyboard shortcuts (Ctrl+K for search)
  - [ ] Drag to reorder
  - [ ] Pin important conversations

**Mockup:**
```
┌──────────┬───────────────────────┐
│ 🔍 Search│  Current Chat         │
├──────────┤                       │
│ 📌 Pinned│                       │
│ · Conv 1 │                       │
│          │                       │
│ 📅 Today │                       │
│ · Conv 2 │                       │
│ · Conv 3 │                       │
│          │                       │
│ 📅 Yest. │                       │
│ · Conv 4 │                       │
│          │                       │
│ [+ New]  │                       │
└──────────┴───────────────────────┘
```

---

### 13. Conversation Export & Sharing
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  
**Dependencies:** Conversation sidebar (#12)  

**Tasks:**
- [ ] **Export formats:**
  - [ ] Export as Markdown
  - [ ] Export as JSON
  - [ ] Export as PDF (using jsPDF)
  - [ ] Export as HTML
  
- [ ] **Sharing (optional):**
  - [ ] Generate shareable link
  - [ ] Anonymous viewing mode
  - [ ] Expiration settings
  - [ ] Password protection

---

## ⚡ PHASE 6: Performance & Optimization (WEEKS 9-10)

### 14. Response Caching
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  
**Dependencies:** None  

**Tasks:**
- [ ] Install Redis
- [ ] Implement cache key generation (hash of prompt + model)
- [ ] Add cache lookup before API calls
- [ ] Set appropriate TTL (1 hour suggested)
- [ ] Add cache invalidation
- [ ] Add cache statistics endpoint

**Implementation:**
```python
# llmselect/services/llm.py
import hashlib
import redis

class LLMService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def invoke(self, provider, model, messages, api_key):
        # Check cache
        cache_key = self._generate_cache_key(provider, model, messages)
        cached = self.redis.get(cache_key)
        if cached:
            return cached
        
        # Call provider
        response = self._call_provider(provider, model, messages, api_key)
        
        # Cache for 1 hour
        self.redis.setex(cache_key, 3600, response)
        
        return response
```

---

### 15. Bundle Optimization & Code Splitting
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 2-3 days  
**Dependencies:** None  

**Tasks:**
- [ ] Configure webpack code splitting
- [ ] Lazy load comparison mode
- [ ] Lazy load markdown renderer
- [ ] Separate vendor bundles
- [ ] Add bundle analysis
- [ ] Optimize images and assets
- [ ] Enable gzip compression

**Webpack Config:**
```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          priority: 20
        }
      }
    }
  }
};
```

---

### 16. Performance Monitoring
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 2-3 days  
**Dependencies:** None  

**Tasks:**
- [ ] Add Web Vitals tracking
- [ ] Implement custom performance marks
- [ ] Add API response time tracking
- [ ] Track LLM provider latency
- [ ] Add error rate monitoring
- [ ] Create performance dashboard

---

## 🎨 PHASE 7: UX/UI Polish (WEEKS 10-11)

### 17. Accessibility (a11y) Improvements
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  
**Dependencies:** None  

**Tasks:**
- [ ] Add ARIA labels to all interactive elements
- [ ] Implement keyboard navigation (Tab, Arrow keys)
- [ ] Add focus indicators
- [ ] Improve color contrast (WCAG AA compliance)
- [ ] Add skip-to-content link
- [ ] Test with screen readers (NVDA, JAWS)
- [ ] Add alt text for all images
- [ ] Support reduced motion preferences

---

### 18. Mobile Responsiveness
**Priority:** P2 - Medium  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  
**Dependencies:** Comparison UI (#4)  

**Tasks:**
- [ ] Responsive comparison layout (stack on mobile)
- [ ] Touch-friendly tap targets (min 44x44px)
- [ ] Mobile-optimized sidebar (drawer)
- [ ] Swipe gestures for navigation
- [ ] Virtual keyboard handling
- [ ] Test on iOS and Android
- [ ] Add PWA support (optional)

---

### 19. Theme & Visual Polish
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 2-3 days  
**Dependencies:** None  

**Tasks:**
- [ ] Add light theme option
- [ ] Implement theme toggle
- [ ] Persist theme preference
- [ ] Add theme transition animations
- [ ] Refine color palette
- [ ] Add loading skeletons
- [ ] Improve button states (hover, active, disabled)
- [ ] Add micro-interactions

---

### 20. Keyboard Shortcuts
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 1-2 days  
**Dependencies:** None  

**Tasks:**
- [ ] Implement shortcut handler
- [ ] Add shortcuts:
  - `Ctrl/Cmd + K` - Command palette
  - `Ctrl/Cmd + N` - New conversation
  - `Ctrl/Cmd + /` - Toggle sidebar
  - `Ctrl/Cmd + Enter` - Send message
  - `Esc` - Close modals
  - `Ctrl/Cmd + ,` - Settings
- [ ] Add shortcut help modal (?)
- [ ] Persist user preferences

---

## 🚀 PHASE 8: Advanced Features (FUTURE)

### 21. Voice Input/Output
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 1 week  

**Tasks:**
- [ ] Integrate Web Speech API
- [ ] Add microphone button
- [ ] Add voice transcription
- [ ] Add text-to-speech for responses
- [ ] Handle multiple languages

---

### 22. Model Configuration Panel
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  

**Tasks:**
- [ ] Add advanced settings panel
- [ ] Temperature control
- [ ] Max tokens slider
- [ ] Top-p, frequency penalty, presence penalty
- [ ] System message customization
- [ ] Save custom presets

---

### 23. Conversation Templates
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 3-4 days  

**Tasks:**
- [ ] Create template library
- [ ] Add template categories (code, writing, analysis)
- [ ] User-created templates
- [ ] Template sharing
- [ ] Template variables

---

### 24. Cost Tracking & Analytics
**Priority:** P3 - Low  
**Status:** NOT STARTED ⏸️  
**Duration:** 1 week  

**Tasks:**
- [ ] Track token usage per provider
- [ ] Calculate costs based on pricing
- [ ] Show cost per conversation
- [ ] Monthly cost dashboard
- [ ] Set budget alerts
- [ ] Export usage reports

---

## 📅 Implementation Roadmap

### **Sprint 1 (Weeks 1-2): Comparison Core**
- ✅ Backend comparison persistence (#4)
- ✅ ComparisonMode UI component (#4)
- ✅ Multi-model selector (#4)
- ✅ Side-by-side response layout (#4)

### **Sprint 2 (Week 3): Streaming**
- ✅ Backend streaming endpoint (#5)
- ✅ Frontend EventSource integration (#5)
- ✅ Streaming UI updates (#5)

### **Sprint 3 (Weeks 4-5): Frontend Refactor**
- ✅ Extract custom hooks (#7)
- ✅ Implement Context API (#7)
- ✅ Message rendering improvements (#6)
- ✅ Markdown + syntax highlighting (#6)

### **Sprint 4 (Weeks 6-7): Testing**
- ✅ Frontend test suite (#9)
- ✅ Backend test coverage expansion (#10)
- ✅ E2E tests for critical flows (#11)

### **Sprint 5 (Week 8): Conversation Management**
- ✅ Conversation sidebar (#12)
- ✅ Conversation history (#12)
- ✅ Conversation export (#13)

### **Sprint 6 (Weeks 9-10): Performance**
- ✅ Response caching (#14)
- ✅ Bundle optimization (#15)
- ✅ Performance monitoring (#16)

### **Sprint 7 (Week 11): Polish**
- ✅ Accessibility improvements (#17)
- ✅ Mobile responsiveness (#18)
- ✅ Theme toggle (#19)
- ✅ Keyboard shortcuts (#20)

---

## 🎯 Success Metrics

### Phase 2 Success Criteria:
- ✅ Users can compare 2-4 models side-by-side
- ✅ Responses stream in real-time (< 1s to first token)
- ✅ Comparison results are persisted
- ✅ Code blocks have syntax highlighting
- ✅ Copy buttons work on all messages

### Phase 3 Success Criteria:
- ✅ App.js reduced from 261 to < 100 lines
- ✅ All state managed through custom hooks
- ✅ Components are reusable and testable

### Phase 4 Success Criteria:
- ✅ Frontend test coverage > 80%
- ✅ Backend test coverage > 90%
- ✅ E2E tests cover critical user flows
- ✅ CI/CD pipeline runs all tests

### Phase 5 Success Criteria:
- ✅ Users can view and manage conversation history
- ✅ Conversations can be searched and filtered
- ✅ Conversations can be exported in multiple formats

---

## 🔧 Technical Debt Tracking

### High Priority Debt:
- [ ] No streaming support (blocks good UX)
- [ ] Large App.js component (maintenance issue)
- [ ] Low test coverage (30% backend, 0% frontend)
- [ ] No error recovery mechanisms

### Medium Priority Debt:
- [ ] localStorage as primary storage (should be backend)
- [ ] No request cancellation
- [ ] No response caching
- [ ] Hardcoded model lists

### Low Priority Debt:
- [ ] No TypeScript
- [ ] No bundle optimization
- [ ] No PWA support
- [ ] No monitoring/observability

---

## 📊 Effort Summary

| Phase | Duration | Priority | Status |
|-------|----------|----------|--------|
| Phase 1: Foundation | 4-5 weeks | Critical | ✅ Complete |
| Phase 2: Comparison UI | 2-3 weeks | Critical | 🚧 In Progress |
| Phase 3: Frontend Refactor | 1-2 weeks | High | ⏸️ Not Started |
| Phase 4: Testing | 2 weeks | High | ⏸️ Not Started |
| Phase 5: Conversation Mgmt | 1 week | Medium | ⏸️ Not Started |
| Phase 6: Performance | 1 week | Medium | ⏸️ Not Started |
| Phase 7: UX Polish | 1 week | Medium | ⏸️ Not Started |
| Phase 8: Advanced Features | TBD | Low | ⏸️ Future |
| **Total (Phases 1-7)** | **12-16 weeks** | | **~30% Complete** |

---

## 🎉 Recent Wins

- ✅ Implemented secure authentication (JWT + CSRF)
- ✅ Added API key encryption at rest
- ✅ Refactored to clean architecture (service layer)
- ✅ Added comprehensive error handling
- ✅ Implemented rate limiting
- ✅ Created structured logging system
- ✅ Added conversation persistence
- ✅ Implemented parallel comparison backend

---

## 📞 Questions & Decisions Needed

### Open Questions:
1. **Streaming priority:** Should we implement streaming before or after comparison UI?
   - **Recommendation:** Comparison UI first (core feature), then streaming
   
2. **TypeScript migration:** Is it worth the effort?
   - **Recommendation:** Not critical, but beneficial for long-term maintenance
   
3. **Mobile strategy:** Native app or PWA?
   - **Recommendation:** Start with responsive web, add PWA later
   
4. **Caching strategy:** Redis or in-memory?
   - **Recommendation:** Redis for production, in-memory for development

### Architecture Decisions:
- ✅ Use Flask (not FastAPI) - Decision made
- ✅ Use SQLite (can migrate to Postgres) - Decision made
- ✅ Use React (not Vue/Svelte) - Decision made
- [ ] Use TypeScript or JavaScript? - **Pending**
- [ ] Use Redux or Context API? - **Recommend Context API**
- [ ] Use REST or GraphQL? - **Recommend REST (current)**

---

**Last Updated:** October 31, 2025  
**Next Review:** November 15, 2025  
**Owner:** @jbuz

---

## 📚 References

- [CODE_REVIEW_AND_RECOMMENDATIONS.md](./CODE_REVIEW_AND_RECOMMENDATIONS.md) - Detailed code review
- [README.md](./README.md) - Setup and deployment guide
- [Architecture Decision Records](./docs/adr/) - Coming soon


---

### 5. Missing Tests
**Priority:** P1 - High  
**Category:** Testing

**Issues:**
- No unit tests
- No integration tests
- No end-to-end tests
- No test coverage tracking

**Action Items:**
- [ ] Set up pytest for backend testing
- [ ] Add unit tests for all API endpoints (target: 80%+ coverage)
- [ ] Add unit tests for LLM provider functions
- [ ] Set up Jest and React Testing Library for frontend
- [ ] Add component tests for all React components
- [ ] Implement integration tests for API flows
- [ ] Add E2E tests using Playwright or Cypress
- [ ] Set up CI/CD pipeline with automated testing
- [ ] Add code coverage reporting (codecov or similar)

---

### 6. Performance Issues
**Priority:** P1 - High  
**Category:** Performance

**Issues:**
- No response streaming for LLM responses
- No caching mechanism
- All messages stored in localStorage (can grow indefinitely)
- No pagination for long conversations
- Concurrent API calls in compare mode not optimized

**Action Items:**
- [ ] Implement Server-Sent Events (SSE) for streaming responses
- [ ] Add Redis caching for frequently used responses
- [ ] Implement conversation pagination/virtualization
- [ ] Add message limit and cleanup in localStorage
- [ ] Optimize bundle size (code splitting, lazy loading)
- [ ] Add service worker for offline support
- [ ] Implement request deduplication
- [ ] Add CDN for static assets

---

### 7. State Management
**Priority:** P1 - High  
**Category:** Frontend Architecture

**Issues:**
- Props drilling in React components
- No global state management solution
- localStorage used as primary data store
- No optimistic updates
- State not synchronized across tabs

**Action Items:**
- [ ] Implement Context API or Redux for state management
- [ ] Create custom hooks for common functionality
- [ ] Add optimistic UI updates
- [ ] Implement proper data persistence strategy
- [ ] Add broadcast channel for cross-tab communication
- [ ] Implement undo/redo functionality

---

## 🟡 Medium Priority Issues

### 8. User Experience Improvements
**Priority:** P2 - Medium  
**Category:** UX/UI

**Issues:**
- No conversation history/management
- Can't edit or delete messages
- No message copying functionality
- No syntax highlighting for code blocks
- No markdown rendering
- No file upload support
- No conversation search
- No keyboard shortcuts

**Action Items:**
- [ ] Add conversation sidebar with history
- [ ] Implement message editing and deletion
- [ ] Add "Copy to clipboard" button for messages
- [ ] Integrate markdown parser (marked.js or react-markdown)
- [ ] Add syntax highlighting (Prism.js or highlight.js)
- [ ] Implement file upload for images/documents
- [ ] Add conversation search functionality
- [ ] Implement keyboard shortcuts (Ctrl+K for commands, etc.)
- [ ] Add message reactions/ratings
- [ ] Implement conversation export (PDF, Markdown, JSON)
- [ ] Add dark/light theme toggle (already dark, add light option)

---

### 9. Model Management
**Priority:** P2 - Medium  
**Category:** Features

**Issues:**
- Hardcoded model lists in frontend
- No model capabilities information
- Can't adjust model parameters (temperature, max_tokens, etc.)
- No token usage tracking
- No cost estimation

**Action Items:**
- [ ] Create backend endpoint to fetch available models
- [ ] Add model information cards (capabilities, pricing, limits)
- [ ] Implement advanced settings panel:
  - Temperature control
  - Max tokens slider
  - Top-p, frequency penalty, presence penalty
  - System message customization
- [ ] Add token counter for messages
- [ ] Implement cost tracking and estimation
- [ ] Add model comparison features
- [ ] Support for custom model endpoints (Azure OpenAI, etc.)

---

### 10. Accessibility (a11y)
**Priority:** P2 - Medium  
**Category:** Accessibility

**Issues:**
- Missing ARIA labels
- No keyboard navigation support
- Insufficient color contrast in some areas
- No screen reader optimization
- Missing focus indicators

**Action Items:**
- [ ] Add proper ARIA labels to all interactive elements
- [ ] Implement full keyboard navigation
- [ ] Audit and fix color contrast issues
- [ ] Add skip-to-content links
- [ ] Implement focus trap in modals
- [ ] Add screen reader announcements for dynamic content
- [ ] Test with screen readers (NVDA, JAWS, VoiceOver)
- [ ] Add reduced motion support

---

### 11. Documentation
**Priority:** P2 - Medium  
**Category:** Documentation

**Issues:**
- Minimal README documentation
- No API documentation
- No architecture documentation
- No contribution guidelines
- No deployment guide

**Action Items:**
- [ ] Expand README with:
  - Feature overview with screenshots
  - Detailed setup instructions
  - Troubleshooting guide
  - FAQ section
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Add architecture decision records (ADRs)
- [ ] Create CONTRIBUTING.md
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Create deployment guide for various platforms
- [ ] Add JSDoc/docstrings to all functions
- [ ] Create developer onboarding guide

---

### 12. Mobile Responsiveness
**Priority:** P2 - Medium  
**Category:** UI/UX

**Issues:**
- Limited mobile optimization
- No PWA support
- Touch interactions not optimized
- Small tap targets on mobile

**Action Items:**
- [ ] Enhance mobile layout and spacing
- [ ] Add PWA manifest and service worker
- [ ] Implement pull-to-refresh
- [ ] Optimize touch interactions (swipe gestures)
- [ ] Increase tap target sizes (minimum 44x44px)
- [ ] Add mobile-specific features (voice input)
- [ ] Test on various mobile devices and screen sizes

---

## 🟢 Low Priority / Nice-to-Have

### 13. Advanced Features
**Priority:** P3 - Low  
**Category:** Features

**Action Items:**
- [ ] Multi-language support (i18n)
- [ ] Voice input/output integration
- [ ] Image generation support (DALL-E, Midjourney)
- [ ] Plugin/extension system
- [ ] Conversation sharing functionality
- [ ] Collaborative editing
- [ ] Conversation templates/prompts library
- [ ] Integration with third-party tools (Notion, Slack, etc.)
- [ ] Analytics dashboard
- [ ] A/B testing framework for prompts
- [ ] Conversation branching (explore alternate responses)
- [ ] Multi-modal support (images, audio)

---

### 14. Developer Experience
**Priority:** P3 - Low  
**Category:** DevEx

**Action Items:**
- [ ] Add pre-commit hooks (Husky)
- [ ] Set up ESLint and Prettier
- [ ] Add Python linting (Black, flake8, mypy)
- [ ] Implement hot module replacement (HMR) for development
- [ ] Add development proxy configuration
- [ ] Create development seed data
- [ ] Add debugging configurations for VS Code
- [ ] Implement feature flags system
- [ ] Add performance monitoring (Sentry, DataDog)

---

### 15. Infrastructure & DevOps
**Priority:** P3 - Low  
**Category:** DevOps

**Action Items:**
- [ ] Set up proper CI/CD pipeline (GitHub Actions)
- [ ] Add automated dependency updates (Dependabot)
- [ ] Implement blue-green deployment
- [ ] Add monitoring and alerting (Prometheus, Grafana)
- [ ] Set up centralized logging (ELK stack)
- [ ] Add backup and disaster recovery procedures
- [ ] Implement auto-scaling configuration
- [ ] Add security scanning (Snyk, OWASP ZAP)
- [ ] Create infrastructure as code (Terraform/CloudFormation)

---

## 🎨 Proposed UI/UX Redesign

### Modern Interface Enhancements

#### 1. Conversation Management Sidebar
**Description:** Add a collapsible sidebar for managing multiple conversations

**Features:**
- Recent conversations list with timestamps
- Search/filter conversations
- Folder/tag organization
- Pin important conversations
- Bulk actions (delete, archive, export)

**Mockup Concept:**
```
┌─────────────┬──────────────────────────────┐
│ [☰] Convos  │  [🤖] Chat Header           │
├─────────────┼──────────────────────────────┤
│ 🔍 Search   │                              │
│             │                              │
│ 📌 Pinned   │      Messages Area           │
│ └─ Conv1    │                              │
│             │                              │
│ 📅 Today    │                              │
│ └─ Conv2    │                              │
│ └─ Conv3    │                              │
│             │                              │
│ 📅 Yesterd. │                              │
│             │                              │
│ [+ New]     │  [Input Area              ] │
└─────────────┴──────────────────────────────┘
```

---

#### 2. Advanced Model Selector
**Description:** Replace dropdown with a rich model selector card interface

**Features:**
- Visual cards for each model with logo/icon
- Quick stats (speed, quality, cost per 1K tokens)
- Real-time availability indicator
- Recently used models
- Favorites system
- Model comparison view

**Visual Approach:**
```
┌─────────────────────────────────────┐
│  Select AI Model                    │
├─────────────────────────────────────┤
│                                     │
│  ⭐ Favorites                       │
│  [GPT-4]  [Claude 3.5]  [Gemini]   │
│                                     │
│  🚀 All Models                      │
│                                     │
│  ┌─────────┐  ┌─────────┐          │
│  │ 🟢 GPT-4│  │ 🟢 Claude│          │
│  │ ★★★★★   │  │ ★★★★☆    │          │
│  │ Fast    │  │ Creative │          │
│  │ $0.03/1K│  │ $0.015/1K│          │
│  └─────────┘  └─────────┘          │
└─────────────────────────────────────┘
```

---

#### 3. Message Enhancements
**Description:** Richer message interactions and formatting

**Features:**
- Message timestamps (show on hover)
- Edit/Delete/Copy/Regenerate buttons
- Code block copy button with language detection
- Collapsible code blocks for long code
- LaTeX rendering for math equations
- Mermaid diagram support
- Table formatting
- Quote/citation support
- Message reactions (👍 👎)
- Token count per message

---

#### 4. Quick Actions Panel
**Description:** Command palette for power users

**Features:**
- Keyboard shortcut: `Ctrl/Cmd + K`
- Quick access to:
  - Switch models
  - Load conversation templates
  - Export conversation
  - Settings
  - Clear chat
  - Toggle features

**Visual:**
```
┌────────────────────────────────────┐
│ 🔍 Search commands...              │
├────────────────────────────────────┤
│ 💬 New conversation                │
│ 🔄 Switch model to...              │
│ 📤 Export conversation             │
│ ⚙️  Settings                       │
│ 🗑️  Clear chat                     │
│ 📋 Load template                   │
└────────────────────────────────────┘
```

---

#### 5. Response Quality Indicators
**Description:** Visual feedback on response quality and metadata

**Features:**
- Response time indicator
- Token usage display
- Confidence/quality score (if available)
- Source citations (for RAG implementations)
- Warning badges for potential issues

---

#### 6. Split View for Comparison
**Description:** Enhanced comparison mode with side-by-side responses

**Features:**
- Split screen for comparing 2-4 models simultaneously
- Synchronized scrolling
- Difference highlighting
- Vote for best response
- Export comparison report

**Layout:**
```
┌──────────────┬──────────────┐
│   GPT-4      │  Claude 3.5  │
│              │              │
│  Response... │  Response... │
│              │              │
│  [👍 👎 📋]  │  [👍 👎 📋]  │
└──────────────┴──────────────┘
```

---

#### 7. Settings Panel
**Description:** Comprehensive settings with visual controls

**Categories:**
- **Appearance:** Theme, font size, message density
- **Behavior:** Auto-save, notifications, sound effects
- **Privacy:** Data retention, telemetry
- **API Keys:** Secure key management with validation
- **Advanced:** Model parameters, debug mode

---

#### 8. Onboarding Experience
**Description:** Smooth first-time user experience

**Features:**
- Welcome tour with interactive tooltips
- Quick start guide
- Sample prompts/templates
- Video tutorials
- API key setup wizard

---

#### 9. Status Bar
**Description:** Persistent bottom status bar with useful information

**Features:**
- Connection status
- Current model indicator
- Token usage counter
- Cost tracker (session/total)
- Background task indicators

---

#### 10. Prompt Templates Library
**Description:** Pre-built prompt templates for common use cases

**Categories:**
- Code Generation
- Writing & Editing
- Analysis & Research
- Creative Writing
- Business & Productivity
- Custom (user-created)

---

## 🔧 Code Quality Improvements

### Backend Refactoring

#### File: `app.py`
**Current Issues:**
- All code in single file
- No error handling classes
- Magic strings and numbers
- No type hints
- No docstrings

**Proposed Structure:**
```python
# app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    
    # Register blueprints
    from app.routes import chat_bp, keys_bp
    app.register_blueprint(chat_bp, url_prefix='/api/v1')
    app.register_blueprint(keys_bp, url_prefix='/api/v1')
    
    return app

# app/config.py
import os
from typing import Dict

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # API Configuration
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 1000))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = "100 per hour"
    
    # LLM Provider Endpoints
    LLM_ENDPOINTS: Dict[str, str] = {
        'openai': 'https://api.openai.com/v1/chat/completions',
        'anthropic': 'https://api.anthropic.com/v1/messages',
        'mistral': 'https://api.mistral.ai/v1/chat/completions',
    }

# app/services/llm_service.py
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    @abstractmethod
    def chat(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Send chat request to LLM provider"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation"""
    
    def chat(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Send chat request to OpenAI"""
        response = self.session.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', 1000),
                'temperature': kwargs.get('temperature', 0.7),
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

# app/models/message.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    """Message model"""
    role: str
    content: str
    timestamp: datetime
    model: Optional[str] = None
    tokens: Optional[int] = None
    
    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'model': self.model,
            'tokens': self.tokens
        }
```

---

### Frontend Refactoring

#### Component Structure
**Current Issues:**
- Large App.js component
- No custom hooks
- Duplicated logic
- No proper TypeScript types

**Proposed Improvements:**

```javascript
// hooks/useChat.js
import { useState, useCallback } from 'react';
import { chatApi } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (content, provider, model) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await chatApi.sendMessage({
        provider,
        model,
        messages: [...messages, { role: 'user', content }]
      });
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content },
        { role: 'assistant', content: response.data.response }
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages
  };
};

// services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

// Add request interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    // Handle different error types
    if (error.response) {
      throw new Error(error.response.data.error || 'Server error');
    } else if (error.request) {
      throw new Error('Network error. Please check your connection.');
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
);

export const chatApi = {
  sendMessage: (data) => api.post('/chat', data),
  compareModels: (data) => api.post('/compare', data),
};

export const keysApi = {
  save: (keys) => api.post('/keys', keys),
  get: () => api.get('/keys'),
};

// contexts/AppContext.js
import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [theme, setTheme] = useState('dark');

  return (
    <AppContext.Provider value={{
      selectedProvider,
      setSelectedProvider,
      selectedModel,
      setSelectedModel,
      theme,
      setTheme
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
```

---

## 📊 Technical Debt Summary

### Estimated Effort

| Priority | Total Items | Est. Time |
|----------|-------------|-----------|
| P0 - Critical | 3 items | 2-3 weeks |
| P1 - High | 4 items | 4-6 weeks |
| P2 - Medium | 6 items | 6-8 weeks |
| P3 - Low | 3 items | 3-4 weeks |
| **Total** | **16 categories** | **15-21 weeks** |

---

## 🎯 Recommended Implementation Order

### Phase 1: Foundation & Security (Weeks 1-4)
1. Security vulnerabilities (#1)
2. Error handling & logging (#2)
3. Environment configuration (#3)
4. Testing setup (#5)

### Phase 2: Architecture & Performance (Weeks 5-9)
1. API design refactoring (#4)
2. Performance improvements (#6)
3. State management (#7)
4. Documentation (#11)

### Phase 3: User Experience (Weeks 10-14)
1. UX improvements (#8)
2. Model management (#9)
3. Accessibility (#10)
4. Mobile responsiveness (#12)

### Phase 4: Polish & Advanced Features (Weeks 15-21)
1. UI/UX redesign implementation
2. Advanced features (#13)
3. Developer experience (#14)
4. Infrastructure (#15)

---

## 📝 Notes

- This backlog should be revisited quarterly
- Priority levels may change based on user feedback
- Each item should be broken down into smaller tickets for implementation
- Consider creating GitHub issues from this backlog
- Use feature flags for gradual rollout of major changes

---

**Last Updated:** October 21, 2025  
**Next Review:** January 21, 2026


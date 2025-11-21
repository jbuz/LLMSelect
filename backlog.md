# LLMSelect - Strategic Product Backlog

**Last Updated:** November 9, 2025  
**Repository:** https://github.com/jbuz/LLMSelect  
**Status:** Phase 1-5 ✅ COMPLETE | Phase 6-7 ⏸️ NOT STARTED

---

## 📊 Project Status Overview

### Completed ✅
- ✅ **Phase 1**: Security infrastructure (encryption, JWT, CSRF)
- ✅ **Phase 1**: Backend architecture (service layer, database, API versioning)
- ✅ **Phase 1**: Error handling and logging
- ✅ **Phase 1**: Basic authentication and API key management
- ✅ **Phase 1**: Rate limiting and input validation
- ✅ **Phase 2**: Comparison mode UI with side-by-side display
- ✅ **Phase 2**: Comparison result persistence and history
- ✅ **Phase 2**: Multi-model selector (2-4 models)
- ✅ **Phase 2**: Vote/preference tracking
- ✅ **Phase 3**: Real-time streaming for all providers (OpenAI, Anthropic, Gemini, Mistral)
- ✅ **Phase 3**: Parallel multi-model streaming in comparison mode
- ✅ **Phase 3**: Markdown rendering with syntax highlighting (277+ languages)
- ✅ **Phase 3**: Comparison history UI component with pagination
- ✅ **Phase 4**: Azure AI Foundry routing for unified billing
- ✅ **Phase 4**: Testing infrastructure documentation and framework
- ✅ **Phase 5**: Database performance optimization (indexes, connection pooling, eager loading)
- ✅ **Phase 5**: Response caching (Flask-Caching, model registry, conversations)
- ✅ **Phase 5**: Performance monitoring (request timing, slow query logging)

### Not Started ⏸️
- ⏸️ **Phase 6**: Frontend architecture refactor (custom hooks, Context API)
- ⏸️ **Phase 6**: Conversation management UI (sidebar, search, management)
- ⏸️ **Phase 6**: Multimodal support - vision input (image upload & analysis)
- ⏸️ **Phase 7**: Mobile optimization and responsive design enhancements
- ⏸️ **Phase 7**: Accessibility features (ARIA, keyboard navigation)
- ⏸️ **Phase 8**: Advanced features (export, voice input, analytics)

---

## 🎯 Strategic Priorities

### **Core Value Proposition:**
Enable users to compare multiple LLM responses side-by-side from a single prompt with exceptional UX/UI.

### **Current Focus:**
Phase 5 complete! Ready for Phase 6: Frontend architecture refactor with custom hooks and Context API.

---

## 🔴 PHASE 1: Foundation (COMPLETE ✅)

### ✅ 1. Security Infrastructure
**Priority:** P0 - Critical  

**Status:** COMPLETE  

---**Duration:** 2-3 weeks  



## 🔴 PHASE 1: Foundation (COMPLETE ✅)**Completed Items:**

- ✅ Implement API key encryption at rest (Fernet)

### ✅ 1. Security Infrastructure- ✅ Add user authentication system (JWT with cookies)

**Priority:** P0 - Critical  - ✅ Implement rate limiting (Flask-Limiter)

**Status:** COMPLETE ✅  - ✅ Add CSRF protection

**Completed:** October 2025- ✅ Input validation and sanitization

- ✅ Structured error responses

**Delivered:**

- ✅ API key encryption at rest (Fernet)---

- ✅ JWT authentication with secure HTTP-only cookies

- ✅ Rate limiting (Flask-Limiter, 60 req/min default)### ✅ 2. Backend Architecture

- ✅ CSRF protection**Priority:** P0 - Critical  

- ✅ Input validation and sanitization (Marshmallow schemas)**Status:** COMPLETE  

- ✅ Structured error responses with no sensitive data exposure**Duration:** 2-3 weeks  



---**Completed Items:**

- ✅ Refactor to application factory pattern

### ✅ 2. Backend Architecture- ✅ Implement service layer (LLM, Conversations, API Keys)

**Priority:** P0 - Critical  - ✅ Add database models (User, APIKey, Conversation, Message)

**Status:** COMPLETE ✅  - ✅ API versioning (`/api/v1`)

**Completed:** October 2025- ✅ Dependency injection via service container

- ✅ Health check endpoint

**Delivered:**

- ✅ Application factory pattern---

- ✅ Service layer architecture (LLM, Conversations, API Keys, Comparisons)

- ✅ Database models (User, APIKey, Conversation, Message, ComparisonResult)### ✅ 3. Error Handling & Logging

- ✅ API versioning (`/api/v1`)**Priority:** P0 - Critical  

- ✅ Dependency injection via service container**Status:** COMPLETE  

- ✅ Health check endpoint (`/api/v1/health`)**Duration:** 1 week  



---**Completed Items:**

- ✅ Comprehensive logging system

### ✅ 3. Error Handling & Logging- ✅ Retry logic with exponential backoff

**Priority:** P0 - Critical  - ✅ Error boundaries in React

**Status:** COMPLETE ✅  - ✅ Structured error responses

**Completed:** October 2025- ✅ Request/response logging



**Delivered:****Remaining:**

- ✅ Comprehensive logging system with structured logs- [ ] Custom error pages (404, 500, etc.)

- ✅ Retry logic with exponential backoff for LLM API calls- [ ] Client-side error reporting (Sentry integration)

- ✅ Error boundaries in React

- ✅ Structured error responses---

- ✅ Request/response logging

## 🟠 PHASE 2: Core Comparison Experience (IN PROGRESS 🚧)

**Remaining:**

- [ ] Custom error pages (404, 500, etc.)### 🚧 4. Comparison Mode UI **[HIGHEST PRIORITY]**

- [ ] Client-side error reporting (Sentry integration)**Priority:** P0 - CRITICAL  

**Status:** IN PROGRESS 🚧  

---**Duration:** 2-3 weeks  

**Dependencies:** None  

## 🟢 PHASE 2: Core Comparison Experience (COMPLETE ✅)

**Why Critical:** This is the app's primary value proposition. Currently users can only chat with one model at a time, defeating the purpose of "LLMSelect".

### ✅ 4. Comparison Mode UI

**Priority:** P0 - CRITICAL  **Tasks:**

**Status:** COMPLETE ✅  - [ ] **Backend additions:**

**Completed:** October-November 2025  - [ ] Create `ComparisonResult` model to persist comparisons

  - [ ] Add `GET /api/v1/comparisons` endpoint (list user's comparison history)

**Delivered:**  - [ ] Add `POST /api/v1/comparisons/:id/vote` endpoint (track preferred responses)

- ✅ **Backend:**  - [ ] Update `/api/v1/compare` to save results to database

  - ComparisonResult model for persistence  

  - `GET /api/v1/comparisons` endpoint (list user's comparison history)- [ ] **Frontend components:**

  - `POST /api/v1/comparisons/:id/vote` endpoint (track preferred responses)  - [ ] Create `ComparisonMode.js` main component

  - Updated `/api/v1/compare` to save results to database  - [ ] Create `ModelSelector.js` for multi-model selection

  - `POST /api/v1/compare/stream` for real-time streaming  - [ ] Create `ResponseCard.js` for individual model responses

    - [ ] Create `ResponseDiff.js` for highlighting differences

- ✅ **Frontend Components:**  - [ ] Add mode toggle in Header (Chat vs Compare)

  - ComparisonMode.js main component with mode toggle  

  - ModelSelector.js for multi-model selection (2-4 models)- [ ] **UX features:**

  - ResponseCard.js for individual model responses with metadata  - [ ] Side-by-side response layout (2-4 models)

  - ComparisonHistory.js for browsing past comparisons  - [ ] Synchronized scrolling between responses

    - [ ] Response metadata (time, tokens, cost)

- ✅ **UX Features:**  - [ ] Copy button per response

  - Side-by-side response layout (responsive grid)  - [ ] Vote buttons (👍/👎) per response

  - Response metadata (time, tokens, estimated cost)  - [ ] Drag-to-reorder model cards

  - Copy button per response  - [ ] Export comparison as PDF/Markdown

  - Vote buttons (👍/👎) per response

  - Color-coded model chips**Mockup:**

  - Empty states and loading indicators```

  - Error handling per provider┌─────────────────────────────────────────────────┐

│ [💬 Chat] [⚖️ Compare ✓]                       │

---├─────────────────────────────────────────────────┤

│ Selected: [GPT-4 ✕] [Claude 3.5 ✕] [+ Add]    │

### ✅ 5. Streaming Responses│                                                 │

**Priority:** P0 - CRITICAL  │ ┌─────────────────────────────────────────────┐│

**Status:** COMPLETE ✅  │ │ Explain quantum computing in simple terms   ││

**Completed:** November 2025│ │                              [🔄 Compare ▶] ││

│ └─────────────────────────────────────────────┘│

**Delivered:**│                                                 │

- ✅ **Backend Streaming:**│ ┌──────────────────┬──────────────────────────┐│

  - `POST /api/v1/compare/stream` SSE endpoint│ │ GPT-4            │ Claude 3.5 Sonnet        ││

  - `LLMService.invoke_stream()` for all providers│ │ 🟢 1.2s · 245 tok│ 🟢 2.4s · 198 tok        ││

  - Token-by-token streaming for OpenAI│ ├──────────────────┼──────────────────────────┤│

  - Streaming for Anthropic (Claude)│ │ Quantum          │ Quantum computing is...  ││

  - Streaming for Google Gemini│ │ computing...     │                          ││

  - Streaming for Mistral AI│ │                  │                          ││

  - ThreadPoolExecutor for parallel streaming│ │ [📋] [👍] [👎]  │ [📋] [👍] [👎]          ││

  │ └──────────────────┴──────────────────────────┘│

- ✅ **Frontend Streaming:**└─────────────────────────────────────────────────┘

  - `useStreamingComparison` custom hook```

  - Fetch API with ReadableStream for SSE parsing

  - Request cancellation (AbortController)---

  - Real-time typing animation with content

  - Connection error handling### 🚧 5. Streaming Responses

  **Priority:** P0 - CRITICAL  

- ✅ **Comparison Streaming:****Status:** NOT STARTED ⏸️  

  - Stream multiple models simultaneously**Duration:** 1 week  

  - Progress indicators per model (⚡ icon)**Dependencies:** None  

  - Blinking cursor during streaming

  - Partial failure handling (per-provider isolation)**Why Critical:** Without streaming, users wait 20-60 seconds staring at a blank screen. This creates a poor UX that makes the app feel broken.



**Performance Achieved:****Tasks:**

- Time to first token: < 1 second (previously 20-60 seconds)- [ ] **Backend streaming:**

- No blocking between providers  - [ ] Add `POST /api/v1/chat/stream` SSE endpoint

- Progressive rendering as chunks arrive  - [ ] Update `LLMService.invoke_stream()` for each provider

  - [ ] Implement token-by-token streaming for OpenAI

---  - [ ] Implement streaming for Anthropic (Claude)

  - [ ] Implement streaming for Gemini

### ✅ 6. Message Rendering Improvements  - [ ] Implement streaming for Mistral

**Priority:** P1 - High    

**Status:** COMPLETE ✅  - [ ] **Frontend streaming:**

**Completed:** November 2025  - [ ] Create `useStreamingChat` custom hook

  - [ ] Implement EventSource connection

**Delivered:**  - [ ] Add request cancellation (AbortController)

- ✅ **Markdown Rendering:**  - [ ] Show typing animation with real content

  - MarkdownMessage component with react-markdown  - [ ] Handle connection errors and reconnection

  - GitHub Flavored Markdown support (remark-gfm)  

  - Tables, lists, links, images, task lists- [ ] **Comparison streaming:**

    - [ ] Stream multiple models simultaneously

- ✅ **Code Highlighting:**  - [ ] Show progress indicators per model

  - react-syntax-highlighter with Prism  - [ ] Handle partial failures gracefully

  - 277+ programming languages supported

  - VS Code Dark Plus theme**Example Implementation:**

  - Copy button for code blocks with visual feedback```python

  - Inline code styling# Backend

  @bp.post("/chat/stream")

- ✅ **Message Actions:**@jwt_required()

  - Copy button per message in ResponseCarddef chat_stream():

  - Timestamp display    def generate():

  - Token count display        for chunk in llm_service.invoke_stream(provider, model, messages, api_key):

  - Response time display            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

  - Model name display        yield "data: [DONE]\n\n"

    

**Dependencies Added:**    return Response(stream_with_context(generate()), mimetype='text/event-stream')

- `react-markdown` ^9.0.1```

- `remark-gfm` ^4.0.0

- `react-syntax-highlighter` ^15.5.0```javascript

// Frontend

---const useStreamingChat = () => {

  const streamMessage = async (content) => {

## 🟢 PHASE 3: Real-Time Experience (COMPLETE ✅)    const eventSource = new EventSource('/api/v1/chat/stream');

    let fullResponse = '';

All Phase 3 items delivered in November 2025. See Phase 2 sections above for streaming (#5) and markdown rendering (#6) details.    

    eventSource.onmessage = (event) => {

**Additional Deliverables:**      if (event.data === '[DONE]') {

- ✅ Comparison history UI (#12 partial)        eventSource.close();

- ✅ Streaming architecture documentation        return;

- ✅ Testing checklist for manual validation      }

      

---      const { chunk } = JSON.parse(event.data);

      fullResponse += chunk;

## 🔵 AZURE INTEGRATION (COMPLETE ✅)      setMessages(prev => [...prev.slice(0, -1), {

        role: 'assistant',

### ✅ Azure AI Foundry Support        content: fullResponse,

**Priority:** P1 - High          streaming: true

**Status:** COMPLETE ✅        }]);

**Completed:** January 2025    };

  };

**Delivered:**};

- ✅ Configuration layer with Azure-specific settings```

- ✅ Unified routing through Azure endpoint

- ✅ Support for 14 model deployments across 4 providers---

- ✅ Deployment name mappings with environment variable overrides

- ✅ Streaming support through Azure (SSE)### 🚧 6. Message Rendering Improvements

- ✅ Fallback to direct provider APIs when Azure is disabled**Priority:** P1 - High  

- ✅ Comprehensive documentation (3 guides, 1200+ lines)**Status:** NOT STARTED ⏸️  

**Duration:** 3-4 days  

**Files Modified:****Dependencies:** None  

- `llmselect/config.py` - Azure configuration variables

- `llmselect/services/llm.py` - Azure routing methods**Tasks:**

- `llmselect/container.py` - Azure config injection- [ ] **Markdown rendering:**

- `.env.example` - Azure environment variables  - [ ] Install `react-markdown` and `remark-gfm`

  - [ ] Add markdown parser to MessageList

**Documentation Created:**  - [ ] Support tables, lists, links, images

- `AZURE_FOUNDRY_SETUP.md` (350+ lines)  

- `AZURE_INTEGRATION_GUIDE.md` (400+ lines)- [ ] **Code highlighting:**

- `AZURE_IMPLEMENTATION_SUMMARY.md` (500+ lines)  - [ ] Install `react-syntax-highlighter`

- `AZURE_QUICK_REFERENCE.md`  - [ ] Add language detection

  - [ ] Add copy button for code blocks

---  - [ ] Add line numbers (optional)

  

## 🟡 PHASE 4: Testing & Documentation (COMPLETE ✅)

### ✅ 10. Testing Infrastructure Documentation
**Priority:** P1 - High  
**Status:** COMPLETE ✅  
**Completed:** November 2025  

**Delivered:**
- ✅ Comprehensive testing documentation (SUPERPROMPT_PHASE4_TESTING.md)
- ✅ Testing strategy and framework setup guides
- ✅ 50+ test examples covering streaming, caching, comparisons
- ✅ GitHub Copilot testing prompt (GITHUB_COPILOT_TESTING_PROMPT.md)
- ✅ Testing infrastructure summary and roadmap

### ✅ 11. Azure AI Foundry Integration
**Priority:** P0 - Critical  
**Status:** COMPLETE ✅  
**Completed:** November 2025  

**Delivered:**
- ✅ Azure AI Foundry routing for unified billing
- ✅ Multi-deployment support (swedencentral, canadaeast)
- ✅ Azure integration documentation
- ✅ Seamless provider routing through Azure

---

## 🟠 PHASE 5: Database Performance & Caching (IN PROGRESS 🚧)

**Current Phase** - See SUPERPROMPT_PHASE5_DATABASE_CACHING.md for detailed implementation guide

### 🚧 12. Database Optimization
**Priority:** P0 - Critical  
**Status:** IN PROGRESS 🚧  
**Duration:** 3-5 days  
**Dependencies:** None  

**Tasks:**
- [ ] Add database indexes
  - [ ] Index on `conversations.user_id` + `created_at`
  - [ ] Index on `messages.conversation_id`
  - [ ] Index on `api_keys.user_id` + `provider`
  - [ ] Index on `comparison_results.user_id` + `created_at`
- [ ] Implement connection pooling (SQLAlchemy)
  - [ ] Configure pool size (10-20 connections)
  - [ ] Set pool timeout (30 seconds)
  - [ ] Enable pool pre-ping
- [ ] Optimize query patterns
  - [ ] Use `joinedload` for eager loading
  - [ ] Implement cursor-based pagination
  - [ ] Add query result counting optimization
- [ ] Add slow query logging (> 100ms)

**Acceptance Criteria:**
- Common queries execute in < 50ms
- No N+1 query issues
- Connection pool handles concurrent requests

---

### 🚧 13. Response Caching
**Priority:** P0 - Critical  
**Status:** IN PROGRESS 🚧  
**Duration:** 2-3 days  
**Dependencies:** None  

**Tasks:**
- [ ] Implement Flask-Caching with in-memory cache (SimpleCache)
- [ ] Cache model registry (24-hour TTL)
  - [ ] Cache OpenAI models
  - [ ] Cache Anthropic models  
  - [ ] Cache Google models
  - [ ] Cache Mistral models
  - [ ] Add cache invalidation endpoint
- [ ] Cache conversation lists (5-minute TTL)
  - [ ] Cache user's conversation list
  - [ ] Invalidate on new conversation/message
  - [ ] Add cache headers to responses
- [ ] Cache API responses
  - [ ] Add ETags for conditional requests
  - [ ] Set proper cache control headers
  - [ ] Implement response caching decorator

**Acceptance Criteria:**
- Model registry external API calls reduced by >90%
- Conversation list load times improved by >70%
- Cache hit rate >80% for repeated queries
- Proper cache invalidation on mutations

---

## 🟡 PHASE 6: Frontend Architecture & UX (NOT STARTED ⏸️)

  - [ ] Add copy button per message

### 🚧 7. Database & Backend Performance  - [ ] Add regenerate button

**Priority:** P1 - High    - [ ] Add edit button (edit and resend)

**Status:** NOT STARTED ⏸️    - [ ] Add delete button

**Duration:** 3-5 days  

- [ ] **Metadata display:**

**Tasks:**  - [ ] Show message timestamp

- [ ] Add database indexes  - [ ] Show token count

  - [ ] Index on `conversations.user_id` + `created_at`  - [ ] Show response time

  - [ ] Index on `messages.conversation_id`  - [ ] Show model name

  - [ ] Index on `api_keys.user_id` + `provider`

  - [ ] Index on `comparison_results.user_id` + `created_at`**Package additions:**

- [ ] Implement connection pooling (SQLAlchemy)```json

  - [ ] Configure pool size (10-20 connections){

  - [ ] Set pool timeout (30 seconds)  "dependencies": {

  - [ ] Enable pool pre-ping    "react-markdown": "^9.0.0",

- [ ] Optimize query patterns    "remark-gfm": "^4.0.0",

  - [ ] Use `joinedload` for eager loading    "react-syntax-highlighter": "^15.5.0"

  - [ ] Implement cursor-based pagination  }

  - [ ] Add query result counting optimization}

- [ ] Add slow query logging (> 100ms)```



**Acceptance Criteria:**---

- Common queries execute in < 50ms

- No N+1 query issues## 🟡 PHASE 3: Frontend Architecture (WEEKS 4-5)

- Connection pool handles concurrent requests

### 7. State Management & Component Refactor

---**Priority:** P1 - High  

**Status:** NOT STARTED ⏸️  

### 🚧 8. Response Caching**Duration:** 1-2 weeks  

**Priority:** P1 - High  **Dependencies:** None  

**Status:** NOT STARTED ⏸️  

**Duration:** 2-3 days**Why Important:** Current App.js is 261 lines with complex state management. Extracting hooks and adding Context API will make the codebase maintainable.



**Tasks:****Tasks:**

- [ ] Implement Flask-Caching with in-memory cache (SimpleCache)- [ ] **Custom hooks:**

- [ ] Cache model registry (24-hour TTL)  - [ ] Create `useAuth` hook (login, logout, register, user state)

- [ ] Cache conversation summaries (1-hour TTL)  - [ ] Create `useChat` hook (messages, sendMessage, clearChat)

- [ ] Implement cache invalidation strategies  - [ ] Create `useComparison` hook (compare, results, history)

- [ ] Add cache hit/miss metrics  - [ ] Create `useModels` hook (model list, selection)

  - [ ] Create `useApiKeys` hook (save, validate keys)

**Implementation Notes:**  

```python- [ ] **Context API:**

from flask_caching import Cache  - [ ] Create `AppContext` for global state

  - [ ] Create `AuthContext` for user/session

cache = Cache(config={  - [ ] Create `ThemeContext` for dark/light mode

    'CACHE_TYPE': 'SimpleCache',  

    'CACHE_DEFAULT_TIMEOUT': 3600- [ ] **Component structure:**

})  ```

  src/

@cache.cached(timeout=86400, key_prefix='models_list')    components/

def get_available_models():      chat/

    pass        ChatMode.js

```        MessageList.js

        MessageItem.js

---        MessageInput.js

      comparison/

### 🚧 9. Frontend Architecture Refactor        ComparisonMode.js

**Priority:** P1 - High          ModelSelector.js

**Status:** NOT STARTED ⏸️          ResponseCard.js

**Duration:** 1-2 weeks      common/

        Modal.js

**Tasks:**        Button.js

- [ ] **Custom Hooks:**        LoadingSpinner.js

  - [ ] Create `useAuth` hook (login, logout, register, user state)    hooks/

  - [ ] Create `useChat` hook (messages, sendMessage, clearChat)      useAuth.js

  - [ ] Create `useComparison` hook (compare, results, history)      useChat.js

  - [ ] Create `useModels` hook (model list, selection)      useComparison.js

  - [ ] Create `useApiKeys` hook (save, validate keys)      useModels.js

      contexts/

- [ ] **Context API:**      AppContext.js

  - [ ] Create `AppContext` for global state  ```

  - [ ] Create `AuthContext` for user/session

  - [ ] Create `ThemeContext` for dark/light mode**Example Hook:**

  ```javascript

- [ ] **Component Restructure:**// hooks/useChat.js

  ```export const useChat = () => {

  src/  const [messages, setMessages] = useState([]);

    components/  const [isLoading, setIsLoading] = useState(false);

      chat/  const [conversationId, setConversationId] = useState(null);

        ChatMode.js  

        MessageList.js  const sendMessage = useCallback(async (content, provider, model) => {

        MessageItem.js    setIsLoading(true);

        MessageInput.js    try {

      comparison/      const response = await chatApi.sendMessage({

        ComparisonMode.js        provider,

        ModelSelector.js        model,

        ResponseCard.js        messages: [...messages, { role: 'user', content }],

      common/        conversationId

        Modal.js      });

        Button.js      

        LoadingSpinner.js      setMessages(prev => [

  ```        ...prev,

        { role: 'user', content },

---        { role: 'assistant', content: response.data.response }

      ]);

### ⏸️ 10. Testing Infrastructure      setConversationId(response.data.conversationId);

**Priority:** P1 - High      } finally {

**Status:** NOT STARTED ⏸️        setIsLoading(false);

**Duration:** 2-3 weeks    }

  }, [messages, conversationId]);

**Backend Testing:**  

- [ ] Expand unit test coverage to > 80%  return { messages, sendMessage, isLoading, conversationId };

- [ ] Add integration tests for streaming endpoints};

- [ ] Add tests for Azure routing logic```

- [ ] Performance regression tests

---

**Frontend Testing:**

- [ ] Set up Jest + React Testing Library### 8. TypeScript Migration (Optional)

- [ ] Unit tests for custom hooks**Priority:** P2 - Medium  

- [ ] Component tests for UI elements**Status:** NOT STARTED ⏸️  

- [ ] Integration tests for API interactions**Duration:** 1 week  

- [ ] E2E tests with Playwright/Cypress**Dependencies:** Component refactor (#7)  

  - [ ] User registration and login flow

  - [ ] API key management**Tasks:**

  - [ ] Chat conversation flow- [ ] Add TypeScript configuration

  - [ ] Comparison mode with streaming- [ ] Convert components to `.tsx`

  - [ ] Vote/preference recording- [ ] Add type definitions for API responses

- [ ] Add prop types for components

**Current Status:** 12/13 backend tests passing (92%)- [ ] Add utility types



---**Note:** This is optional but highly recommended for large applications.



### ⏸️ 11. Conversation Management UI---

**Priority:** P2 - Medium  

**Status:** NOT STARTED ⏸️  ## 🟢 PHASE 4: Testing & Quality (WEEKS 6-8)

**Duration:** 1 week

### 9. Frontend Testing Suite

**Tasks:****Priority:** P1 - High  

- [ ] Create ConversationSidebar component**Status:** NOT STARTED ⏸️  

- [ ] Add conversation list with search/filter**Duration:** 1-2 weeks  

- [ ] Add conversation rename/delete**Dependencies:** Component refactor (#7)  

- [ ] Add "New Conversation" button

- [ ] Add conversation metadata (date, message count)**Current Coverage:** 0% ❌

- [ ] Implement conversation switching

- [ ] Add conversation export (JSON/Markdown)**Tasks:**

- [ ] **Setup:**

**Mockup:**  - [ ] Install Jest, React Testing Library, @testing-library/user-event

```  - [ ] Configure test environment

┌────────────────────┬─────────────────────────┐  - [ ] Add test scripts to package.json

│ Conversations      │ Chat                    │  

│ ──────────────────│                         │- [ ] **Component tests:**

│ 🔍 Search...      │ Messages...             │  - [ ] MessageList component tests

│                    │                         │  - [ ] MessageInput component tests

│ Today              │                         │  - [ ] Header component tests

│ • Code Review Help │                         │  - [ ] Modal component tests

│ • API Design Q...  │                         │  - [ ] ComparisonMode tests (when implemented)

│                    │                         │  

│ Yesterday          │                         │- [ ] **Hook tests:**

│ • Debug SQL Query  │                         │  - [ ] useAuth tests

└────────────────────┴─────────────────────────┘  - [ ] useChat tests

```  - [ ] useComparison tests

  

---- [ ] **Integration tests:**

  - [ ] Complete user flow tests

## 🟠 PHASE 5: User Experience Enhancements (NOT STARTED ⏸️)  - [ ] API integration tests (mocked)

  

### ⏸️ 12. Comparison Export- [ ] **Target:** 80%+ code coverage

**Priority:** P2 - Medium  

**Status:** NOT STARTED ⏸️  **Example Test:**

**Duration:** 3-4 days```javascript

// components/__tests__/MessageList.test.js

**Tasks:**import { render, screen } from '@testing-library/react';

- [ ] Export comparison as Markdownimport MessageList from '../MessageList';

- [ ] Export comparison as PDF

- [ ] Export comparison as JSONdescribe('MessageList', () => {

- [ ] Add export button to ComparisonMode  it('renders messages correctly', () => {

- [ ] Include metadata in exports (models, timing, tokens)    const messages = [

      { role: 'user', content: 'Hello' },

---      { role: 'assistant', content: 'Hi!' }

    ];

### ⏸️ 13. Mobile Responsive Design    

**Priority:** P2 - Medium      render(<MessageList messages={messages} isLoading={false} />);

**Status:** NOT STARTED ⏸️      

**Duration:** 1 week    expect(screen.getByText('Hello')).toBeInTheDocument();

    expect(screen.getByText('Hi!')).toBeInTheDocument();

**Tasks:**  });

- [ ] Optimize comparison layout for mobile (stack vertically)  

- [ ] Add touch gestures for scrolling  it('shows loading indicator', () => {

- [ ] Optimize button sizes for touch    render(<MessageList messages={[]} isLoading={true} />);

- [ ] Test on iOS and Android devices    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();

- [ ] Ensure keyboard doesn't obscure input  });

- [ ] Add mobile-specific navigation});

```

---

---

### ⏸️ 14. Accessibility Improvements

**Priority:** P2 - Medium  ### 10. Backend Test Coverage Expansion

**Status:** NOT STARTED ⏸️  **Priority:** P1 - High  

**Duration:** 3-5 days**Status:** IN PROGRESS 🚧  

**Duration:** 1 week  

**Tasks:****Dependencies:** None  

- [ ] Add ARIA labels to all interactive elements

- [ ] Ensure keyboard navigation works everywhere**Current Coverage:** ~30% (basic tests exist)  

- [ ] Add focus indicators**Target Coverage:** 90%+

- [ ] Test with screen readers (NVDA, JAWS, VoiceOver)

- [ ] Add alt text to all images/icons**Tasks:**

- [ ] Ensure color contrast meets WCAG AA standards- [ ] **Streaming tests:**

- [ ] Add skip links for keyboard users  - [ ] SSE endpoint tests

  - [ ] Stream error handling

---  - [ ] Stream cancellation

  

### ⏸️ 15. Theme Toggle (Dark/Light Mode)- [ ] **Comparison tests:**

**Priority:** P2 - Medium    - [ ] Multi-model comparison

**Status:** NOT STARTED ⏸️    - [ ] Parallel execution tests

**Duration:** 2-3 days  - [ ] Timeout handling

  - [ ] Partial failure tests

**Tasks:**  

- [ ] Create light mode color palette- [ ] **Authentication tests:**

- [ ] Add theme toggle button to header  - [ ] JWT token refresh

- [ ] Persist theme preference to localStorage  - [ ] Session expiration

- [ ] Update all components to support both themes  - [ ] CSRF protection

- [ ] Ensure syntax highlighting works in both themes  - [ ] Rate limiting enforcement

- [ ] Test for color contrast in both themes  

- [ ] **LLM service tests:**

---  - [ ] Provider-specific tests

  - [ ] Retry logic tests

### ⏸️ 16. Keyboard Shortcuts  - [ ] Response parsing tests

**Priority:** P3 - Low    - [ ] Error handling tests

**Status:** NOT STARTED ⏸️    

**Duration:** 2-3 days- [ ] **Database tests:**

  - [ ] Conversation persistence

**Tasks:**  - [ ] Message ordering

- [ ] Add shortcut for new conversation (Ctrl+N)  - [ ] User isolation

- [ ] Add shortcut for focus input (Ctrl+/)  - [ ] API key encryption/decryption

- [ ] Add shortcut for submit message (Ctrl+Enter)

- [ ] Add shortcut for cancel request (Escape)**Example Test:**

- [ ] Add shortcut for mode toggle (Ctrl+M)```python

- [ ] Add keyboard shortcut help modal (?)# tests/test_comparison.py

def test_compare_multiple_models(client, app, monkeypatch):

---    """Test side-by-side comparison of multiple models"""

    register_and_login(client)

## 🔵 PHASE 6: Advanced Features (NOT STARTED ⏸️)    

    responses = {"openai": "GPT response", "anthropic": "Claude response"}

### ⏸️ 17. Model Configuration Panel    

**Priority:** P3 - Low      def fake_invoke(provider, model, messages, api_key):

**Status:** NOT STARTED ⏸️          return responses[provider]

**Duration:** 3-5 days    

    monkeypatch.setattr(app.extensions["services"].llm, "invoke", fake_invoke)

**Tasks:**    

- [ ] Add advanced settings panel    response = client.post("/api/v1/compare", json={

- [ ] Temperature control slider        "prompt": "Hello",

- [ ] Max tokens slider        "providers": [

- [ ] Top-p slider            {"provider": "openai", "model": "gpt-4"},

- [ ] Frequency penalty slider            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}

- [ ] Presence penalty slider        ]

- [ ] System message customization    })

- [ ] Save custom presets    

- [ ] Provider-specific settings    assert response.status_code == 200

    data = response.get_json()

---    assert data["openai"] == "GPT response"

    assert data["anthropic"] == "Claude response"

### ⏸️ 18. Cost Tracking & Analytics```

**Priority:** P3 - Low  

**Status:** NOT STARTED ⏸️  ---

**Duration:** 1 week

### 11. E2E Testing with Playwright

**Tasks:****Priority:** P2 - Medium  

- [ ] Track token usage per provider**Status:** NOT STARTED ⏸️  

- [ ] Calculate costs based on current pricing**Duration:** 3-4 days  

- [ ] Show cost per conversation**Dependencies:** Comparison UI (#4)  

- [ ] Show cost per comparison

- [ ] Monthly cost dashboard**Tasks:**

- [ ] Set budget alerts- [ ] Install Playwright

- [ ] Export usage reports (CSV)- [ ] Configure test environment

- [ ] Visualize usage trends- [ ] Write critical user flows:

  - [ ] User registration and login

---  - [ ] API key configuration

  - [ ] Single model chat

### ⏸️ 19. Voice Input/Output  - [ ] Multi-model comparison

**Priority:** P3 - Low    - [ ] Conversation history

**Status:** NOT STARTED ⏸️    - [ ] Settings management

**Duration:** 1 week

**Example E2E Test:**

**Tasks:**```javascript

- [ ] Integrate Web Speech API// e2e/comparison.spec.js

- [ ] Add microphone buttonimport { test, expect } from '@playwright/test';

- [ ] Add voice transcription (speech-to-text)

- [ ] Add text-to-speech for responsestest('compare multiple models', async ({ page }) => {

- [ ] Handle multiple languages  await page.goto('http://localhost:3044');

- [ ] Add voice activity detection  

  // Login

---  await page.click('text=Sign in');

  await page.fill('input[name="username"]', 'testuser');

### ⏸️ 20. Conversation Templates  await page.fill('input[name="password"]', 'testpass');

**Priority:** P3 - Low    await page.click('button:has-text("Login")');

**Status:** NOT STARTED ⏸️    

**Duration:** 3-5 days  // Switch to compare mode

  await page.click('button:has-text("Compare")');

**Tasks:**  

- [ ] Create template library  // Select models

- [ ] Add template categories (code, writing, analysis, etc.)  await page.click('text=Add model');

- [ ] User-created templates  await page.selectOption('select[name="provider"]', 'openai');

- [ ] Template variables/placeholders  

- [ ] Template sharing (import/export)  // Send prompt

  await page.fill('textarea', 'Explain quantum computing');

---  await page.click('button[type="submit"]');

  

## 🆕 NEW FEATURES (BACKLOG)  // Verify responses appear

  await expect(page.locator('.response-card').first()).toBeVisible();

### ⏸️ 21. Comparison Output Difference Summarizer});

**Priority:** P2 - Medium  ```

**Status:** NOT STARTED ⏸️  

**Duration:** 1 week  ---

**Added:** November 6, 2025

## 🔵 PHASE 5: Conversation Management (WEEKS 7-8)

**Description:**  

After generating outputs from multiple models in the 'compare' feature, add a button that analyzes and summarizes the key differences between each output in a structured table format.### 12. Conversation Sidebar & History

**Priority:** P2 - Medium  

**Feature Details:****Status:** NOT STARTED ⏸️  

- Add "Summarize Differences" button that appears after all model outputs are generated**Duration:** 1 week  

- When clicked, analyze the outputs and identify:**Dependencies:** None  

  - Content differences (what information each model included/excluded)

  - Structural differences (formatting, organization)**Tasks:**

  - Tone/style differences- [ ] **Backend:**

  - Length variations  - [ ] Add `GET /api/v1/conversations` endpoint

  - Key factual discrepancies  - [ ] Add `DELETE /api/v1/conversations/:id` endpoint

- Present findings in a summary table with columns for:  - [ ] Add `PATCH /api/v1/conversations/:id` endpoint (rename)

  - Aspect/Category  - [ ] Add conversation search endpoint

  - Model 1  - [ ] Add pagination support

  - Model 2  

  - Model N (for each model compared)- [ ] **Frontend:**

- Make the comparison actionable and easy to scan  - [ ] Create ConversationSidebar component

  - [ ] Add conversation list with timestamps

**Technical Considerations:**  - [ ] Implement search/filter

- May need to use an LLM to perform the comparison analysis  - [ ] Add "New conversation" button

  - Could use cheapest available model (e.g., gpt-4o-mini) to reduce costs  - [ ] Add conversation deletion

  - Or use dedicated comparison/analysis model  - [ ] Add conversation renaming

- Consider caching results if the same outputs are compared multiple times  - [ ] Show active conversation indicator

- UI should handle variable number of models being compared (2-4)  

- Table should be responsive and readable on all devices- [ ] **UX:**

- Button should be disabled during streaming  - [ ] Collapsible sidebar (toggle)

- Consider adding option to export the difference summary  - [ ] Keyboard shortcuts (Ctrl+K for search)

  - [ ] Drag to reorder

**Implementation Approach:**  - [ ] Pin important conversations

1. Add new backend endpoint: `POST /api/v1/comparisons/:id/analyze`

2. Use LLM to generate structured difference analysis**Mockup:**

3. Create `DifferenceSummary` component for display```

4. Add "Summarize Differences" button to ComparisonMode┌──────────┬───────────────────────┐

5. Display results in collapsible panel or modal│ 🔍 Search│  Current Chat         │

├──────────┤                       │

**Dependencies:**│ 📌 Pinned│                       │

- Requires comparison result to be saved (✅ already implemented)│ · Conv 1 │                       │

- May require additional API credits for analysis calls│          │                       │

│ 📅 Today │                       │

---│ · Conv 2 │                       │

│ · Conv 3 │                       │

## 🐛 KNOWN ISSUES & TECHNICAL DEBT│          │                       │

│ 📅 Yest. │                       │

### Performance Issues│ · Conv 4 │                       │

│          │                       │

#### 1. Parallel API Calls for Same Provider│ [+ New]  │                       │

**Priority:** P2 - Medium  └──────────┴───────────────────────┘

**Status:** NOT STARTED ⏸️  ```



**Problem:**  ---

When comparing multiple models from the same provider (e.g., GPT-4o and GPT-3.5-Turbo from OpenAI), requests may execute sequentially rather than in parallel, causing unnecessary delays.

### 13. Conversation Export & Sharing

**Investigation Needed:****Priority:** P3 - Low  

1. Verify if requests library's Session object is causing sequential execution**Status:** NOT STARTED ⏸️  

2. Check API provider rate limits**Duration:** 3-4 days  

3. Test impact of connection pool size**Dependencies:** Conversation sidebar (#12)  

4. Consider per-provider connection pool configuration

**Tasks:**

**Proposed Solutions:**- [ ] **Export formats:**

1. **Connection Pool Tuning:**  - [ ] Export as Markdown

   ```python  - [ ] Export as JSON

   from requests.adapters import HTTPAdapter  - [ ] Export as PDF (using jsPDF)

   adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)  - [ ] Export as HTML

   ```  

2. **Provider-Specific Rate Limit Handling:**- [ ] **Sharing (optional):**

   - Research rate limits per provider  - [ ] Generate shareable link

   - Implement provider-specific semaphores if needed  - [ ] Anonymous viewing mode

3. **Async Architecture (Future):**  - [ ] Expiration settings

   - Consider migrating to `httpx` or `aiohttp`  - [ ] Password protection

   - Would require Flask async views or FastAPI migration

---

**Acceptance Criteria:**

- Multiple models from same provider complete in parallel## ⚡ PHASE 6: Performance & Optimization (WEEKS 9-10)

- No increase in API errors or rate limit violations

- Total comparison time reduced### 14. Response Caching

- Connection pool metrics logged**Priority:** P2 - Medium  

**Status:** NOT STARTED ⏸️  

**Estimated Effort:** 1-2 days**Duration:** 3-4 days  

**Dependencies:** None  

---

**Tasks:**

### Frontend Issues- [ ] Install Redis

- [ ] Implement cache key generation (hash of prompt + model)

#### 2. Bundle Size Optimization- [ ] Add cache lookup before API calls

**Priority:** P2 - Medium  - [ ] Set appropriate TTL (1 hour suggested)

**Status:** NOT STARTED ⏸️- [ ] Add cache invalidation

- [ ] Add cache statistics endpoint

**Problem:**  

Bundle size increased to 1020 KiB (from 246 KiB) due to syntax highlighter library including 277 languages.**Implementation:**

```python

**Proposed Solutions:**# llmselect/services/llm.py

- [ ] Implement code splitting for syntax highlighterimport hashlib

- [ ] Lazy load language support (load on-demand)import redis

- [ ] Consider using lighter alternative (e.g., highlight.js with selective languages)

- [ ] Add bundle size monitoring to CI/CDclass LLMService:

    def __init__(self):

**Target:** Reduce bundle to < 500 KiB        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    

---    def invoke(self, provider, model, messages, api_key):

        # Check cache

### Backend Issues        cache_key = self._generate_cache_key(provider, model, messages)

        cached = self.redis.get(cache_key)

#### 3. Incomplete Error Handling        if cached:

**Priority:** P2 - Medium              return cached

**Status:** PARTIAL ✅        

        # Call provider

**Remaining Tasks:**        response = self._call_provider(provider, model, messages, api_key)

- [ ] Custom error pages (404, 500, etc.)        

- [ ] Client-side error reporting (Sentry integration)        # Cache for 1 hour

- [ ] Better error messages for API key validation failures        self.redis.setex(cache_key, 3600, response)

- [ ] Timeout handling for long-running streaming requests        

        return response

---```



## 📅 Implementation Roadmap---



### **Q1 2025 (Completed ✅)**### 15. Bundle Optimization & Code Splitting

- ✅ Phase 1: Security & Backend Architecture (Weeks 1-4)**Priority:** P2 - Medium  

- ✅ Phase 2: Comparison Mode UI (Weeks 5-7)**Status:** NOT STARTED ⏸️  

- ✅ Phase 3: Real-Time Streaming (Weeks 8-9)**Duration:** 2-3 days  

- ✅ Azure AI Foundry Integration (Week 10)**Dependencies:** None  



### **Q2 2025 (Planned)****Tasks:**

- 🚧 Phase 4: Performance & Polish (Weeks 11-14)- [ ] Configure webpack code splitting

  - Database optimization- [ ] Lazy load comparison mode

  - Response caching- [ ] Lazy load markdown renderer

  - Frontend refactor- [ ] Separate vendor bundles

  - Testing infrastructure- [ ] Add bundle analysis

- ⏸️ Phase 5: UX Enhancements (Weeks 15-18)- [ ] Optimize images and assets

  - Comparison export- [ ] Enable gzip compression

  - Mobile responsive design

  - Accessibility improvements**Webpack Config:**

  - Theme toggle```javascript

// webpack.config.js

### **Q3 2025 (Planned)**module.exports = {

- ⏸️ Phase 6: Advanced Features (Weeks 19-24)  optimization: {

  - Model configuration panel    splitChunks: {

  - Cost tracking      chunks: 'all',

  - Conversation templates      cacheGroups: {

  - Difference summarizer        vendor: {

- ⏸️ Production deployment preparation          test: /[\\/]node_modules[\\/]/,

  - Load testing          name: 'vendors',

  - Security audit          priority: 10

  - Documentation finalization        },

        react: {

---          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,

          name: 'react',

## 🎯 Success Metrics          priority: 20

        }

### Phase 1 Success Criteria (✅ MET)      }

- ✅ Zero security vulnerabilities in dependency scan    }

- ✅ All API keys encrypted at rest  }

- ✅ JWT authentication working with token refresh};

- ✅ Rate limiting prevents abuse```



### Phase 2 Success Criteria (✅ MET)---

- ✅ Users can compare 2-4 models side-by-side

- ✅ Comparison results are persisted to database### 16. Performance Monitoring

- ✅ Users can vote on preferred responses**Priority:** P3 - Low  

- ✅ Comparison history accessible**Status:** NOT STARTED ⏸️  

**Duration:** 2-3 days  

### Phase 3 Success Criteria (✅ MET)**Dependencies:** None  

- ✅ Time to first token < 1 second (achieved: < 1s)

- ✅ Multiple models stream in parallel without blocking**Tasks:**

- ✅ Markdown rendering with syntax highlighting works- [ ] Add Web Vitals tracking

- ✅ Code blocks are readable with copy buttons- [ ] Implement custom performance marks

- ✅ Comparison history UI displays past results- [ ] Add API response time tracking

- [ ] Track LLM provider latency

### Phase 4 Success Criteria (🚧 IN PROGRESS)- [ ] Add error rate monitoring

- [ ] Page load time < 1 second- [ ] Create performance dashboard

- [ ] Common database queries < 50ms

- [ ] No N+1 query issues---

- [ ] Frontend architecture uses custom hooks and Context API

- [ ] Test coverage > 80%## 🎨 PHASE 7: UX/UI Polish (WEEKS 10-11)



### Phase 5 Success Criteria (⏸️ NOT STARTED)### 17. Accessibility (a11y) Improvements

- [ ] Mobile responsive on all devices**Priority:** P2 - Medium  

- [ ] Passes WCAG AA accessibility standards**Status:** NOT STARTED ⏸️  

- [ ] Supports dark and light themes**Duration:** 3-4 days  

- [ ] Keyboard shortcuts implemented**Dependencies:** None  



---**Tasks:**

- [ ] Add ARIA labels to all interactive elements

## 📊 Technical Debt Summary- [ ] Implement keyboard navigation (Tab, Arrow keys)

- [ ] Add focus indicators

### By Priority- [ ] Improve color contrast (WCAG AA compliance)

- [ ] Add skip-to-content link

| Priority | Total Items | Est. Time |- [ ] Test with screen readers (NVDA, JAWS)

|----------|-------------|-----------|- [ ] Add alt text for all images

| P0 - Critical | 0 items | 0 weeks (all complete ✅) |- [ ] Support reduced motion preferences

| P1 - High | 4 items | 5-8 weeks |

| P2 - Medium | 8 items | 6-9 weeks |---

| P3 - Low | 7 items | 5-8 weeks |

| **Total** | **19 items** | **16-25 weeks** |### 18. Mobile Responsiveness

**Priority:** P2 - Medium  

### By Category**Status:** NOT STARTED ⏸️  

**Duration:** 3-4 days  

| Category | Items | Status |**Dependencies:** Comparison UI (#4)  

|----------|-------|--------|

| Security & Auth | 2 | 100% Complete ✅ |**Tasks:**

| Backend Architecture | 4 | 75% Complete (caching, optimization pending) |- [ ] Responsive comparison layout (stack on mobile)

| Frontend UI/UX | 8 | 60% Complete (refactor, mobile, accessibility pending) |- [ ] Touch-friendly tap targets (min 44x44px)

| Testing | 1 | 10% Complete (backend only) |- [ ] Mobile-optimized sidebar (drawer)

| Advanced Features | 5 | 0% Complete ⏸️ |- [ ] Swipe gestures for navigation

- [ ] Virtual keyboard handling

---- [ ] Test on iOS and Android

- [ ] Add PWA support (optional)

## 📝 Notes

---

- **Phase 1, 2, 3, and Azure Integration are complete** and delivered high-quality foundational features

- **Phase 4 (Performance)** is the current focus for production readiness### 19. Theme & Visual Polish

- **Streaming is production-ready** with <1s time to first token across all providers**Priority:** P3 - Low  

- **Markdown rendering** creates professional appearance for code and formatted content**Status:** NOT STARTED ⏸️  

- **Azure integration** enables enterprise deployments with unified billing**Duration:** 2-3 days  

- Testing infrastructure needs significant investment for long-term maintainability**Dependencies:** None  

- Mobile optimization is deferred but should be prioritized for wider adoption

- Advanced features (analytics, voice, templates) are nice-to-have but not critical**Tasks:**

- [ ] Add light theme option

---- [ ] Implement theme toggle

- [ ] Persist theme preference

**Last Updated:** November 6, 2025  - [ ] Add theme transition animations

**Next Review:** January 1, 2026  - [ ] Refine color palette

**Maintained By:** @jbuz- [ ] Add loading skeletons

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

### 9. Dynamic Model Management (UPDATED - Nov 2025)
**Priority:** P1 - High  
**Category:** Features  
**Status:** NOT STARTED ⏸️  
**Duration:** 1-2 weeks

**Issues:**
- Hardcoded model lists in frontend (outdated models)
- Missing latest models: GPT-4o, GPT-4o-mini, o1-preview, o1-mini, Gemini 1.5 Pro/Flash, Gemini 2.0 Flash
- No model capabilities information
- Can't adjust model parameters (temperature, max_tokens, etc.)
- No token usage tracking
- No cost estimation

**Phase 1: Dynamic Model Discovery (Priority: HIGH)**
- [ ] **Backend: Model Registry Service**
  - [ ] Create `ModelRegistryService` class to query provider APIs for available models
  - [ ] Add caching layer (Redis/memory) to reduce API calls
  - [ ] Implement fallback to static model lists if API fails
  - [ ] Query OpenAI models API: `GET https://api.openai.com/v1/models`
  - [ ] Query Anthropic models (use static list with version check)
  - [ ] Query Google AI models: `GET https://generativelanguage.googleapis.com/v1beta/models`
  - [ ] Query Mistral models API
  
- [ ] **Backend: Models Endpoint**
  - [ ] Create `GET /api/v1/models` endpoint
  - [ ] Return structured model data: `{provider, id, name, contextWindow, maxTokens, capabilities, pricing}`
  - [ ] Add filtering by provider: `GET /api/v1/models?provider=openai`
  - [ ] Add caching headers (1 hour TTL)
  
- [ ] **Frontend: Dynamic Model Loading**
  - [ ] Create `useModels()` hook to fetch from backend
  - [ ] Replace hardcoded `PROVIDER_MODELS` in App.js
  - [ ] Update ModelSelector component to use dynamic data
  - [ ] Add loading states while fetching models
  - [ ] Handle errors gracefully (fallback to cached/default models)

**Phase 2: Latest Models Addition (Priority: HIGH)**
- [ ] **Add OpenAI models:**
  - [ ] `gpt-4o` (GPT-4 Optimized - 128k context)
  - [ ] `gpt-4o-mini` (cost-effective, 128k context)
  - [ ] `o1-preview` (reasoning model, 128k context)
  - [ ] `o1-mini` (faster reasoning, 128k context)
  
- [ ] **Add Google models:**
  - [ ] `gemini-1.5-pro` (2M token context)
  - [ ] `gemini-1.5-flash` (1M token context, faster)
  - [ ] `gemini-2.0-flash-exp` (newest experimental)
  
- [ ] **Update Anthropic:**
  - [ ] `claude-3-5-sonnet-20241022` (already present ✅)
  - [ ] Verify version is latest (check for newer releases)
  
- [ ] **Update Mistral:**
  - [ ] Keep `-latest` suffix but add specific version IDs
  - [ ] Add `mistral-small-2409`, `mistral-large-2411`

**Phase 3: Model Capabilities & Settings (Priority: MEDIUM)**
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

**Technical Design:**
```python
# Backend: llmselect/services/model_registry.py
class ModelRegistryService:
    def __init__(self, cache_ttl=3600):
        self._cache = {}
        self._cache_ttl = cache_ttl
    
    async def get_available_models(self, provider=None):
        """Fetch models from provider APIs with caching"""
        if provider:
            return await self._fetch_provider_models(provider)
        
        all_models = {}
        for p in ['openai', 'anthropic', 'gemini', 'mistral']:
            all_models[p] = await self._fetch_provider_models(p)
        return all_models
    
    async def _fetch_openai_models(self):
        """Query OpenAI API for latest models"""
        # Implementation with error handling and fallback
```

```javascript
// Frontend: src/hooks/useModels.js
export const useModels = (provider = null) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const endpoint = provider 
          ? `/api/v1/models?provider=${provider}`
          : '/api/v1/models';
        const response = await http.get(endpoint);
        setModels(response.data);
      } catch (err) {
        setError(err);
        // Fallback to default models
        setModels(DEFAULT_MODELS);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, [provider]);
  
  return { models, loading, error };
};
```

**Success Criteria:**
- [ ] Models list updates automatically when providers release new models
- [ ] All latest models (as of Nov 2025) are available in UI
- [ ] Fallback mechanism works if API calls fail
- [ ] Performance: models load in <500ms (with caching)
- [ ] No breaking changes to existing functionality

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

### 13. Multimodal Support - Vision Input
**Priority:** P2 - Medium  
**Category:** Features  
**Status:** NOT STARTED ⏸️  
**Duration:** 2-3 weeks  
**Added:** November 22, 2025

**Context:**
Many models in the registry now support multimodal input (analyzing images provided by users):
- **GPT-5.1** - Full multimodal support
- **Claude Sonnet 4.5** - Vision and document analysis
- **Gemini 2.5 Pro, Flash, Flash-Lite** - Native multimodal
- **Gemini 3 Pro (Preview)** - Advanced multimodal
- **Gemini Pro Vision** - Dedicated vision model

This feature enables users to upload images and ask questions about them (e.g., "What's in this image?", "Analyze this chart", "Debug this error screenshot").

**Note:** This is separate from image generation (DALL-E), which remains P3-Low priority.

**Phase 1: Backend - Image Upload & Storage (1 week)**
- [ ] **Cloud Storage Integration:**
  - [ ] Set up Azure Blob Storage or AWS S3 bucket
  - [ ] Configure storage credentials and access policies
  - [ ] Implement upload service with signed URLs
  - [ ] Add image optimization (resize, compress)
  - [ ] Configure CORS for direct browser uploads
  - [ ] Set up automatic cleanup for old images (30-day retention)
  
- [ ] **Database Schema:**
  ```sql
  CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    conversation_id INTEGER,
    message_id INTEGER,
    storage_url TEXT NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (message_id) REFERENCES messages(id)
  );
  
  CREATE INDEX idx_images_user_id ON images(user_id);
  CREATE INDEX idx_images_conversation_id ON images(conversation_id);
  ```

- [ ] **API Endpoints:**
  - [ ] `POST /api/v1/images/upload` - Upload image, return storage URL
  - [ ] `GET /api/v1/images/{id}` - Get image metadata
  - [ ] `DELETE /api/v1/images/{id}` - Delete image
  - [ ] Add file size limits (10MB max)
  - [ ] Validate image types (JPEG, PNG, WebP, GIF)
  - [ ] Add rate limiting for uploads

- [ ] **Message Schema Updates:**
  ```python
  # llmselect/schemas.py
  class MessageContentItem(Schema):
      type = fields.String(required=True)  # "text" or "image"
      text = fields.String()  # For type="text"
      image_url = fields.String()  # For type="image"
      
  class MessageSchema(Schema):
      role = fields.String(required=True)
      content = fields.List(fields.Nested(MessageContentItem))  # Changed from String
  ```

**Phase 2: LLM Service Integration (3-4 days)**
- [ ] **Update LLMService for multimodal:**
  - [ ] Modify `_call_openai()` to support vision messages
  - [ ] Modify `_call_anthropic()` for Claude vision
  - [ ] Modify `_call_gemini()` for Gemini vision
  - [ ] Handle image URL references in message content
  - [ ] Add image preprocessing (base64 encoding if needed)
  - [ ] Add error handling for unsupported models

- [ ] **Model Registry Updates:**
  ```python
  # Add capabilities field to model definitions
  {
      "id": "gpt-5.1",
      "name": "GPT-5.1",
      "provider": "openai",
      "capabilities": ["text", "vision", "multimodal"],
      # ...
  }
  ```

- [ ] **Example API calls:**
  ```python
  # OpenAI Vision API
  {
      "model": "gpt-5.1",
      "messages": [
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "What's in this image?"},
                  {"type": "image_url", "image_url": {"url": "https://..."}}
              ]
          }
      ]
  }
  ```

**Phase 3: Frontend - Image Upload UI (1 week)**
- [ ] **Image Upload Component:**
  - [ ] Create `ImageUpload.js` component
  - [ ] Add drag-and-drop zone
  - [ ] Add file picker button
  - [ ] Show upload progress indicator
  - [ ] Display image preview thumbnails
  - [ ] Add remove/clear functionality
  [ ] Support multiple images per message
  - [ ] Add paste-from-clipboard support

- [ ] **Update MessageInput:**
  ```javascript
  // src/components/chat/MessageInput.js
  const MessageInput = () => {
    const [text, setText] = useState('');
    const [images, setImages] = useState([]);
    
    const handleImageUpload = async (files) => {
      // Upload to backend, get URLs
      const uploadedImages = await uploadImages(files);
      setImages(prev => [...prev, ...uploadedImages]);
    };
    
    const handleSubmit = () => {
      // Send message with text + image URLs
      sendMessage({
        content: [
          { type: 'text', text },
          ...images.map(img => ({ type: 'image', url: img.url }))
        ]
      });
    };
  };
  ```

- [ ] **Update MessageList to display images:**
  - [ ] Render inline images in messages
  - [ ] Add lightbox/zoom functionality
  - [ ] Show image loading states
  - [ ] Handle image load errors gracefully
  - [ ] Add image alt text for accessibility

- [ ] **Model Selector Updates:**
  - [ ] Show vision capability badge on models
  - [ ] Disable image upload for non-vision models
  - [ ] Show tooltip: "This model supports image analysis"

**Phase 4: Comparison Mode Support (3-4 days)**
- [ ] Enable image upload in comparison mode
- [ ] Send same image(s) to all selected models
- [ ] Display images in each response card
- [ ] Allow voting on vision-based comparisons

**Phase 5: Testing & Polish (3-4 days)**
- [ ] **Backend Tests:**
  - [ ] Image upload endpoint tests
  - [ ] Multimodal message schema validation
  - [ ] Cloud storage integration tests
  - [ ] Image cleanup job tests
  
- [ ] **Frontend Tests:**
  - [ ] ImageUpload component tests
  - [ ] Drag-and-drop tests
  - [ ] Image display tests
  - [ ] Error handling tests

- [ ] **Integration Tests:**
  - [ ] Upload image → send to GPT-5.1 → receive response
  - [ ] Upload image → compare across multiple vision models
  - [ ] Image deletion and cleanup

- [ ] **Manual Testing:**
  - [ ] Test with various image formats (JPEG, PNG, WebP)
  - [ ] Test with large images (resize/compression)
  - [ ] Test with multiple images per message
  - [ ] Test error cases (invalid format, too large, network issues)
  - [ ] Test on mobile devices

**Dependencies:**
- Azure Blob Storage or AWS S3 account
- Frontend refactor (#9) - custom hooks
- Model registry with capabilities field

**Acceptance Criteria:**
- [ ] Users can upload images (drag-drop or file picker)
- [ ] Images stored securely in cloud storage
- [ ] Vision-capable models can analyze uploaded images
- [ ] Images display correctly in chat history
- [ ] Comparison mode works with images
- [ ] All tests passing
- [ ] Mobile-friendly image upload

**Storage Cost Estimate:**
- Azure Blob Storage: ~$0.02 per GB/month (hot tier)
- Assuming 1MB avg image, 1000 images = ~$0.02/month
- With 30-day retention, costs are minimal

---

## 🟢 Low Priority / Nice-to-Have

### 14. Advanced Features
**Priority:** P3 - Low  
**Category:** Features

**Action Items:**
- [ ] Multi-language support (i18n)
- [ ] Voice input/output integration
- [ ] **Image generation output (DALL-E, Midjourney)** - Note: Vision input (analyzing images) is P2-Medium (#13)
- [ ] Plugin/extension system
- [ ] Conversation sharing functionality
- [ ] Collaborative editing
- [ ] Conversation templates/prompts library
- [ ] Integration with third-party tools (Notion, Slack, etc.)
- [ ] Analytics dashboard
- [ ] A/B testing framework for prompts
- [ ] Conversation branching (explore alternate responses)
- [ ] Audio input/output support

---

### 15. Developer Experience
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

### 16. Infrastructure & DevOps
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

## � Performance & Optimization Backlog

### Parallel API Calls for Same Provider
**Priority:** P2 - Medium  
**Status:** Not Started ⏸️  
**Category:** Performance Optimization  

**Problem:**
When comparing multiple models from the same provider (e.g., GPT-5 and GPT-4o from OpenAI), requests appear to be executed sequentially rather than in parallel, causing unnecessary delays in the comparison UI.

**Current Behavior:**
- ThreadPoolExecutor is used in `/api/v1/compare` and `/api/v1/compare/stream`
- HTTP session may be reusing connections sequentially
- No explicit connection pooling configuration for concurrent same-host requests

**Investigation Needed:**
1. Verify if requests library's Session object is causing sequential execution for same-host
2. Check if API provider rate limits require sequential requests
3. Test impact of connection pool size on parallel performance
4. Consider per-provider connection pool configuration

**Proposed Solutions:**
1. **Connection Pool Tuning:**
   - Configure `HTTPAdapter` with `pool_connections` and `pool_maxsize` parameters
   - Consider separate session instances per provider
   - Example: `HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retry)`

2. **Provider-Specific Rate Limit Handling:**
   - Research rate limits per provider:
     - OpenAI: Typically allows parallel requests
     - Anthropic: Check if per-account limits apply
     - Google Gemini: Verify QPM (queries per minute) limits
     - Mistral: Document concurrent request policies
   - Implement provider-specific semaphores if needed

3. **Async Architecture (Future Enhancement):**
   - Consider migrating to `httpx` or `aiohttp` for true async concurrent requests
   - Would require Flask migration to async views or FastAPI migration

**Acceptance Criteria:**
- Multiple models from same provider complete in parallel (observable via logging)
- No increase in API errors or rate limit violations
- Total comparison time reduced when using same-provider models
- Connection pool metrics logged for monitoring

**Estimated Effort:** 1-2 days  
**Dependencies:** None  
**Related:** Performance improvements (#6)

---

## �📝 Notes

- This backlog should be revisited quarterly
- Priority levels may change based on user feedback
- Each item should be broken down into smaller tickets for implementation
- Consider creating GitHub issues from this backlog
- Use feature flags for gradual rollout of major changes

---

**Last Updated:** November 6, 2025  
**Next Review:** January 21, 2026


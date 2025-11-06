# SUPERPROMPT: Phase 4 - Performance Optimization & Code Quality

**Project:** LLMSelect - Multi-LLM Comparison Platform  
**Phase:** 4 (Performance & Polish)  
**Priority:** HIGH - Production Readiness  
**Target:** Production-ready application with optimized performance and maintainable codebase  
**Duration:** 3-4 weeks  
**Date:** November 6, 2025

---

## 🎯 EXECUTIVE SUMMARY

Phase 4 focuses on making LLMSelect production-ready by optimizing performance, refactoring frontend architecture, and establishing comprehensive testing. Phases 1-3 delivered all core features (security, comparison mode, streaming); now we optimize and polish for deployment.

**What's Complete (✅):**
- Phase 1: Security infrastructure, backend architecture, error handling
- Phase 2: Comparison mode UI, multi-model selector, persistence, voting
- Phase 3: Real-time streaming (SSE), markdown rendering, comparison history
- Azure Integration: Unified routing through Azure AI Foundry

**Phase 4 Goals:**
1. **Database & Backend Performance** - Indexes, connection pooling, query optimization
2. **Response Caching** - Flask-Caching for model registry and conversations
3. **Frontend Architecture Refactor** - Custom hooks, Context API, component restructure
4. **Testing Infrastructure** - Expand coverage to >80%, add frontend tests
5. **Conversation Management UI** - Sidebar with history, search, and management

**Success Criteria:**
- Page load time < 1 second
- Common database queries < 50ms
- No N+1 query issues
- Frontend uses custom hooks and Context API
- Test coverage > 80% (backend), > 60% (frontend)
- Users can manage conversation history in sidebar

---

## 📋 CONTEXT & CURRENT STATE

### Project Structure
```
/home/jamesbuzzard/Git/LLMSelect/
├── app.py                          # Flask application entry point
├── llmselect/                      # Python backend
│   ├── __init__.py                 # Application factory
│   ├── config.py                   # Configuration management
│   ├── container.py                # Service container (DI)
│   ├── extensions.py               # Flask extensions (SQLAlchemy, etc.)
│   ├── security.py                 # Security utilities
│   ├── schemas.py                  # Marshmallow validation schemas
│   ├── models/                     # SQLAlchemy models
│   │   ├── user.py
│   │   ├── api_key.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── comparison_result.py
│   ├── routes/                     # API endpoints
│   │   ├── auth.py                 # /api/v1/auth/*
│   │   ├── chat.py                 # /api/v1/chat/* + /api/v1/compare/*
│   │   ├── conversations.py        # /api/v1/conversations/*
│   │   ├── comparisons.py          # /api/v1/comparisons/*
│   │   ├── keys.py                 # /api/v1/keys/*
│   │   └── models.py               # /api/v1/models/*
│   ├── services/                   # Business logic
│   │   ├── llm.py                  # LLMService (invoke, streaming, Azure)
│   │   ├── conversations.py        # ConversationService
│   │   ├── comparisons.py          # ComparisonService
│   │   ├── api_keys.py             # APIKeyService
│   │   └── model_registry.py       # ModelRegistryService
│   └── utils/
│       ├── errors.py
│       └── logging.py
├── src/                            # React frontend
│   ├── App.js                      # Main app component (261 lines, needs refactor)
│   ├── components/
│   │   ├── Header.js
│   │   ├── ComparisonMode.js       # Multi-model comparison
│   │   ├── ModelSelector.js        # Model selection dropdown
│   │   ├── ResponseCard.js         # Individual response display
│   │   ├── ComparisonHistory.js    # History browser
│   │   ├── MessageList.js          # Chat message display
│   │   ├── MessageInput.js         # Chat input
│   │   ├── MarkdownMessage.js      # Markdown renderer
│   │   ├── ApiKeyModal.js          # API key management
│   │   ├── ErrorBoundary.js
│   │   ├── LoadingSkeleton.js
│   │   └── EmptyState.js
│   ├── hooks/
│   │   └── useStreamingComparison.js  # Streaming comparison hook
│   └── services/
│       └── api.js                  # API client
├── tests/                          # Backend tests (12/13 passing, 92%)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_comparisons.py
│   ├── test_llm_service.py
│   └── test_models.py
├── requirements.txt
├── package.json
└── webpack.config.js
```

### Current Performance Metrics (Baseline)
- Page load time: ~2-3 seconds (first load)
- Database queries: Not optimized (no indexes, no pooling)
- Model list fetch: ~200-500ms (API call each time)
- Conversation list: ~100-300ms (no caching)
- Bundle size: 1020 KiB (includes syntax highlighter with 277 languages)
- Test coverage: Backend 92% (12/13 tests), Frontend 0%

### Known Issues
1. **N+1 Queries:** Conversation list may trigger multiple queries
2. **No Caching:** Model registry fetched on every page load
3. **Large Bundle:** Syntax highlighter includes all languages
4. **Monolithic App.js:** 261 lines with complex state management
5. **No Frontend Tests:** Zero test coverage for React components
6. **Connection Pooling:** Not configured for SQLAlchemy
7. **Parallel Same-Provider Calls:** May execute sequentially

---

## 🔧 PART 1: DATABASE & BACKEND PERFORMANCE (WEEK 1)

**Priority:** P1 - High  
**Duration:** 5-7 days  
**Goal:** Achieve < 50ms query times, eliminate N+1 issues, handle concurrent requests efficiently

### 1.1 Database Indexes (Days 1-2)

**Why:** Without indexes, queries scan entire tables. With ~1000 conversations, this becomes slow.

**Tasks:**

#### A. Add Migration File
Create `migrations/002_add_performance_indexes.sql`:

```sql
-- Conversations: User's conversation list (most common query)
CREATE INDEX IF NOT EXISTS idx_conversations_user_created 
ON conversations(user_id, created_at DESC);

-- Messages: Fetch messages for a conversation
CREATE INDEX IF NOT EXISTS idx_messages_conversation 
ON messages(conversation_id, created_at ASC);

-- API Keys: User's keys by provider
CREATE INDEX IF NOT EXISTS idx_apikeys_user_provider 
ON api_keys(user_id, provider);

-- Comparison Results: User's comparison history
CREATE INDEX IF NOT EXISTS idx_comparison_results_user_created 
ON comparison_results(user_id, created_at DESC);

-- Conversations: Provider-specific conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_provider 
ON conversations(user_id, provider);
```

#### B. Update Model Definitions
Add index hints to SQLAlchemy models:

**File:** `llmselect/models/conversation.py`
```python
class Conversation(Base):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_conversations_user_created', 'user_id', 'created_at'),
        Index('idx_conversations_user_provider', 'user_id', 'provider'),
    )
```

**File:** `llmselect/models/message.py`
```python
class Message(Base):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_messages_conversation', 'conversation_id', 'created_at'),
    )
```

**File:** `llmselect/models/api_key.py`
```python
class APIKey(Base):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_apikeys_user_provider', 'user_id', 'provider'),
    )
```

**File:** `llmselect/models/comparison_result.py`
```python
class ComparisonResult(Base):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_comparison_results_user_created', 'user_id', 'created_at'),
    )
```

#### C. Apply Migration
```bash
# Add migration runner if not exists
python scripts/run_migrations.py
```

**Acceptance Criteria:**
- All indexes created successfully
- Query execution plans show index usage (`EXPLAIN` in SQLite)
- Conversation list query < 20ms with 1000 records

---

### 1.2 Connection Pooling (Day 2)

**Why:** Each request creates a new database connection (expensive). Pool reuses connections.

**Tasks:**

#### A. Configure SQLAlchemy Pool
**File:** `llmselect/extensions.py`

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(
    engine_options={
        'pool_size': 10,           # Max connections in pool
        'max_overflow': 20,        # Additional connections when pool full
        'pool_timeout': 30,        # Wait 30s for connection
        'pool_recycle': 3600,      # Recycle connections after 1 hour
        'pool_pre_ping': True,     # Test connection before using
    }
)
```

#### B. Add Pool Monitoring (Optional)
**File:** `llmselect/utils/logging.py`

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    current_app.logger.debug("Database connection opened")

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    current_app.logger.debug("Connection checked out from pool")
```

#### C. Test Connection Pooling
Create test script to verify pooling works:

```python
# scripts/test_connection_pool.py
import concurrent.futures
from llmselect import create_app
from llmselect.models import User

app = create_app()

def query_database(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        return user.id if user else None

# Execute 50 concurrent queries
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(query_database, 1) for _ in range(50)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

print(f"Completed {len(results)} queries successfully")
```

**Acceptance Criteria:**
- Pool size set to 10-20 connections
- Concurrent requests don't fail
- No "database is locked" errors in logs
- Pool metrics logged in debug mode

---

### 1.3 Query Optimization (Days 3-4)

**Why:** Avoid N+1 queries where we fetch conversations, then messages for each conversation individually.

**Tasks:**

#### A. Use Eager Loading for Relationships
**File:** `llmselect/services/conversations.py`

```python
from sqlalchemy.orm import joinedload

class ConversationService:
    def get_user_conversations(self, user_id: int, limit: int = 50, offset: int = 0):
        """Get user's conversations with eager-loaded messages."""
        conversations = (
            Conversation.query
            .filter_by(user_id=user_id)
            .options(joinedload(Conversation.messages))  # Eager load messages
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return conversations
```

#### B. Implement Cursor-Based Pagination
**File:** `llmselect/services/comparisons.py`

```python
class ComparisonService:
    def get_user_comparisons(self, user_id: int, cursor: str = None, limit: int = 20):
        """Get user's comparisons using cursor pagination."""
        query = ComparisonResult.query.filter_by(user_id=user_id)
        
        if cursor:
            # Decode cursor (base64 encoded timestamp)
            import base64
            from datetime import datetime
            cursor_time = datetime.fromisoformat(base64.b64decode(cursor).decode())
            query = query.filter(ComparisonResult.created_at < cursor_time)
        
        comparisons = (
            query
            .order_by(ComparisonResult.created_at.desc())
            .limit(limit + 1)  # Fetch one extra to check for more
            .all()
        )
        
        has_more = len(comparisons) > limit
        if has_more:
            comparisons = comparisons[:limit]
        
        next_cursor = None
        if has_more and comparisons:
            next_cursor = base64.b64encode(
                comparisons[-1].created_at.isoformat().encode()
            ).decode()
        
        return {
            'comparisons': comparisons,
            'next_cursor': next_cursor,
            'has_more': has_more
        }
```

#### C. Add Slow Query Logging
**File:** `llmselect/__init__.py`

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log queries slower than 100ms
        current_app.logger.warning(
            f"Slow query ({total:.2f}s): {statement}",
            extra={'query_time': total, 'statement': statement}
        )
```

**Acceptance Criteria:**
- Conversation list loads in single query (no N+1)
- Pagination works smoothly with cursor approach
- Slow queries (> 100ms) are logged
- All queries < 50ms in production

---

## 🚀 PART 2: RESPONSE CACHING (WEEK 1-2)

**Priority:** P1 - High  
**Duration:** 2-3 days  
**Goal:** Eliminate redundant API calls and database queries with intelligent caching

### 2.1 Install Flask-Caching (Day 5)

#### A. Add Dependency
**File:** `requirements.txt`
```
flask-caching>=2.0.0
```

#### B. Configure Cache Extension
**File:** `llmselect/extensions.py`

```python
from flask_caching import Cache

# Initialize cache
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',  # In-memory (sufficient for demo)
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour default
    'CACHE_THRESHOLD': 500,  # Max 500 items
})

# For production, use Redis:
# cache = Cache(config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_URL': 'redis://localhost:6379/0',
#     'CACHE_DEFAULT_TIMEOUT': 3600,
# })
```

#### C. Initialize in Application Factory
**File:** `llmselect/__init__.py`

```python
from llmselect.extensions import db, cache

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)  # Add cache initialization
    
    return app
```

---

### 2.2 Cache Model Registry (Day 5-6)

**Why:** Model list doesn't change frequently. Cache for 24 hours to avoid repeated API calls.

**File:** `llmselect/services/model_registry.py`

```python
from llmselect.extensions import cache

class ModelRegistryService:
    @cache.cached(timeout=86400, key_prefix='models_list')
    def get_available_models(self):
        """Get list of available models (cached 24 hours)."""
        models = {
            'openai': self._get_openai_models(),
            'anthropic': self._get_anthropic_models(),
            'google': self._get_google_models(),
            'mistral': self._get_mistral_models(),
        }
        return models
    
    @cache.cached(timeout=86400, key_prefix=lambda provider: f'models_{provider}')
    def get_provider_models(self, provider: str):
        """Get models for specific provider (cached 24 hours)."""
        if provider == 'openai':
            return self._get_openai_models()
        elif provider == 'anthropic':
            return self._get_anthropic_models()
        # ... etc
    
    def _get_openai_models(self):
        """Fetch OpenAI models (expensive operation)."""
        # Actual API call here
        pass
```

**Add Cache Invalidation:**
```python
def refresh_models_cache(self):
    """Manually refresh model cache (admin endpoint)."""
    cache.delete('models_list')
    for provider in ['openai', 'anthropic', 'google', 'mistral']:
        cache.delete(f'models_{provider}')
    return self.get_available_models()
```

---

### 2.3 Cache Conversation Lists (Day 6)

**Why:** User's conversation list doesn't change on every page load. Cache for 1 hour, invalidate on updates.

**File:** `llmselect/services/conversations.py`

```python
from llmselect.extensions import cache

class ConversationService:
    def _get_cache_key(self, user_id: int, prefix: str = 'conversations'):
        """Generate cache key for user."""
        return f'{prefix}_{user_id}'
    
    @cache.memoize(timeout=3600)  # 1 hour
    def get_user_conversations(self, user_id: int, limit: int = 50, offset: int = 0):
        """Get user's conversations (cached 1 hour)."""
        conversations = (
            Conversation.query
            .filter_by(user_id=user_id)
            .options(joinedload(Conversation.messages))
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return conversations
    
    def create_conversation(self, user_id: int, provider: str, model: str):
        """Create conversation and invalidate cache."""
        conversation = Conversation(user_id=user_id, provider=provider, model=model)
        db.session.add(conversation)
        db.session.commit()
        
        # Invalidate cache
        cache.delete_memoized(self.get_user_conversations, user_id)
        
        return conversation
    
    def delete_conversation(self, conversation_id: int, user_id: int):
        """Delete conversation and invalidate cache."""
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id
        ).first()
        
        if conversation:
            db.session.delete(conversation)
            db.session.commit()
            
            # Invalidate cache
            cache.delete_memoized(self.get_user_conversations, user_id)
```

---

### 2.4 Add Cache Metrics (Day 6)

**File:** `llmselect/routes/health.py`

```python
from llmselect.extensions import cache

@bp.get("/health")
def health_check():
    """Health check with cache stats."""
    cache_stats = {}
    
    if hasattr(cache.cache, '_cache'):
        cache_stats = {
            'size': len(cache.cache._cache),
            'max_size': cache.cache._threshold,
        }
    
    return {
        'status': 'healthy',
        'database': 'connected',
        'cache': cache_stats,
    }
```

**Acceptance Criteria:**
- Model list loads instantly (< 10ms) after first fetch
- Conversation list cached for 1 hour
- Cache invalidates when conversations created/deleted
- Cache hit/miss logged in debug mode

---

## 🎨 PART 3: FRONTEND ARCHITECTURE REFACTOR (WEEK 2-3)

**Priority:** P1 - High  
**Duration:** 1-2 weeks  
**Goal:** Extract custom hooks, implement Context API, restructure components

### 3.1 Custom Hooks (Days 7-10)

**Why:** App.js is 261 lines with complex state. Extract reusable hooks for cleaner code.

#### A. Create `useAuth` Hook
**File:** `src/hooks/useAuth.js`

```javascript
import { useState, useEffect } from 'react';
import { authApi } from '../services/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await authApi.check();
      setUser(userData);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const userData = await authApi.login(email, password);
      setUser(userData);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const userData = await authApi.register(email, password);
      setUser(userData);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    checkAuth,
  };
};
```

#### B. Create `useChat` Hook
**File:** `src/hooks/useChat.js`

```javascript
import { useState, useCallback } from 'react';
import { chatApi } from '../services/api';

export const useChat = (provider, model) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);

  const sendMessage = useCallback(async (content) => {
    const userMessage = { role: 'user', content, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await chatApi.send({
        provider,
        model,
        message: content,
        conversationId,
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      }]);

      if (response.conversationId) {
        setConversationId(response.conversationId);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [provider, model, conversationId]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    error,
    conversationId,
    sendMessage,
    clearChat,
  };
};
```

#### C. Create `useComparison` Hook
**File:** `src/hooks/useComparison.js`

```javascript
import { useState, useCallback } from 'react';
import { chatApi } from '../services/api';

export const useComparison = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonId, setComparisonId] = useState(null);

  const compare = useCallback(async (prompt, providers) => {
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await chatApi.compare({
        prompt,
        providers,
      });

      setResults(response.results);
      setComparisonId(response.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const vote = useCallback(async (index) => {
    if (!comparisonId) return;

    try {
      await chatApi.voteComparison(comparisonId, index);
    } catch (err) {
      console.error('Vote failed:', err);
    }
  }, [comparisonId]);

  const clear = useCallback(() => {
    setResults([]);
    setComparisonId(null);
    setError(null);
  }, []);

  return {
    results,
    loading,
    error,
    comparisonId,
    compare,
    vote,
    clear,
  };
};
```

#### D. Create `useModels` Hook
**File:** `src/hooks/useModels.js`

```javascript
import { useState, useEffect } from 'react';
import { chatApi } from '../services/api';

export const useModels = (provider = null) => {
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchModels();
  }, [provider]);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const data = await chatApi.getModels(provider);
      setModels(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    models,
    loading,
    error,
    refetch: fetchModels,
  };
};
```

#### E. Create `useApiKeys` Hook
**File:** `src/hooks/useApiKeys.js`

```javascript
import { useState, useCallback } from 'react';
import { chatApi } from '../services/api';

export const useApiKeys = () => {
  const [keys, setKeys] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const saveKey = useCallback(async (provider, apiKey) => {
    setLoading(true);
    setError(null);

    try {
      await chatApi.saveApiKey(provider, apiKey);
      setKeys(prev => ({ ...prev, [provider]: true }));
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const validateKey = useCallback(async (provider, apiKey) => {
    // Could add validation endpoint
    return apiKey && apiKey.length > 10;
  }, []);

  const hasKey = useCallback((provider) => {
    return keys[provider] === true;
  }, [keys]);

  return {
    keys,
    loading,
    error,
    saveKey,
    validateKey,
    hasKey,
  };
};
```

---

### 3.2 Context API (Days 10-11)

#### A. Create App Context
**File:** `src/contexts/AppContext.js`

```javascript
import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [mode, setMode] = useState('chat'); // 'chat' or 'compare'
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');

  const value = {
    mode,
    setMode,
    selectedProvider,
    setSelectedProvider,
    selectedModel,
    setSelectedModel,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
```

#### B. Create Auth Context
**File:** `src/contexts/AuthContext.js`

```javascript
import React, { createContext, useContext } from 'react';
import { useAuth as useAuthHook } from '../hooks/useAuth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const auth = useAuthHook();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

#### C. Create Theme Context (Optional)
**File:** `src/contexts/ThemeContext.js`

```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark'); // Default dark theme

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.body.className = savedTheme;
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.body.className = newTheme;
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

#### D. Update App.js to Use Contexts
**File:** `src/App.js`

```javascript
import React from 'react';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import MainApp from './components/MainApp';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppProvider>
          <MainApp />
        </AppProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
```

---

### 3.3 Component Restructure (Days 11-12)

**Goal:** Organize components into logical folders and simplify App.js

#### A. Create Folder Structure
```
src/
  components/
    chat/
      ChatMode.js          # Chat interface (extract from App.js)
      MessageList.js       # ✅ Already exists
      MessageInput.js      # ✅ Already exists
    comparison/
      ComparisonMode.js    # ✅ Already exists
      ModelSelector.js     # ✅ Already exists
      ResponseCard.js      # ✅ Already exists
      ComparisonHistory.js # ✅ Already exists
    common/
      Header.js            # ✅ Already exists
      Modal.js             # Create generic modal
      Button.js            # Create button component
      LoadingSpinner.js    # ✅ Already exists
      EmptyState.js        # ✅ Already exists
      ErrorBoundary.js     # ✅ Already exists
    MainApp.js             # New: Main app logic (simplified from App.js)
```

#### B. Create MainApp Component
**File:** `src/components/MainApp.js`

```javascript
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import Header from './common/Header';
import ChatMode from './chat/ChatMode';
import ComparisonMode from './comparison/ComparisonMode';
import ApiKeyModal from './ApiKeyModal';
import ErrorBoundary from './common/ErrorBoundary';
import LoadingSkeleton from './common/LoadingSkeleton';

function MainApp() {
  const { user, loading, isAuthenticated } = useAuth();
  const { mode } = useApp();

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <ErrorBoundary>
      <div className="app">
        <Header />
        <main className="main-content">
          {mode === 'chat' ? <ChatMode /> : <ComparisonMode />}
        </main>
        <ApiKeyModal />
      </div>
    </ErrorBoundary>
  );
}

export default MainApp;
```

#### C. Extract ChatMode Component
**File:** `src/components/chat/ChatMode.js`

```javascript
import React from 'react';
import { useApp } from '../../contexts/AppContext';
import { useChat } from '../../hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

function ChatMode() {
  const { selectedProvider, selectedModel } = useApp();
  const { messages, loading, sendMessage, clearChat } = useChat(
    selectedProvider,
    selectedModel
  );

  return (
    <div className="chat-mode">
      <MessageList messages={messages} loading={loading} />
      <MessageInput onSend={sendMessage} disabled={loading} />
    </div>
  );
}

export default ChatMode;
```

**Acceptance Criteria:**
- App.js reduced from 261 lines to < 50 lines
- All state management uses hooks and contexts
- Components organized in logical folders
- No duplicate logic between components

---

## 🧪 PART 4: TESTING INFRASTRUCTURE (WEEK 3-4)

**Priority:** P1 - High  
**Duration:** 1-2 weeks  
**Goal:** Expand backend coverage to >80%, add frontend tests >60%

### 4.1 Backend Testing Expansion (Days 13-15)

**Current Status:** 12/13 tests passing (92%)

#### A. Add Missing Tests
**File:** `tests/test_streaming.py` (NEW)

```python
import pytest
import json
from llmselect import create_app

def test_streaming_endpoint(client, auth_headers):
    """Test /api/v1/compare/stream endpoint."""
    response = client.post(
        '/api/v1/compare/stream',
        headers=auth_headers,
        json={
            'prompt': 'Test prompt',
            'providers': [
                {'provider': 'openai', 'model': 'gpt-4o'},
            ]
        },
        stream=True
    )
    
    assert response.status_code == 200
    assert response.mimetype == 'text/event-stream'
    
    # Parse SSE events
    events = []
    for line in response.iter_lines():
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            events.append(data)
    
    # Should have start, chunk(s), complete, done events
    assert len(events) >= 3
    assert events[0]['event'] == 'start'
    assert events[-1]['event'] == 'done'
```

**File:** `tests/test_caching.py` (NEW)

```python
import pytest
from llmselect.extensions import cache

def test_model_cache(client, auth_headers):
    """Test model list caching."""
    # First request (cache miss)
    response1 = client.get('/api/v1/models', headers=auth_headers)
    assert response1.status_code == 200
    
    # Second request (cache hit, should be faster)
    response2 = client.get('/api/v1/models', headers=auth_headers)
    assert response2.status_code == 200
    assert response1.json == response2.json

def test_cache_invalidation(client, auth_headers):
    """Test cache invalidates on conversation creation."""
    # Get conversations (cache)
    response1 = client.get('/api/v1/conversations', headers=auth_headers)
    count1 = len(response1.json)
    
    # Create conversation
    client.post(
        '/api/v1/conversations',
        headers=auth_headers,
        json={'provider': 'openai', 'model': 'gpt-4o'}
    )
    
    # Get conversations again (cache should be invalidated)
    response2 = client.get('/api/v1/conversations', headers=auth_headers)
    count2 = len(response2.json)
    
    assert count2 == count1 + 1
```

#### B. Add Performance Tests
**File:** `tests/test_performance.py` (NEW)

```python
import pytest
import time

def test_query_performance(client, auth_headers, db_session):
    """Test database query performance."""
    # Create test data
    from llmselect.models import Conversation
    for i in range(100):
        conv = Conversation(user_id=1, provider='openai', model='gpt-4o')
        db_session.add(conv)
    db_session.commit()
    
    # Measure query time
    start = time.time()
    response = client.get('/api/v1/conversations', headers=auth_headers)
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.1  # Should be < 100ms
```

---

### 4.2 Frontend Testing Setup (Days 15-17)

#### A. Install Testing Dependencies
**File:** `package.json`

```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/user-event": "^14.5.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0"
  },
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

#### B. Configure Jest
**File:** `jest.config.js` (NEW)

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/setupTests.js',
  ],
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 60,
      lines: 60,
      statements: 60,
    },
  },
};
```

#### C. Add Test Setup
**File:** `src/setupTests.js` (NEW)

```javascript
import '@testing-library/jest-dom';
```

#### D. Write Component Tests
**File:** `src/components/__tests__/Header.test.js` (NEW)

```javascript
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Header from '../common/Header';
import { AppProvider } from '../../contexts/AppContext';

describe('Header', () => {
  it('renders app title', () => {
    render(
      <AppProvider>
        <Header />
      </AppProvider>
    );
    expect(screen.getByText('LLMSelect')).toBeInTheDocument();
  });

  it('toggles mode on button click', async () => {
    const user = userEvent.setup();
    render(
      <AppProvider>
        <Header />
      </AppProvider>
    );

    const compareButton = screen.getByText('Compare');
    await user.click(compareButton);
    
    // Mode should be 'compare'
    expect(compareButton).toHaveClass('active');
  });
});
```

**File:** `src/hooks/__tests__/useChat.test.js` (NEW)

```javascript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from '../useChat';
import { chatApi } from '../../services/api';

jest.mock('../../services/api');

describe('useChat', () => {
  it('sends message and updates state', async () => {
    chatApi.send.mockResolvedValue({
      response: 'Test response',
      conversationId: '123',
    });

    const { result } = renderHook(() => useChat('openai', 'gpt-4o'));

    act(() => {
      result.current.sendMessage('Test message');
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.messages).toHaveLength(2); // User + assistant
    expect(result.current.messages[1].content).toBe('Test response');
  });
});
```

**Acceptance Criteria:**
- Backend test coverage > 80%
- Frontend test coverage > 60%
- All critical paths tested (auth, chat, comparison, streaming)
- Tests run in CI/CD pipeline

---

## 🗂️ PART 5: CONVERSATION MANAGEMENT UI (WEEK 4)

**Priority:** P2 - Medium  
**Duration:** 3-5 days  
**Goal:** Add sidebar for browsing, searching, and managing conversation history

### 5.1 Backend Support (Day 18)

**Verify existing endpoints work:**
- ✅ `GET /api/v1/conversations` - List user's conversations
- ✅ `DELETE /api/v1/conversations/:id` - Delete conversation
- [ ] Add `PATCH /api/v1/conversations/:id` - Rename conversation

**File:** `llmselect/routes/conversations.py`

```python
@bp.patch("/<int:conversation_id>")
@jwt_required()
@limiter.limit(_rate_limit)
def update_conversation(conversation_id):
    """Update conversation (rename)."""
    payload = request.get_json()
    title = payload.get('title')
    
    if not title or len(title) > 100:
        return {'error': 'Invalid title'}, 400
    
    services = current_app.extensions["services"]
    conversation_service = services.conversations
    
    conversation = conversation_service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        return {'error': 'Conversation not found'}, 404
    
    conversation.title = title
    db.session.commit()
    
    # Invalidate cache
    cache.delete_memoized(conversation_service.get_user_conversations, current_user.id)
    
    return {'id': conversation.id, 'title': conversation.title}
```

---

### 5.2 ConversationSidebar Component (Days 19-20)

**File:** `src/components/chat/ConversationSidebar.js` (NEW)

```javascript
import React, { useState, useEffect } from 'react';
import { chatApi } from '../../services/api';
import ConversationItem from './ConversationItem';

function ConversationSidebar({ onSelectConversation, currentConversationId }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const data = await chatApi.getConversations();
      setConversations(data);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (conversationId) => {
    try {
      await chatApi.deleteConversation(conversationId);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleRename = async (conversationId, newTitle) => {
    try {
      await chatApi.updateConversation(conversationId, { title: newTitle });
      setConversations(prev =>
        prev.map(c => (c.id === conversationId ? { ...c, title: newTitle } : c))
      );
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    }
  };

  const filteredConversations = conversations.filter(c =>
    c.title?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group by date
  const today = [];
  const yesterday = [];
  const older = [];

  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterdayStart = new Date(todayStart);
  yesterdayStart.setDate(yesterdayStart.getDate() - 1);

  filteredConversations.forEach(conv => {
    const createdAt = new Date(conv.created_at);
    if (createdAt >= todayStart) {
      today.push(conv);
    } else if (createdAt >= yesterdayStart) {
      yesterday.push(conv);
    } else {
      older.push(conv);
    }
  });

  return (
    <div className="conversation-sidebar">
      <div className="sidebar-header">
        <h2>Conversations</h2>
        <button className="new-chat-btn" onClick={() => onSelectConversation(null)}>
          + New Chat
        </button>
      </div>

      <div className="search-box">
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="conversation-list">
        {today.length > 0 && (
          <div className="conversation-group">
            <h3>Today</h3>
            {today.map(conv => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                isActive={conv.id === currentConversationId}
                onSelect={() => onSelectConversation(conv.id)}
                onDelete={() => handleDelete(conv.id)}
                onRename={(title) => handleRename(conv.id, title)}
              />
            ))}
          </div>
        )}

        {yesterday.length > 0 && (
          <div className="conversation-group">
            <h3>Yesterday</h3>
            {yesterday.map(conv => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                isActive={conv.id === currentConversationId}
                onSelect={() => onSelectConversation(conv.id)}
                onDelete={() => handleDelete(conv.id)}
                onRename={(title) => handleRename(conv.id, title)}
              />
            ))}
          </div>
        )}

        {older.length > 0 && (
          <div className="conversation-group">
            <h3>Older</h3>
            {older.map(conv => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                isActive={conv.id === currentConversationId}
                onSelect={() => onSelectConversation(conv.id)}
                onDelete={() => handleDelete(conv.id)}
                onRename={(title) => handleRename(conv.id, title)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ConversationSidebar;
```

---

### 5.3 ConversationItem Component (Day 20)

**File:** `src/components/chat/ConversationItem.js` (NEW)

```javascript
import React, { useState } from 'react';

function ConversationItem({ conversation, isActive, onSelect, onDelete, onRename }) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(conversation.title || 'Untitled');
  const [showMenu, setShowMenu] = useState(false);

  const handleRename = () => {
    onRename(title);
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setTitle(conversation.title || 'Untitled');
      setIsEditing(false);
    }
  };

  return (
    <div className={`conversation-item ${isActive ? 'active' : ''}`}>
      {isEditing ? (
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onBlur={handleRename}
          onKeyDown={handleKeyDown}
          autoFocus
        />
      ) : (
        <>
          <div className="conversation-title" onClick={onSelect}>
            {conversation.title || 'Untitled'}
          </div>
          <div className="conversation-menu">
            <button
              className="menu-btn"
              onClick={() => setShowMenu(!showMenu)}
            >
              ⋮
            </button>
            {showMenu && (
              <div className="menu-dropdown">
                <button onClick={() => { setIsEditing(true); setShowMenu(false); }}>
                  Rename
                </button>
                <button onClick={() => { onDelete(); setShowMenu(false); }}>
                  Delete
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default ConversationItem;
```

---

### 5.4 Add Sidebar CSS (Day 20)

**File:** `src/styles.css`

```css
/* Conversation Sidebar */
.app {
  display: flex;
  height: 100vh;
}

.conversation-sidebar {
  width: 260px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h2 {
  font-size: 18px;
  margin: 0;
}

.new-chat-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.new-chat-btn:hover {
  background: var(--primary-hover);
}

.search-box {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--input-bg);
  color: var(--text-color);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-group {
  margin-bottom: 16px;
}

.conversation-group h3 {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin: 8px 12px;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.conversation-item:hover {
  background: var(--hover-bg);
}

.conversation-item.active {
  background: var(--active-bg);
}

.conversation-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.conversation-menu {
  position: relative;
}

.menu-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .menu-btn {
  opacity: 1;
}

.menu-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  background: var(--dropdown-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.menu-dropdown button {
  display: block;
  width: 100%;
  padding: 8px 16px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-color);
}

.menu-dropdown button:hover {
  background: var(--hover-bg);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
```

**Acceptance Criteria:**
- Sidebar displays conversation list grouped by date
- Users can search conversations
- Users can rename conversations (double-click or menu)
- Users can delete conversations
- "New Chat" button starts fresh conversation
- Active conversation highlighted
- Sidebar collapsed on mobile (< 768px)

---

## 📈 SUCCESS METRICS & ACCEPTANCE CRITERIA

### Performance Metrics
- [ ] Page load time < 1 second (from ~2-3s)
- [ ] Model list loads in < 10ms after first fetch (cached)
- [ ] Conversation list loads in < 50ms with indexes
- [ ] Database queries < 50ms for common operations
- [ ] No N+1 query issues detected
- [ ] Bundle size < 600 KiB (from 1020 KiB) via lazy loading

### Code Quality Metrics
- [ ] Backend test coverage > 80% (from 92%)
- [ ] Frontend test coverage > 60% (from 0%)
- [ ] App.js reduced to < 50 lines (from 261)
- [ ] Zero ESLint errors
- [ ] All components use functional patterns (hooks)

### User Experience Metrics
- [ ] Conversation sidebar functional and polished
- [ ] Users can search, rename, delete conversations
- [ ] Frontend architecture uses custom hooks + Context API
- [ ] All state management centralized
- [ ] No prop drilling (Context API in use)

---

## 🛠️ IMPLEMENTATION CHECKLIST

### Week 1: Database & Caching
- [ ] Day 1-2: Add database indexes and test
- [ ] Day 2: Configure connection pooling
- [ ] Day 3-4: Optimize queries (eager loading, cursor pagination)
- [ ] Day 4: Add slow query logging
- [ ] Day 5: Install Flask-Caching
- [ ] Day 5-6: Cache model registry and conversations
- [ ] Day 6: Add cache metrics and invalidation

### Week 2-3: Frontend Refactor
- [ ] Day 7-8: Create useAuth and useChat hooks
- [ ] Day 8-9: Create useComparison and useModels hooks
- [ ] Day 9: Create useApiKeys hook
- [ ] Day 10: Create App and Auth contexts
- [ ] Day 10-11: Create Theme context (optional)
- [ ] Day 11: Restructure component folders
- [ ] Day 11-12: Extract ChatMode and simplify App.js
- [ ] Day 12: Update all components to use hooks/contexts

### Week 3-4: Testing & Sidebar
- [ ] Day 13-14: Add streaming and caching tests
- [ ] Day 14-15: Add performance tests
- [ ] Day 15-16: Set up Jest and React Testing Library
- [ ] Day 16-17: Write component and hook tests
- [ ] Day 17: Achieve coverage goals (>80% backend, >60% frontend)
- [ ] Day 18: Add PATCH endpoint for conversation rename
- [ ] Day 19-20: Build ConversationSidebar and ConversationItem
- [ ] Day 20: Add sidebar CSS and integration
- [ ] Day 21: Final testing and polish

---

## 🚨 RISK MITIGATION

### Risk 1: Cache Invalidation Bugs
**Mitigation:** Write comprehensive cache invalidation tests. Always invalidate on data mutations.

### Risk 2: Frontend Refactor Breaking Changes
**Mitigation:** Extract one hook at a time, test before moving to next. Keep old code until new works.

### Risk 3: Performance Degradation
**Mitigation:** Benchmark before and after changes. Use slow query logging to catch regressions.

### Risk 4: Test Setup Complexity
**Mitigation:** Follow official docs for Jest + RTL setup. Start with simple tests, build complexity gradually.

---

## 📚 RESOURCES & REFERENCES

### Documentation
- Flask-Caching: https://flask-caching.readthedocs.io/
- SQLAlchemy Indexes: https://docs.sqlalchemy.org/en/14/core/constraints.html#indexes
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- Jest: https://jestjs.io/docs/getting-started

### Current Codebase
- Backend Services: `llmselect/services/`
- Frontend Hooks: `src/hooks/useStreamingComparison.js` (example)
- API Client: `src/services/api.js`
- Test Suite: `tests/`

### Key Files to Modify
**Backend:**
- `llmselect/extensions.py` - Add cache, configure pool
- `llmselect/models/*.py` - Add indexes
- `llmselect/services/*.py` - Add caching, optimize queries
- `llmselect/routes/conversations.py` - Add rename endpoint
- `requirements.txt` - Add flask-caching

**Frontend:**
- `src/hooks/` - Create 5 custom hooks
- `src/contexts/` - Create 3 context providers
- `src/components/` - Restructure and simplify
- `src/App.js` - Simplify to < 50 lines
- `package.json` - Add testing dependencies

---

## 🎯 FINAL NOTES

**Phase 4 is about polish and production readiness.** The core features (streaming comparison, markdown rendering, Azure integration) are complete. Focus on:

1. **Performance** - Make it fast and scalable
2. **Architecture** - Make it maintainable and clean
3. **Testing** - Make it reliable and bug-free
4. **UX** - Make it delightful to use

**Don't get sidetracked** by new features. Phase 4 is refactoring and optimization. New features (difference summarizer, voice input, analytics) come in Phases 5-6.

**Measure everything.** Benchmark before and after. Document improvements. Celebrate wins!

---

**Last Updated:** November 6, 2025  
**Next Review:** After Phase 4 completion (estimated 4 weeks)  
**Owner:** @jbuz

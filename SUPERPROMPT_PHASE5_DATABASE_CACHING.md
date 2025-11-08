# SUPERPROMPT: Phase 5 - Database Performance & Response Caching

**Project:** LLMSelect - Multi-LLM Comparison Platform  
**Phase:** 5 (Database Optimization + Caching)  
**Priority:** HIGH - Production Performance  
**Target:** Sub-50ms queries, intelligent caching, production-ready performance  
**Duration:** 1-2 weeks  
**Date:** November 9, 2025

---

## 🎯 EXECUTIVE SUMMARY

Phase 5 focuses on optimizing backend performance through database indexing, connection pooling, and intelligent response caching. Phases 1-4 delivered all core features; now we optimize for production-scale performance.

**What's Complete (✅):**
- Phase 1: Security infrastructure, backend architecture, error handling ✅
- Phase 2: Comparison mode UI, multi-model selector, persistence, voting ✅
- Phase 3: Real-time streaming (SSE), markdown rendering, comparison history ✅
- Phase 4: Azure AI Foundry integration, testing infrastructure documentation ✅

**Phase 5 Goals:**
1. **Database Performance** - Add indexes, optimize queries, implement connection pooling
2. **Response Caching** - Flask-Caching for model registry, conversations, and API responses
3. **Query Optimization** - Eliminate N+1 queries, implement eager loading
4. **Performance Monitoring** - Add slow query logging and metrics

**Success Criteria:**
- Common database queries execute in < 50ms
- No N+1 query issues
- Cache hit rate > 80% for repeated queries
- Connection pool handles concurrent requests efficiently
- Model registry cached (reduces external API calls)

---

## 📋 PART 1: DATABASE OPTIMIZATION

### 1.1 Add Database Indexes 🎯

**Priority:** P0 - Critical  
**Duration:** 2-3 hours  
**Files:** Create `/home/jamesbuzzard/Git/LLMSelect/migrations/002_add_performance_indexes.sql`

**Current State:**
- No indexes on foreign keys
- No indexes on frequently queried columns
- Queries doing full table scans

**Target State:**
- Indexes on all foreign keys
- Indexes on common query patterns
- Sub-50ms query times

**Implementation:**

```sql
-- migrations/002_add_performance_indexes.sql
-- Performance indexes for LLMSelect database
-- Date: November 2025

-- Conversations table indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id_created 
ON conversations(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
ON conversations(user_id);

-- Messages table indexes  
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at 
ON messages(created_at DESC);

-- API Keys table indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id_provider 
ON api_keys(user_id, provider);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id 
ON api_keys(user_id);

-- Comparison Results table indexes
CREATE INDEX IF NOT EXISTS idx_comparison_results_user_id_created 
ON comparison_results(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_comparison_results_user_id 
ON comparison_results(user_id);

-- Users table indexes (if needed)
CREATE INDEX IF NOT EXISTS idx_users_email 
ON users(email) 
WHERE email IS NOT NULL;
```

**Migration Script:**

```python
# scripts/run_migrations.py
import os
import sqlite3
from pathlib import Path

def run_migrations():
    """Run all pending database migrations"""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///instance/llmselect.db').replace('sqlite:///', '')
    migrations_dir = Path(__file__).parent.parent / 'migrations'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create migrations table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Get applied migrations
    cursor.execute('SELECT version FROM schema_migrations')
    applied = {row[0] for row in cursor.fetchall()}
    
    # Apply pending migrations
    for migration_file in sorted(migrations_dir.glob('*.sql')):
        version = migration_file.stem
        if version not in applied:
            print(f'Applying migration: {version}')
            with open(migration_file) as f:
                cursor.executescript(f.read())
            cursor.execute('INSERT INTO schema_migrations (version) VALUES (?)', (version,))
            conn.commit()
            print(f'✓ Applied {version}')
    
    conn.close()
    print('All migrations applied successfully')

if __name__ == '__main__':
    run_migrations()
```

**Testing:**

```bash
# Run migrations
python scripts/run_migrations.py

# Verify indexes were created
sqlite3 instance/llmselect.db ".indexes"

# Test query performance
sqlite3 instance/llmselect.db "EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE user_id = 1 ORDER BY created_at DESC LIMIT 10;"
```

**Acceptance Criteria:**
- [x] All indexes created successfully
- [x] EXPLAIN QUERY PLAN shows index usage
- [x] Query times reduced by >80%
- [x] No breaking changes to existing queries

---

### 1.2 Implement Connection Pooling 🔧

**Priority:** P0 - Critical  
**Duration:** 2-3 hours  
**Files:** `llmselect/config.py`, `llmselect/extensions.py`

**Current State:**
- Default SQLAlchemy settings
- No connection pooling configured
- Potential connection exhaustion under load

**Target State:**
- QueuePool configured (10-20 connections)
- Pool timeout set (30 seconds)
- Connection health checks enabled
- Handles concurrent requests efficiently

**Implementation:**

```python
# llmselect/config.py
import os

class Config:
    """Base configuration"""
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///instance/llmselect.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,                # Normal pool size
        'max_overflow': 10,             # Max connections beyond pool_size
        'pool_timeout': 30,             # Timeout for getting connection
        'pool_recycle': 3600,           # Recycle connections after 1 hour
        'pool_pre_ping': True,          # Test connections before using
        'echo': False,                  # Don't log SQL queries (production)
        'echo_pool': False,             # Don't log pool events
    }
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True,                   # Log SQL queries in dev
        'pool_size': 5,                 # Smaller pool for dev
        'max_overflow': 5,
    }

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 20,                # Larger pool for production
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800,           # More aggressive recycling
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 1,                 # Single connection for tests
        'max_overflow': 0,
        'pool_timeout': 10,
        'pool_pre_ping': False,         # Skip pre-ping in tests
    }
```

**Monitoring Connection Pool:**

```python
# llmselect/routes/health.py
from flask import Blueprint, jsonify
from llmselect.extensions import db

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with DB pool stats"""
    pool = db.engine.pool
    
    return jsonify({
        'status': 'healthy',
        'database': {
            'connected': True,
            'pool_size': pool.size(),
            'checked_out': pool.checked_out_connections,
            'overflow': pool.overflow(),
            'checked_in': pool.size() - pool.checked_out_connections
        }
    })
```

**Testing:**

```bash
# Check pool configuration
python -c "from llmselect import create_app; app = create_app(); print(app.config['SQLALCHEMY_ENGINE_OPTIONS'])"

# Test concurrent connections
python scripts/test_connection_pool.py
```

**Acceptance Criteria:**
- [x] Connection pool configured correctly
- [x] Pool handles concurrent requests
- [x] Connections recycled properly
- [x] Health endpoint shows pool stats

---

### 1.3 Optimize Query Patterns 🚀

**Priority:** P1 - High  
**Duration:** 4-6 hours  
**Files:** `llmselect/services/*.py`

**Current Issues:**
- Potential N+1 queries (loading relationships)
- No eager loading configured
- Inefficient pagination (offset-based)

**Target State:**
- Eager loading for relationships
- Cursor-based pagination for large datasets
- Optimized query patterns

**Implementation:**

```python
# llmselect/services/conversations.py
from sqlalchemy.orm import joinedload
from llmselect.models import Conversation, Message
from llmselect.extensions import db

class ConversationService:
    """Service for managing conversations"""
    
    def get_user_conversations(self, user_id: int, limit: int = 50, cursor: int = None):
        """Get user's conversations with eager loading"""
        query = (
            db.session.query(Conversation)
            .options(
                joinedload(Conversation.messages)  # Eager load messages
            )
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        
        # Cursor-based pagination (more efficient than offset)
        if cursor:
            query = query.filter(Conversation.id < cursor)
        
        conversations = query.limit(limit).all()
        
        return {
            'conversations': [c.to_dict() for c in conversations],
            'next_cursor': conversations[-1].id if len(conversations) == limit else None
        }
    
    def get_conversation_with_messages(self, conversation_id: int, user_id: int):
        """Get single conversation with all messages (eager loaded)"""
        conversation = (
            db.session.query(Conversation)
            .options(
                joinedload(Conversation.messages)
                .joinedload(Message.user)  # Also load message user
            )
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            .first()
        )
        
        return conversation.to_dict() if conversation else None
    
    def get_recent_conversations_count(self, user_id: int) -> int:
        """Efficient count query"""
        return (
            db.session.query(Conversation.id)
            .filter(Conversation.user_id == user_id)
            .count()
        )
```

**Slow Query Logging:**

```python
# llmselect/extensions.py
import logging
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    """Log slow queries (>100ms)"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    """Log slow queries (>100ms)"""
    total_time = time.time() - context._query_start_time
    
    if total_time > 0.1:  # Log queries slower than 100ms
        logger.warning(
            f"Slow query ({total_time:.3f}s): {statement[:200]}",
            extra={
                'duration': total_time,
                'statement': statement,
                'params': params
            }
        )
```

**Testing:**

```python
# tests/test_query_optimization.py
def test_no_n_plus_one_queries(client, auth_headers):
    """Test that conversation list doesn't have N+1 queries"""
    from sqlalchemy import event
    from llmselect.extensions import db
    
    query_count = []
    
    def count_queries(conn, cursor, statement, params, context, executemany):
        query_count.append(statement)
    
    event.listen(db.engine, "before_cursor_execute", count_queries)
    
    # Get conversations
    response = client.get('/api/v1/conversations', headers=auth_headers)
    
    # Should be 1-2 queries max (conversation + messages join)
    assert len(query_count) <= 2
```

**Acceptance Criteria:**
- [x] N+1 queries eliminated
- [x] Eager loading configured
- [x] Cursor-based pagination implemented
- [x] Slow query logging active

---

## 📋 PART 2: RESPONSE CACHING

### 2.1 Implement Flask-Caching 💾

**Priority:** P0 - Critical  
**Duration:** 3-4 hours  
**Files:** `llmselect/extensions.py`, `llmselect/config.py`

**Current State:**
- No caching implemented
- Every request hits database
- Repeated model registry fetches

**Target State:**
- Flask-Caching with SimpleCache (in-memory)
- Model registry cached (24-hour TTL)
- Conversation lists cached (5-minute TTL)
- Cache hit rate >80%

**Implementation:**

```python
# requirements.txt
Flask-Caching==2.1.0
```

```python
# llmselect/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

db = SQLAlchemy()
cache = Cache()

def init_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    cache.init_app(app)
```

```python
# llmselect/config.py
class Config:
    """Base configuration"""
    # Cache configuration
    CACHE_TYPE = 'SimpleCache'  # In-memory cache
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default
    CACHE_THRESHOLD = 1000      # Max 1000 cached items
    CACHE_KEY_PREFIX = 'llmselect_'

class DevelopmentConfig(Config):
    """Development configuration"""
    CACHE_DEFAULT_TIMEOUT = 60  # Shorter TTL in dev

class TestingConfig(Config):
    """Testing configuration"""
    CACHE_TYPE = 'NullCache'  # Disable cache in tests
```

```python
# llmselect/__init__.py
from llmselect.extensions import db, cache, init_extensions

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    config_class = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }[config_name]
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    return app
```

**Acceptance Criteria:**
- [x] Flask-Caching installed and configured
- [x] Cache working in dev/prod
- [x] Cache disabled in tests

---

### 2.2 Cache Model Registry 🤖

**Priority:** P0 - Critical  
**Duration:** 2-3 hours  
**Files:** `llmselect/services/llm_service.py`

**Current State:**
- Model registry fetched on every request
- External API calls for model lists
- No caching of model information

**Target State:**
- Model registry cached for 24 hours
- Reduced external API calls
- Faster model selection

**Implementation:**

```python
# llmselect/services/llm_service.py
from llmselect.extensions import cache

class LLMService:
    """Service for LLM interactions"""
    
    @cache.cached(timeout=86400, key_prefix='model_registry')
    def get_model_registry(self):
        """Get available models (cached for 24 hours)"""
        return {
            'openai': self._get_openai_models(),
            'anthropic': self._get_anthropic_models(),
            'google': self._get_google_models(),
            'mistral': self._get_mistral_models()
        }
    
    @cache.memoize(timeout=86400)
    def get_provider_models(self, provider: str):
        """Get models for specific provider (cached)"""
        registry = self.get_model_registry()
        return registry.get(provider, [])
    
    def clear_model_cache(self):
        """Clear model registry cache (admin only)"""
        cache.delete('model_registry')
        cache.delete_memoized(self.get_provider_models)
```

**Cache Invalidation Endpoint:**

```python
# llmselect/routes/admin.py
from flask import Blueprint
from llmselect.services.llm_service import LLMService
from llmselect.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@bp.route('/cache/clear', methods=['POST'])
@admin_required
def clear_cache():
    """Clear all caches (admin only)"""
    llm_service = LLMService()
    llm_service.clear_model_cache()
    
    return jsonify({'message': 'Cache cleared successfully'})
```

**Acceptance Criteria:**
- [x] Model registry cached for 24 hours
- [x] Cache invalidation endpoint works
- [x] External API calls reduced by >90%

---

### 2.3 Cache Conversation Lists 📝

**Priority:** P1 - High  
**Duration:** 2-3 hours  
**Files:** `llmselect/services/conversations.py`, `llmselect/routes/chat.py`

**Current State:**
- Conversation lists fetched from DB on every request
- No caching for user's conversation history

**Target State:**
- Conversation lists cached for 5 minutes
- Cache invalidated on new conversation/message
- Faster conversation loading

**Implementation:**

```python
# llmselect/services/conversations.py
from llmselect.extensions import cache

class ConversationService:
    """Service for managing conversations"""
    
    @cache.memoize(timeout=300)  # 5 minutes
    def get_user_conversations_cached(self, user_id: int, limit: int = 50):
        """Get user's conversations with caching"""
        return self.get_user_conversations(user_id, limit)
    
    def create_conversation(self, user_id: int, title: str = None):
        """Create conversation and invalidate cache"""
        conversation = Conversation(user_id=user_id, title=title)
        db.session.add(conversation)
        db.session.commit()
        
        # Invalidate user's conversation cache
        self._invalidate_user_cache(user_id)
        
        return conversation
    
    def add_message(self, conversation_id: int, role: str, content: str):
        """Add message and invalidate cache"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        
        # Invalidate conversation cache
        conversation = Conversation.query.get(conversation_id)
        self._invalidate_user_cache(conversation.user_id)
        
        return message
    
    def _invalidate_user_cache(self, user_id: int):
        """Invalidate all caches for a user"""
        cache.delete_memoized(
            self.get_user_conversations_cached,
            self,
            user_id
        )
```

**Cache Headers in Responses:**

```python
# llmselect/routes/chat.py
@bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get user's conversations with cache headers"""
    user_id = get_jwt_identity()
    conversations = conversation_service.get_user_conversations_cached(user_id)
    
    response = jsonify(conversations)
    response.cache_control.max_age = 300  # Cache for 5 minutes
    response.cache_control.public = True
    
    return response
```

**Acceptance Criteria:**
- [x] Conversation lists cached for 5 minutes
- [x] Cache invalidated on mutations
- [x] Response times improved by >70%

---

### 2.4 Cache API Responses 🔄

**Priority:** P2 - Medium  
**Duration:** 2-3 hours  
**Files:** `llmselect/routes/*.py`

**Current State:**
- No HTTP response caching
- Repeated identical requests hit backend

**Target State:**
- Cache GET endpoints appropriately
- ETags for conditional requests
- Proper cache control headers

**Implementation:**

```python
# llmselect/decorators.py
from functools import wraps
from flask import request, jsonify, make_response
import hashlib
import json

def cached_response(timeout=300):
    """Decorator to cache API responses with ETags"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key from URL + args
            cache_key = f'response:{request.path}:{json.dumps(request.args.to_dict())}'
            
            # Check if cached
            cached = cache.get(cache_key)
            
            if cached:
                # Generate ETag from cached content
                etag = hashlib.md5(json.dumps(cached).encode()).hexdigest()
                
                # Check if client has same version
                if request.headers.get('If-None-Match') == etag:
                    return make_response('', 304)  # Not Modified
                
                response = make_response(jsonify(cached))
                response.headers['ETag'] = etag
                response.headers['Cache-Control'] = f'max-age={timeout}'
                return response
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result.get_json(), timeout=timeout)
            
            return result
        
        return decorated_function
    return decorator
```

**Usage:**

```python
# llmselect/routes/chat.py
@bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@login_required
@cached_response(timeout=300)
def get_conversation(conversation_id):
    """Get conversation with caching"""
    user_id = get_jwt_identity()
    conversation = conversation_service.get_conversation_with_messages(
        conversation_id, 
        user_id
    )
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify(conversation)
```

**Acceptance Criteria:**
- [x] GET endpoints cached appropriately
- [x] ETags support conditional requests
- [x] Cache headers set correctly

---

## 📊 PERFORMANCE MONITORING

### 3.1 Add Performance Metrics 📈

**Implementation:**

```python
# llmselect/middleware/performance.py
import time
import logging
from flask import request, g

logger = logging.getLogger(__name__)

def init_performance_monitoring(app):
    """Initialize performance monitoring"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            
            # Log slow requests (>500ms)
            if elapsed > 0.5:
                logger.warning(
                    f"Slow request: {request.method} {request.path} ({elapsed:.3f}s)",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration': elapsed,
                        'status': response.status_code
                    }
                )
            
            # Add timing header
            response.headers['X-Response-Time'] = f'{elapsed:.3f}s'
        
        return response
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Database Optimization
- [ ] Create migrations/002_add_performance_indexes.sql
- [ ] Run migration script
- [ ] Verify indexes with EXPLAIN QUERY PLAN
- [ ] Configure connection pooling in config.py
- [ ] Add health endpoint with pool stats
- [ ] Optimize query patterns in services
- [ ] Add eager loading with joinedload
- [ ] Implement cursor-based pagination
- [ ] Add slow query logging
- [ ] Test query performance improvements

### Response Caching
- [ ] Install Flask-Caching
- [ ] Configure cache in config.py
- [ ] Initialize cache in extensions.py
- [ ] Cache model registry (24h TTL)
- [ ] Add cache invalidation endpoint
- [ ] Cache conversation lists (5m TTL)
- [ ] Invalidate cache on mutations
- [ ] Add cached_response decorator
- [ ] Add ETags support
- [ ] Set proper cache headers

### Performance Monitoring
- [ ] Add performance middleware
- [ ] Log slow queries (>100ms)
- [ ] Log slow requests (>500ms)
- [ ] Add X-Response-Time header
- [ ] Monitor cache hit rates

### Testing
- [ ] Test database indexes improve query speed
- [ ] Test connection pool under load
- [ ] Test cache hit rates
- [ ] Test cache invalidation
- [ ] Load test with concurrent users

---

## 🎯 SUCCESS CRITERIA

**Performance Targets:**
- [ ] Common database queries < 50ms
- [ ] Page load time < 1 second
- [ ] Cache hit rate > 80%
- [ ] No N+1 query issues
- [ ] Connection pool handles 50+ concurrent requests

**Code Quality:**
- [ ] All new code has tests
- [ ] No breaking changes
- [ ] Documentation updated
- [ ] Performance metrics logged

---

## 📚 NEXT STEPS

After Phase 5 completion:
1. **Phase 6**: Frontend architecture refactor (custom hooks, Context API)
2. **Phase 7**: Mobile optimization and UX polish
3. **Phase 8**: Advanced features (export, analytics, voice input)

---

**Ready to implement! Let's optimize performance! 🚀**

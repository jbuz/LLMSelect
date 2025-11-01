# Code Improvement Backlog

This document tracks non-urgent refactoring, technical debt, and code quality improvements. These items are not blocking current features but should be addressed over time to maintain code health.

**Priority Levels:**
- 🟢 **Low**: Nice-to-have improvements
- 🟡 **Medium**: Should address when working in related area
- 🔴 **High**: Should address soon to prevent issues

---

## Backend Improvements

### 🟡 Add Type Hints to All Functions
**Category:** Code Quality  
**Effort:** 2-3 days  
**Files:** All Python files in `llmselect/`

**Current State:**
Some functions lack type hints, making code less maintainable and harder for IDEs to analyze.

**Proposed:**
```python
# Current
def invoke(self, provider, model, messages, api_key):
    pass

# Improved
def invoke(
    self,
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    api_key: str
) -> str:
    pass
```

**Benefits:**
- Better IDE autocomplete and error detection
- Self-documenting code
- Enables mypy static type checking
- Easier refactoring

---

### 🟡 Add Docstrings to All Public Methods
**Category:** Documentation  
**Effort:** 3-4 days  
**Files:** All Python files in `llmselect/`

**Current State:**
Many methods lack docstrings explaining their purpose, parameters, and return values.

**Proposed:**
Use Google-style docstrings consistently:
```python
def invoke(self, provider: str, model: str, messages: List[Dict], api_key: str) -> str:
    """Send a chat request to the specified LLM provider.
    
    Args:
        provider: The LLM provider identifier (e.g., 'openai', 'anthropic')
        model: The model identifier for the provider
        messages: List of message dictionaries with 'role' and 'content' keys
        api_key: API key for authentication with the provider
        
    Returns:
        The model's response as a string
        
    Raises:
        ValueError: If provider is not supported
        requests.RequestException: If API request fails
    """
    pass
```

---

### 🟢 Extract Magic Numbers to Constants
**Category:** Maintainability  
**Effort:** 1 day  
**Files:** `llmselect/config.py`, various service files

**Current State:**
Some hardcoded values are scattered throughout code (timeouts, retry counts, etc.)

**Proposed:**
```python
# llmselect/constants.py
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 0.5
MAX_TOKENS_DEFAULT = 1000
RATE_LIMIT_DEFAULT = "60 per minute"
```

---

### 🟡 Improve Error Message Consistency
**Category:** User Experience  
**Effort:** 2 days  
**Files:** All route files

**Current State:**
Error messages have inconsistent formats and detail levels.

**Proposed:**
Create error message constants and standardize format:
```python
# llmselect/errors.py
ERROR_MESSAGES = {
    'auth_failed': 'Authentication failed. Please check your credentials.',
    'invalid_provider': 'Provider {provider} is not supported.',
    'rate_limit_exceeded': 'Rate limit exceeded. Please try again in {seconds} seconds.',
    'api_key_missing': 'API key for {provider} not configured.',
}
```

---

### 🟢 Add Request/Response Logging Middleware
**Category:** Observability  
**Effort:** 1-2 days  
**Files:** `llmselect/__init__.py`

**Current State:**
Request/response logging is ad-hoc and inconsistent.

**Proposed:**
Create Flask middleware for standardized request/response logging with timing, status codes, and sanitized payloads.

---

### 🟡 Implement Health Check Dependencies
**Category:** Monitoring  
**Effort:** 1 day  
**Files:** `llmselect/routes/health.py`

**Current State:**
Health check only returns basic status, doesn't verify dependencies.

**Proposed:**
```python
@bp.get('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {
            'database': check_database(),
            'redis': check_redis() if REDIS_ENABLED else 'disabled',
        },
        'version': VERSION,
    })
```

---

## Frontend Improvements

### 🔴 Extract Custom Hooks
**Category:** Architecture  
**Effort:** 3-4 days  
**Files:** `src/App.js`, new files in `src/hooks/`

**Current State:**
App.js contains all state management logic (261 lines), making it hard to maintain and test.

**Proposed:**
Extract hooks:
- `useAuth.js`: Login, logout, register, user state
- `useChat.js`: Messages, sendMessage, clearChat
- `useComparison.js`: Compare, results, history
- `useApiKeys.js`: Save, validate keys
- `useModels.js`: Model list, selection

**Benefits:**
- Reusable logic
- Easier testing
- Smaller components
- Better separation of concerns

---

### 🔴 Implement Context API
**Category:** Architecture  
**Effort:** 2-3 days  
**Files:** New `src/contexts/` directory

**Current State:**
Props are drilled through multiple component layers.

**Proposed:**
```javascript
// src/contexts/AppContext.js
const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('dark');
  
  return (
    <AppContext.Provider value={{ user, setUser, theme, setTheme }}>
      {children}
    </AppContext.Provider>
  );
};
```

---

### 🟡 Add PropTypes or TypeScript Interfaces
**Category:** Type Safety  
**Effort:** 2-3 days  
**Files:** All React component files

**Current State:**
No prop validation in React components.

**Proposed:**
Add PropTypes to all components:
```javascript
import PropTypes from 'prop-types';

MessageList.propTypes = {
  messages: PropTypes.arrayOf(PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.string,
  })).isRequired,
  isLoading: PropTypes.bool,
};
```

**Alternative:** Migrate to TypeScript for full type safety.

---

### 🟢 Extract Reusable UI Components
**Category:** Maintainability  
**Effort:** 2 days  
**Files:** New `src/components/common/` directory

**Current State:**
Common UI patterns (buttons, inputs, modals) are duplicated.

**Proposed:**
Create reusable components:
- `Button.js`: Standardized button with variants
- `Input.js`: Form input with validation
- `Modal.js`: Base modal component
- `LoadingSpinner.js`: Loading indicator
- `ErrorMessage.js`: Error display component

---

### 🟡 Implement Error Boundary
**Category:** User Experience  
**Effort:** 1 day  
**Files:** New `src/components/ErrorBoundary.js`

**Current State:**
No global error handling for React errors.

**Proposed:**
```javascript
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('React error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

---

### 🟢 Add Loading States and Skeletons
**Category:** User Experience  
**Effort:** 2-3 days  
**Files:** Various component files

**Current State:**
Simple loading spinners, no skeleton screens.

**Proposed:**
Implement skeleton loaders for better perceived performance during loading states.

---

## Testing Improvements

### 🔴 Add Frontend Test Suite
**Category:** Quality  
**Effort:** 1-2 weeks  
**Priority:** HIGH (currently 0% frontend coverage)

**Proposed:**
- Set up Jest + React Testing Library
- Write tests for all components
- Write tests for custom hooks
- Add integration tests
- Target: 80%+ coverage

---

### 🟡 Improve Backend Test Coverage
**Category:** Quality  
**Effort:** 1 week  
**Current Coverage:** ~30%  
**Target:** 90%+

**Areas Needing Tests:**
- LLM service provider-specific tests
- Error handling paths
- Authentication edge cases
- Rate limiting enforcement
- Encryption/decryption edge cases

---

### 🟢 Add E2E Tests
**Category:** Quality  
**Effort:** 1 week  
**Files:** New `e2e/` directory

**Proposed:**
Use Playwright to test critical user flows:
- User registration and login
- API key configuration
- Sending chat messages
- Comparing models
- Error scenarios

---

## Performance Improvements

### 🟡 Implement Response Caching
**Category:** Performance  
**Effort:** 3-4 days  
**Files:** New caching service, updated LLM service

**Current State:**
Every request hits LLM APIs, even for identical prompts.

**Proposed:**
- Add Redis for caching
- Cache responses with TTL (1 hour)
- Implement cache invalidation
- Add cache statistics endpoint

**Benefits:**
- Faster response times
- Reduced API costs
- Better user experience

---

### 🟢 Bundle Optimization
**Category:** Performance  
**Effort:** 2-3 days  
**Files:** `webpack.config.js`, various component files

**Current State:**
Single bundle with all dependencies, no code splitting.

**Proposed:**
- Configure code splitting
- Lazy load routes and heavy components
- Separate vendor bundles
- Enable tree shaking
- Optimize images and assets

---

### 🟢 Add Performance Monitoring
**Category:** Observability  
**Effort:** 2 days  
**Files:** Frontend monitoring setup

**Proposed:**
- Track Web Vitals (LCP, FID, CLS)
- Monitor API response times
- Track LLM provider latency
- Add performance dashboard

---

## Documentation Improvements

### 🟡 Add API Documentation (OpenAPI/Swagger)
**Category:** Documentation  
**Effort:** 2-3 days  
**Files:** New `docs/openapi.yaml`

**Current State:**
API documented only in README.

**Proposed:**
Create OpenAPI specification with all endpoints, schemas, and examples.

---

### 🟢 Add Architecture Decision Records (ADRs)
**Category:** Documentation  
**Effort:** Ongoing  
**Files:** New `docs/adr/` directory

**Proposed:**
Document architectural decisions as they're made:
- ADR-0001: Application Factory Pattern
- ADR-0002: JWT Authentication
- ADR-0003: Per-User API Key Encryption
- ADR-0004: Service Layer Architecture

---

### 🟢 Create Developer Onboarding Guide
**Category:** Documentation  
**Effort:** 2 days  
**Files:** New `docs/ONBOARDING.md`

**Proposed:**
Step-by-step guide for new developers covering:
- Development environment setup
- Architecture overview
- Code patterns and conventions
- Testing strategy
- Deployment process

---

## Infrastructure Improvements

### 🟡 Add CI/CD Pipeline
**Category:** DevOps  
**Effort:** 3-4 days  
**Files:** `.github/workflows/`

**Current State:**
No automated CI/CD (being added as part of security work).

**Proposed:**
- Linting and formatting checks
- Test execution
- Security scanning
- Build verification
- Automated deployment (production)

---

### 🟢 Add Dependency Update Automation
**Category:** Maintenance  
**Effort:** 1 day  
**Files:** `.github/dependabot.yml`

**Current State:**
Manual dependency updates.

**Proposed:**
- Enable Dependabot
- Configure update frequency
- Set up auto-merge for patches
- Group updates by type

---

### 🟢 Add Docker Production Configuration
**Category:** Deployment  
**Effort:** 2 days  
**Files:** `Dockerfile.production`, `docker-compose.production.yml`

**Current State:**
Dockerfile exists but may need production hardening.

**Proposed:**
- Multi-stage builds
- Non-root user
- Security scanning in build
- Optimized layer caching
- Health check configuration

---

## Prioritization Guidelines

When to address each priority level:

### 🔴 High Priority
- Address within current or next sprint
- Blocking future work or causing technical debt
- Examples: Frontend architecture, test coverage

### 🟡 Medium Priority
- Address when working in related code
- Include in quarterly planning
- Examples: Type hints, documentation

### 🟢 Low Priority
- Address during slack time or hack days
- Nice-to-have improvements
- Examples: Performance optimizations, additional monitoring

---

## How to Use This Document

1. **Review quarterly**: Assess which items should be promoted to active backlog
2. **Add new items**: When identifying technical debt, add to appropriate section
3. **Update status**: Mark items as complete when addressed
4. **Link to issues**: Create GitHub issues for items being actively worked on

---

**Last Updated**: October 31, 2025  
**Next Review**: January 31, 2026

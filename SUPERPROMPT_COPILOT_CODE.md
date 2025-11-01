# Superprompt: Phase 2 - Comparison Mode Implementation

**Target:** GitHub Copilot Autonomous Coding Agent  
**Date:** November 1, 2025  
**Phase:** Phase 2 - Core Comparison Experience  
**Priority:** P0 - CRITICAL  
**Estimated Duration:** 2-3 weeks

---

## Mission Statement

Implement the comparison mode UI - the core value proposition of LLMSelect. This feature enables users to compare multiple LLM responses side-by-side from a single prompt. The backend `/api/v1/compare` endpoint exists but has zero frontend implementation.

**Success Criteria:**
- Users can select 2-4 models simultaneously
- Side-by-side response display with synchronized scrolling
- Response metadata visible (time, tokens, cost estimate)
- Comparison results persisted to database
- Ability to vote on preferred responses
- Export comparisons as Markdown or JSON

---

## Context & Constraints

### What Exists ✅
- **Backend:** Complete `/api/v1/compare` endpoint with multi-model support
- **Backend:** LLM service supports OpenAI, Anthropic, Gemini, Mistral
- **Backend:** JWT authentication, CSRF protection, rate limiting
- **Backend:** Database models for User, APIKey, Conversation, Message
- **Frontend:** Basic React app with chat interface (single model only)
- **Frontend:** API key management modal
- **Frontend:** Message history display

### What's Missing 🔴
- **Frontend:** No comparison mode UI at all
- **Frontend:** No multi-model selector
- **Backend:** No persistence of comparison results
- **Backend:** No voting/preference tracking
- **Frontend:** No response metadata display
- **Frontend:** No comparison history view

### Architecture Context
- **Backend:** Flask 2.3.3, SQLAlchemy, Flask-JWT-Extended
- **Frontend:** React 18.2.0, Axios, js-cookie
- **Build:** Webpack 5.x
- **Testing:** pytest (backend), no frontend tests yet
- **Security:** All secrets encrypted, CSRF tokens required

### Critical Files to Review First
1. `PRIORITIES_SUMMARY.md` - Overall priorities and assessment
2. `backlog.md` - Detailed Phase 2 requirements (lines 100-250)
3. `llmselect/routes/chat.py` - Existing `/api/v1/compare` endpoint
4. `llmselect/services/llm.py` - Multi-provider LLM service
5. `src/App.js` - Current frontend implementation (261 lines)
6. `ROADMAP.md` - 8-phase strategic plan

---

## Security & Quality Requirements (NON-NEGOTIABLE)

### Security First (P0)
- ✅ All new endpoints must require JWT authentication
- ✅ CSRF tokens required for all POST requests
- ✅ Input validation using Marshmallow schemas
- ✅ No secrets in code or logs
- ✅ Rate limiting on new endpoints
- ✅ SQL injection prevention (use ORM)
- ✅ XSS prevention (React handles most, but validate on backend)

### Code Quality
- ✅ Follow existing patterns (service layer, dependency injection)
- ✅ Black formatting for Python (max line length 100)
- ✅ Type hints on all new Python functions
- ✅ PropTypes or TypeScript for React components
- ✅ Unit tests for business logic
- ✅ Integration tests for API endpoints
- ✅ No breaking changes to existing endpoints

### Documentation
- ✅ Update CHANGELOG.md with all changes
- ✅ Add entries to DECISIONS.md for architectural choices
- ✅ Update README if user-facing changes
- ✅ Docstrings on all new functions
- ✅ Code comments for complex logic

---

## Phase 2 Implementation Plan

### 🎯 Part 1: Backend - Comparison Persistence (Week 1, Days 1-3)

**Goal:** Enable saving and retrieving comparison results

#### 1.1 Create ComparisonResult Model
**File:** `llmselect/models/comparison.py` (NEW)

```python
from sqlalchemy.dialects.postgresql import JSONB
from ..extensions import db
from .base import TimestampMixin

class ComparisonResult(db.Model, TimestampMixin):
    """Stores comparison results for analysis and history."""
    __tablename__ = 'comparison_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    
    # Store results as JSON: [{"provider": "openai", "model": "gpt-4", "response": "...", "time": 1.2, "tokens": 245}, ...]
    results = db.Column(db.JSON, nullable=False)
    
    # Optional: User's preference (model index or null)
    preferred_index = db.Column(db.Integer, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('comparisons', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'results': self.results,
            'preferred_index': self.preferred_index,
            'created_at': self.created_at.isoformat(),
        }
```

**Tasks:**
- [ ] Create model file with proper relationships
- [ ] Add migration script (Alembic or manual SQL)
- [ ] Add `to_dict()` serialization method
- [ ] Update `llmselect/models/__init__.py` to export new model

#### 1.2 Create Comparison Service
**File:** `llmselect/services/comparisons.py` (NEW)

```python
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models import ComparisonResult, User

class ComparisonService:
    """Business logic for comparison management."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def save_comparison(
        self, 
        user_id: int, 
        prompt: str, 
        results: List[Dict]
    ) -> ComparisonResult:
        """Save a comparison result."""
        comparison = ComparisonResult(
            user_id=user_id,
            prompt=prompt,
            results=results
        )
        self.db.add(comparison)
        self.db.commit()
        return comparison
    
    def get_user_comparisons(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ComparisonResult]:
        """Get comparison history for a user."""
        return ComparisonResult.query.filter_by(user_id=user_id)\
            .order_by(ComparisonResult.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    def vote_preference(
        self, 
        comparison_id: int, 
        user_id: int, 
        preferred_index: int
    ) -> ComparisonResult:
        """Record user's preference for a specific model's response."""
        comparison = ComparisonResult.query.filter_by(
            id=comparison_id, 
            user_id=user_id
        ).first_or_404()
        
        comparison.preferred_index = preferred_index
        self.db.commit()
        return comparison
```

**Tasks:**
- [ ] Create service class with CRUD operations
- [ ] Add to service container in `llmselect/container.py`
- [ ] Add unit tests for service methods
- [ ] Handle edge cases (empty results, invalid user_id)

#### 1.3 Update Compare Endpoint
**File:** `llmselect/routes/chat.py`

**Current endpoint** (lines 80-120):
```python
@bp.post("/compare")
@limiter.limit("10 per minute")
@jwt_required()
def compare():
    # Existing code validates input and calls LLM service
    # Returns: {"results": [...], "prompt": "..."}
```

**Update to**:
```python
@bp.post("/compare")
@limiter.limit("10 per minute")
@jwt_required()
def compare():
    # ... existing validation code ...
    
    # Call LLM service (existing)
    results = []
    for request in payload["requests"]:
        result = services.llm.invoke(...)
        results.append({
            "provider": request["provider"],
            "model": request["model"],
            "response": result,
            "time": elapsed_time,
            "tokens": estimate_tokens(result)
        })
    
    # NEW: Save to database
    comparison = services.comparisons.save_comparison(
        user_id=current_user.id,
        prompt=payload["messages"][-1]["content"],
        results=results
    )
    
    return jsonify({
        "id": comparison.id,  # NEW: Return comparison ID
        "results": results,
        "prompt": payload["messages"][-1]["content"]
    })
```

**Tasks:**
- [ ] Add comparison service injection
- [ ] Update endpoint to save results
- [ ] Add timing measurement per model
- [ ] Add token estimation function
- [ ] Update API response schema
- [ ] Add integration test

#### 1.4 Add Comparison History Endpoints
**File:** `llmselect/routes/comparisons.py` (NEW)

```python
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from ..extensions import limiter
from ..container import get_services

bp = Blueprint('comparisons', __name__, url_prefix='/api/v1/comparisons')

@bp.get('')
@limiter.limit("60 per minute")
@jwt_required()
def list_comparisons():
    """Get user's comparison history."""
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    services = get_services()
    comparisons = services.comparisons.get_user_comparisons(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return jsonify({
        'comparisons': [c.to_dict() for c in comparisons],
        'limit': limit,
        'offset': offset
    })

@bp.post('/<int:comparison_id>/vote')
@limiter.limit("60 per minute")
@jwt_required()
def vote_on_comparison(comparison_id: int):
    """Record preferred model for a comparison."""
    data = request.get_json()
    preferred_index = data.get('preferred_index')
    
    if preferred_index is None or not isinstance(preferred_index, int):
        raise AppError("Invalid preferred_index")
    
    services = get_services()
    comparison = services.comparisons.vote_preference(
        comparison_id=comparison_id,
        user_id=current_user.id,
        preferred_index=preferred_index
    )
    
    return jsonify(comparison.to_dict())
```

**Tasks:**
- [ ] Create new blueprint
- [ ] Register blueprint in `llmselect/__init__.py`
- [ ] Add input validation schemas
- [ ] Add pagination support
- [ ] Add integration tests
- [ ] Update API documentation

---

### 🎨 Part 2: Frontend - Comparison UI (Week 1-2, Days 4-10)

**Goal:** Build side-by-side comparison interface

#### 2.1 Create ModelSelector Component
**File:** `src/components/ModelSelector.js` (NEW)

```javascript
import React, { useState } from 'react';

const AVAILABLE_MODELS = [
  { provider: 'openai', model: 'gpt-4', label: 'GPT-4', color: '#10a37f' },
  { provider: 'openai', model: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo', color: '#10a37f' },
  { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', color: '#d97757' },
  { provider: 'anthropic', model: 'claude-3-opus-20240229', label: 'Claude 3 Opus', color: '#d97757' },
  { provider: 'google', model: 'gemini-pro', label: 'Gemini Pro', color: '#4285f4' },
  { provider: 'mistral', model: 'mistral-large-latest', label: 'Mistral Large', color: '#f2a73b' },
];

export default function ModelSelector({ selected, onChange, maxModels = 4 }) {
  const [isOpen, setIsOpen] = useState(false);
  
  const handleToggle = (model) => {
    const isSelected = selected.some(s => 
      s.provider === model.provider && s.model === model.model
    );
    
    if (isSelected) {
      onChange(selected.filter(s => 
        !(s.provider === model.provider && s.model === model.model)
      ));
    } else if (selected.length < maxModels) {
      onChange([...selected, model]);
    }
  };
  
  return (
    <div className="model-selector">
      <div className="selected-models">
        {selected.map((model, idx) => (
          <div 
            key={`${model.provider}-${model.model}`} 
            className="model-chip"
            style={{ borderColor: model.color }}
          >
            <span>{model.label}</span>
            <button 
              onClick={() => handleToggle(model)}
              className="remove-btn"
            >
              ×
            </button>
          </div>
        ))}
        
        {selected.length < maxModels && (
          <button 
            onClick={() => setIsOpen(!isOpen)}
            className="add-model-btn"
          >
            + Add Model
          </button>
        )}
      </div>
      
      {isOpen && (
        <div className="model-dropdown">
          {AVAILABLE_MODELS
            .filter(m => !selected.some(s => 
              s.provider === m.provider && s.model === m.model
            ))
            .map(model => (
              <button
                key={`${model.provider}-${model.model}`}
                onClick={() => {
                  handleToggle(model);
                  setIsOpen(false);
                }}
                className="model-option"
              >
                <span 
                  className="model-indicator" 
                  style={{ backgroundColor: model.color }}
                />
                {model.label}
              </button>
            ))
          }
        </div>
      )}
    </div>
  );
}
```

**Tasks:**
- [ ] Create component with multi-select logic
- [ ] Add chip-style selected models display
- [ ] Add dropdown for available models
- [ ] Group models by provider
- [ ] Add max selection limit (2-4 models)
- [ ] Style with existing CSS patterns
- [ ] Add PropTypes validation

#### 2.2 Create ResponseCard Component
**File:** `src/components/ResponseCard.js` (NEW)

```javascript
import React, { useState } from 'react';

export default function ResponseCard({ 
  provider, 
  model, 
  response, 
  metadata, 
  onVote,
  isPreferred 
}) {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = async () => {
    await navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <div className={`response-card ${isPreferred ? 'preferred' : ''}`}>
      <div className="response-header">
        <div className="model-info">
          <h3>{model}</h3>
          <span className="provider-badge">{provider}</span>
        </div>
        
        <div className="metadata">
          {metadata.time && (
            <span className="meta-item">
              ⏱️ {metadata.time.toFixed(1)}s
            </span>
          )}
          {metadata.tokens && (
            <span className="meta-item">
              📊 {metadata.tokens} tokens
            </span>
          )}
          {metadata.cost && (
            <span className="meta-item">
              💰 ${metadata.cost.toFixed(4)}
            </span>
          )}
        </div>
      </div>
      
      <div className="response-content">
        <pre>{response}</pre>
      </div>
      
      <div className="response-actions">
        <button 
          onClick={handleCopy}
          className="action-btn"
          title="Copy response"
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
        
        <button
          onClick={() => onVote('up')}
          className={`action-btn vote-btn ${isPreferred ? 'active' : ''}`}
          title="Prefer this response"
        >
          👍 Prefer
        </button>
      </div>
    </div>
  );
}
```

**Tasks:**
- [ ] Create card layout component
- [ ] Display response with proper formatting
- [ ] Show metadata (time, tokens, cost)
- [ ] Add copy-to-clipboard functionality
- [ ] Add vote/preference buttons
- [ ] Add loading skeleton state
- [ ] Style with CSS grid for layout
- [ ] Add PropTypes validation

#### 2.3 Create ComparisonMode Component
**File:** `src/components/ComparisonMode.js` (NEW)

```javascript
import React, { useState } from 'react';
import ModelSelector from './ModelSelector';
import ResponseCard from './ResponseCard';
import MessageInput from './MessageInput';
import { api } from '../services/api';

export default function ComparisonMode() {
  const [selectedModels, setSelectedModels] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonId, setComparisonId] = useState(null);
  const [preferredIndex, setPreferredIndex] = useState(null);
  
  const handleCompare = async () => {
    if (!prompt.trim() || selectedModels.length < 2) {
      setError('Please enter a prompt and select at least 2 models');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await api.post('/compare', {
        requests: selectedModels.map(m => ({
          provider: m.provider,
          model: m.model
        })),
        messages: [{ role: 'user', content: prompt }]
      });
      
      setResults(response.data.results);
      setComparisonId(response.data.id);
    } catch (err) {
      setError(err.response?.data?.message || 'Comparison failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleVote = async (index) => {
    if (!comparisonId) return;
    
    try {
      await api.post(`/comparisons/${comparisonId}/vote`, {
        preferred_index: index
      });
      setPreferredIndex(index);
    } catch (err) {
      console.error('Vote failed:', err);
    }
  };
  
  return (
    <div className="comparison-mode">
      <div className="comparison-controls">
        <ModelSelector
          selected={selectedModels}
          onChange={setSelectedModels}
          maxModels={4}
        />
        
        <MessageInput
          value={prompt}
          onChange={setPrompt}
          onSubmit={handleCompare}
          placeholder="Enter your prompt to compare models..."
          disabled={isLoading || selectedModels.length < 2}
          submitLabel="🔄 Compare"
        />
      </div>
      
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}
      
      {isLoading && (
        <div className="loading-state">
          <div className="spinner" />
          <p>Comparing {selectedModels.length} models...</p>
        </div>
      )}
      
      {results && (
        <div className="comparison-results">
          <div className="results-grid" style={{
            gridTemplateColumns: `repeat(${results.length}, 1fr)`
          }}>
            {results.map((result, idx) => (
              <ResponseCard
                key={idx}
                provider={result.provider}
                model={result.model}
                response={result.response}
                metadata={{
                  time: result.time,
                  tokens: result.tokens,
                  cost: result.cost
                }}
                onVote={() => handleVote(idx)}
                isPreferred={preferredIndex === idx}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

**Tasks:**
- [ ] Create main comparison component
- [ ] Integrate ModelSelector and ResponseCard
- [ ] Handle API calls to `/api/v1/compare`
- [ ] Show loading states per model
- [ ] Handle errors gracefully
- [ ] Add synchronized scrolling (optional)
- [ ] Add export functionality (optional)
- [ ] Style with responsive grid layout
- [ ] Add PropTypes validation

#### 2.4 Update App.js with Mode Switching
**File:** `src/App.js`

**Current structure** (simplified):
```javascript
function App() {
  const [mode, setMode] = useState('chat'); // NEW
  // ... existing state ...
  
  return (
    <div>
      <Header 
        mode={mode} 
        onModeChange={setMode}  // NEW
      />
      
      {mode === 'chat' ? (
        // Existing chat interface
        <div className="chat-mode">
          {/* ... existing chat UI ... */}
        </div>
      ) : (
        // NEW comparison mode
        <ComparisonMode />
      )}
    </div>
  );
}
```

**Tasks:**
- [ ] Add mode state ('chat' | 'compare')
- [ ] Add mode toggle in Header component
- [ ] Conditionally render ComparisonMode or chat UI
- [ ] Preserve chat history when switching modes
- [ ] Add URL routing (optional: /chat vs /compare)
- [ ] Update CSS for new layout

#### 2.5 Add Comparison History View (Optional)
**File:** `src/components/ComparisonHistory.js` (NEW)

```javascript
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ComparisonHistory({ onSelect }) {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    loadHistory();
  }, []);
  
  const loadHistory = async () => {
    try {
      const response = await api.get('/comparisons', {
        params: { limit: 20 }
      });
      setHistory(response.data.comparisons);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="comparison-history">
      <h2>Recent Comparisons</h2>
      
      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : (
        <ul className="history-list">
          {history.map(item => (
            <li 
              key={item.id} 
              onClick={() => onSelect(item)}
              className="history-item"
            >
              <div className="prompt-preview">
                {item.prompt.substring(0, 80)}...
              </div>
              <div className="history-meta">
                <span>{item.results.length} models</span>
                <span>{new Date(item.created_at).toLocaleDateString()}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**Tasks:**
- [ ] Create history list component
- [ ] Fetch comparison history from API
- [ ] Display prompt preview and metadata
- [ ] Add click handler to reload comparison
- [ ] Add pagination if needed
- [ ] Style as sidebar or dropdown

---

### 🎨 Part 3: Styling & Polish (Week 2, Days 11-14)

#### 3.1 CSS Updates
**File:** `src/styles.css`

**Add sections for:**
```css
/* Comparison Mode Layout */
.comparison-mode { }
.comparison-controls { }
.comparison-results { }
.results-grid { 
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* Model Selector */
.model-selector { }
.selected-models { }
.model-chip { }
.model-dropdown { }

/* Response Cards */
.response-card { }
.response-card.preferred { }
.response-header { }
.response-content { }
.response-actions { }

/* Loading States */
.loading-state { }
.spinner { }

/* Mode Toggle */
.mode-toggle { }
.mode-toggle button.active { }

/* Responsive Design */
@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
}
```

**Tasks:**
- [ ] Design comparison grid layout
- [ ] Style model selector chips
- [ ] Style response cards with borders
- [ ] Add loading animations
- [ ] Make responsive for mobile
- [ ] Add dark mode support (optional)
- [ ] Ensure WCAG AA compliance

#### 3.2 Error Handling & Edge Cases
**Tasks:**
- [ ] Handle API key missing for selected provider
- [ ] Show per-model errors if one fails
- [ ] Handle rate limiting gracefully
- [ ] Show connection errors
- [ ] Add retry logic for failed requests
- [ ] Validate prompt length (max tokens)
- [ ] Handle empty responses

---

### 🧪 Part 4: Testing (Week 3, Days 15-18)

#### 4.1 Backend Tests
**File:** `tests/test_comparisons.py` (NEW)

```python
def test_save_comparison_requires_auth(client):
    """Comparison endpoint requires authentication."""
    response = client.post('/api/v1/compare', json={})
    assert response.status_code == 401

def test_compare_saves_to_database(client, app):
    """Comparison results are persisted."""
    register_and_login(client)
    
    response = client.post('/api/v1/compare', json={
        'requests': [
            {'provider': 'openai', 'model': 'gpt-4'},
            {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-20241022'}
        ],
        'messages': [{'role': 'user', 'content': 'Test prompt'}]
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    
    # Verify saved to database
    with app.app_context():
        comparison = ComparisonResult.query.get(data['id'])
        assert comparison is not None
        assert comparison.prompt == 'Test prompt'
        assert len(comparison.results) == 2

def test_get_comparison_history(client):
    """Users can retrieve comparison history."""
    register_and_login(client)
    
    # Create some comparisons
    for i in range(3):
        client.post('/api/v1/compare', json={...})
    
    # Get history
    response = client.get('/api/v1/comparisons')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['comparisons']) == 3

def test_vote_on_comparison(client):
    """Users can vote for preferred response."""
    register_and_login(client)
    
    # Create comparison
    compare_response = client.post('/api/v1/compare', json={...})
    comparison_id = compare_response.get_json()['id']
    
    # Vote
    vote_response = client.post(
        f'/api/v1/comparisons/{comparison_id}/vote',
        json={'preferred_index': 0}
    )
    assert vote_response.status_code == 200
    assert vote_response.get_json()['preferred_index'] == 0
```

**Tasks:**
- [ ] Add unit tests for ComparisonService
- [ ] Add integration tests for comparison endpoints
- [ ] Add tests for vote functionality
- [ ] Test pagination
- [ ] Test error scenarios
- [ ] Achieve 90%+ coverage for new code

#### 4.2 Frontend Tests (Optional but Recommended)
**Files:** `src/components/__tests__/*.test.js` (NEW)

```javascript
// ModelSelector.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import ModelSelector from '../ModelSelector';

test('allows selecting up to max models', () => {
  const onChange = jest.fn();
  render(<ModelSelector selected={[]} onChange={onChange} maxModels={2} />);
  
  // Open dropdown
  fireEvent.click(screen.getByText('+ Add Model'));
  
  // Select first model
  fireEvent.click(screen.getByText('GPT-4'));
  expect(onChange).toHaveBeenCalledTimes(1);
  
  // Select second model
  fireEvent.click(screen.getByText('Claude 3.5 Sonnet'));
  expect(onChange).toHaveBeenCalledTimes(2);
  
  // Should not allow third model
  fireEvent.click(screen.getByText('+ Add Model'));
  expect(screen.queryByText('Gemini Pro')).not.toBeInTheDocument();
});
```

**Tasks:**
- [ ] Set up Jest + React Testing Library
- [ ] Test ModelSelector selection logic
- [ ] Test ResponseCard rendering
- [ ] Test ComparisonMode API calls
- [ ] Mock API responses
- [ ] Test error states
- [ ] Test loading states
- [ ] Achieve 80%+ coverage for new components

---

### 📝 Part 5: Documentation & Finalization (Week 3, Days 19-21)

#### 5.1 Update Documentation
**Tasks:**
- [ ] Update CHANGELOG.md with Phase 2 changes
- [ ] Add entries to DECISIONS.md for:
  - Why JSON storage for comparison results
  - Why grid layout over tabs
  - Model selection UI decisions
- [ ] Update README.md with:
  - Comparison mode usage instructions
  - Screenshots or GIF demos
  - New API endpoints
- [ ] Update API documentation (if separate)
- [ ] Add inline code comments

#### 5.2 Code Review Checklist
**Before marking complete:**
- [ ] All tests passing (backend + frontend)
- [ ] Linting passing (Black, Flake8, ESLint)
- [ ] No console errors or warnings
- [ ] Security audit (no secrets, CSRF works, auth required)
- [ ] Performance check (comparison under 30s for 4 models)
- [ ] Mobile responsive (test on small screens)
- [ ] Browser compatibility (Chrome, Firefox, Safari)
- [ ] Accessibility audit (keyboard navigation, screen readers)

#### 5.3 Database Migration
**File:** `migrations/add_comparison_results.sql` (NEW)

```sql
-- Add comparison_results table
CREATE TABLE IF NOT EXISTS comparison_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    results JSON NOT NULL,
    preferred_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_comparison_user ON comparison_results(user_id);
CREATE INDEX idx_comparison_created ON comparison_results(created_at);
```

**Tasks:**
- [ ] Create migration file
- [ ] Test migration on fresh database
- [ ] Test migration on existing database
- [ ] Add rollback script
- [ ] Document migration in README

---

## Decision Making Framework

When encountering ambiguity, use this framework:

### 1. Security Decisions
**Default:** Always choose the most secure option
- Require authentication? → YES
- Validate input? → YES
- Rate limit? → YES
- Log sensitive data? → NO

### 2. UX Decisions
**Default:** Optimize for user experience
- Show loading state? → YES
- Handle errors gracefully? → YES
- Provide feedback? → YES
- Make user wait? → NO

### 3. Architecture Decisions
**Default:** Follow existing patterns
- Use service layer? → YES (existing pattern)
- Use Marshmallow for validation? → YES (existing pattern)
- Create new file vs. modify existing? → NEW if logically separate
- Document in DECISIONS.md? → YES

### 4. Testing Decisions
**Default:** Test critical paths
- Test happy path? → YES
- Test error cases? → YES
- Test authentication? → YES
- Test every edge case? → Only if time permits

---

## Rollback & Reversibility

### Database Changes
- Keep migration files for rollback
- Test rollback before deploying
- Document rollback procedure

### API Changes
- No breaking changes to existing endpoints
- `/api/v1/compare` response format can be extended but not changed
- New endpoints can be removed without impact

### Frontend Changes
- Mode toggle allows reverting to chat-only UI
- Feature flag possible: `ENABLE_COMPARISON_MODE=true/false`
- CSS namespaced under `.comparison-mode` for easy removal

---

## Success Metrics

### Phase 2 Complete When:
- [ ] Users can select 2-4 models and compare responses
- [ ] Results display side-by-side with metadata
- [ ] Comparisons are saved to database
- [ ] Users can view comparison history
- [ ] Users can vote on preferred responses
- [ ] All tests passing (90%+ backend, 80%+ frontend)
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated
- [ ] CI/CD passing

### Phase 2 Excellence When (Stretch Goals):
- [ ] Synchronized scrolling between response cards
- [ ] Export comparison as Markdown or PDF
- [ ] Comparison statistics (most used models, win rates)
- [ ] Keyboard shortcuts for voting
- [ ] Markdown rendering in responses
- [ ] Syntax highlighting for code blocks

---

## Resources & References

### Critical Documentation
1. **PRIORITIES_SUMMARY.md** - Overall priorities
2. **backlog.md** - Detailed requirements
3. **ROADMAP.md** - 8-phase strategic plan
4. **CONTRIBUTING.md** - Development guidelines
5. **SECURITY.md** - Security policy

### API Endpoints Reference
```
POST   /api/v1/compare              - Compare multiple models (existing)
GET    /api/v1/comparisons          - Get comparison history (new)
POST   /api/v1/comparisons/:id/vote - Vote on comparison (new)
```

### Technology Stack
- **Backend:** Flask 2.3.3, SQLAlchemy, Flask-JWT-Extended
- **Frontend:** React 18.2.0, Axios, js-cookie
- **Database:** SQLite (dev), PostgreSQL (production)
- **Testing:** pytest, Jest, React Testing Library
- **Build:** Webpack 5.x

### External Services
- **OpenAI API:** GPT-4, GPT-3.5 Turbo
- **Anthropic API:** Claude 3.5 Sonnet, Claude 3 Opus
- **Google AI API:** Gemini Pro
- **Mistral AI API:** Mistral Large

---

## Getting Help

### When Blocked
1. **Check existing code:** Similar patterns likely exist
2. **Read DECISIONS.md:** Past decisions documented
3. **Review tests:** Show expected behavior
4. **Check ROADMAP.md:** May have additional context
5. **Use feature flags:** Ship partial work, iterate

### Communication
- **Log decisions:** Always add to DECISIONS.md
- **Update CHANGELOG:** Track all changes
- **Document trade-offs:** Explain why in comments
- **Ask for clarification:** Better to ask than assume

---

## Final Notes

**Remember:**
- Security is P0 - never compromise
- Follow existing patterns - consistency matters
- Test as you go - don't leave it for later
- Document decisions - help future developers
- Small PRs - easier to review and revert
- User experience - make it delightful

**When in doubt:**
- Choose the secure option
- Follow the existing pattern
- Add tests
- Document the decision
- Ask for review

**This is Phase 2 of 8 - stay focused!**

The goal is comparison mode UI, not perfection. Deliver value, iterate quickly, and move to streaming responses (Phase 3) once users can compare models.

---

**Good luck! 🚀**

*This superprompt is designed for GitHub Copilot Autonomous Coding Agent but can be used by any developer implementing Phase 2.*

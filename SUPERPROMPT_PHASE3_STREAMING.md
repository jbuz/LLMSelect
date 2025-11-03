# SUPERPROMPT: Phase 3 - Real-Time Streaming Comparison Implementation

**Priority**: P0 - CRITICAL  
**Duration**: 2 weeks (Days 1-14)  
**Success Criteria**: Multiple models stream simultaneously in real-time with <1s time to first token

---

## Executive Summary

Implement real-time streaming capabilities for the multi-model comparison feature to eliminate the 20-60 second wait time users currently experience. This phase adds Server-Sent Events (SSE) streaming for all 4 LLM providers, frontend EventSource integration, markdown rendering with syntax highlighting, and a comparison history UI component.

**Key Deliverables**:
1. Backend streaming infrastructure with SSE endpoint `/api/v1/compare/stream`
2. Parallel streaming for 4 LLM providers (OpenAI, Anthropic, Gemini, Mistral)
3. Frontend streaming hook (`useStreamingComparison`) with EventSource integration
4. Markdown rendering with syntax highlighting and copy buttons
5. Comparison history UI component
6. Comprehensive documentation updates

---

## Part 1: Backend Streaming Infrastructure (Days 1-3)

### 1.1 SSE Endpoint Implementation

**File**: `llmselect/routes/chat.py`

**Add new endpoint**:
```python
@bp.post("/compare/stream")
@jwt_required()
@limiter.limit(_rate_limit)
def compare_stream():
    """Stream comparison results from multiple providers in real-time using SSE."""
    payload = compare_schema.load(request.get_json() or {})
    prompt = payload["prompt"]
    providers = payload["providers"]
    
    services = current_app.extensions["services"]
    llm_service = services.llm
    comparison_service = services.comparisons
    encryption_service = current_app.extensions["key_encryption"]
    user = current_user
    
    def generate():
        """Generator function for SSE stream."""
        results = {}
        completed_count = 0
        total_providers = len(providers)
        
        # Send initial event
        yield f"data: {json.dumps({'event': 'start', 'total': total_providers})}\n\n"
        
        with ThreadPoolExecutor(max_workers=len(providers)) as executor:
            futures = {}
            for entry in providers:
                provider_name = entry["provider"]
                model = entry["model"]
                futures[
                    executor.submit(
                        _stream_provider,
                        encryption_service,
                        llm_service,
                        user,
                        provider_name,
                        model,
                        [{"role": "user", "content": prompt}],
                    )
                ] = (provider_name, model)
            
            # Process results as they complete
            for future in as_completed(futures):
                provider_name, model = futures[future]
                try:
                    for chunk in future.result():
                        # Stream each chunk
                        yield f"data: {json.dumps(chunk)}\n\n"
                        
                        # Track completion
                        if chunk.get('event') == 'complete':
                            completed_count += 1
                            if provider_name not in results:
                                results[provider_name] = chunk.get('data', {})
                            
                except Exception as exc:
                    current_app.logger.error(
                        f"Provider {provider_name} streaming failed",
                        extra={
                            "provider": provider_name,
                            "model": model,
                            "error": str(exc),
                        },
                    )
                    yield f"data: {json.dumps({
                        'event': 'error',
                        'provider': provider_name,
                        'model': model,
                        'error': 'Streaming failed. Please check your API key and try again.'
                    })}\n\n"
                    completed_count += 1
        
        # Save comparison to database after all streams complete
        if results:
            comparison = comparison_service.save_comparison(
                user_id=user.id,
                prompt=prompt,
                results=[
                    {
                        'provider': provider,
                        'model': data.get('model', ''),
                        'response': data.get('response', ''),
                        'time': data.get('time', 0),
                        'tokens': data.get('tokens', 0),
                    }
                    for provider, data in results.items()
                ]
            )
            yield f"data: {json.dumps({
                'event': 'done',
                'comparisonId': comparison.id
            })}\n\n"
        else:
            yield f"data: {json.dumps({'event': 'done'})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


def _stream_provider(encryption_service, llm_service, user, provider, model, messages):
    """Stream results from a single provider."""
    try:
        api_key = get_api_key(user, provider, encryption_service)
        start_time = time()
        
        # Send start event for this provider
        yield {
            'event': 'chunk',
            'provider': provider,
            'model': model,
            'chunk': '',
            'time': 0,
        }
        
        full_response = ''
        first_chunk = True
        
        # Stream from provider
        for chunk in llm_service.invoke_stream(provider, model, messages, api_key):
            full_response += chunk
            elapsed = time() - start_time
            
            yield {
                'event': 'chunk',
                'provider': provider,
                'model': model,
                'chunk': chunk,
                'time': elapsed,
                'first_chunk': first_chunk,
            }
            first_chunk = False
        
        # Send completion event
        elapsed_time = time() - start_time
        yield {
            'event': 'complete',
            'provider': provider,
            'model': model,
            'data': {
                'provider': provider,
                'model': model,
                'response': full_response,
                'time': elapsed_time,
                'tokens': _estimate_tokens(full_response),
            }
        }
        
    except Exception as exc:
        current_app.logger.error(
            f"Provider {provider} streaming failed: {exc}",
            extra={'provider': provider, 'model': model, 'error': str(exc)}
        )
        raise
```

### 1.2 LLM Service Streaming Methods

**File**: `llmselect/services/llm.py`

**Add streaming methods for each provider**:

```python
def invoke_stream(self, provider: str, model: str, messages: list, api_key: str):
    """Stream response from LLM provider.
    
    Yields:
        str: Chunks of the response as they arrive
    """
    if provider == "openai":
        yield from self._stream_openai(model, messages, api_key)
    elif provider == "anthropic":
        yield from self._stream_anthropic(model, messages, api_key)
    elif provider == "google":
        yield from self._stream_google(model, messages, api_key)
    elif provider == "mistral":
        yield from self._stream_mistral(model, messages, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _stream_openai(self, model: str, messages: list, api_key: str):
    """Stream response from OpenAI API."""
    import openai
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=self.max_tokens,
            temperature=0.7,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        self.logger.error(f"OpenAI streaming error: {e}")
        raise


def _stream_anthropic(self, model: str, messages: list, api_key: str):
    """Stream response from Anthropic Claude API."""
    import anthropic
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Convert messages format
    system_message = None
    claude_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_message = msg["content"]
        else:
            claude_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    try:
        with client.messages.stream(
            model=model,
            messages=claude_messages,
            system=system_message or "",
            max_tokens=self.max_tokens,
        ) as stream:
            for text in stream.text_stream:
                yield text
                
    except Exception as e:
        self.logger.error(f"Anthropic streaming error: {e}")
        raise


def _stream_google(self, model: str, messages: list, api_key: str):
    """Stream response from Google Gemini API."""
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    # Convert messages to Gemini format
    prompt_parts = []
    for msg in messages:
        role = "user" if msg["role"] in ["user", "system"] else "model"
        prompt_parts.append({"role": role, "parts": [msg["content"]]})
    
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(
            prompt_parts,
            stream=True,
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        self.logger.error(f"Google streaming error: {e}")
        raise


def _stream_mistral(self, model: str, messages: list, api_key: str):
    """Stream response from Mistral API."""
    from mistralai.client import MistralClient
    
    client = MistralClient(api_key=api_key)
    
    try:
        stream = client.chat_stream(
            model=model,
            messages=messages,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        self.logger.error(f"Mistral streaming error: {e}")
        raise
```

### 1.3 Testing

**File**: `tests/test_streaming.py` (NEW)

```python
"""Tests for streaming endpoints."""
import json
from unittest.mock import MagicMock, patch

import pytest


def test_compare_stream_endpoint(client, app, monkeypatch):
    """Test SSE streaming endpoint."""
    from tests.conftest import register_and_login
    
    register_and_login(client)
    
    # Mock streaming responses
    def fake_stream(provider, model, messages, api_key):
        if provider == "openai":
            yield "Hello"
            yield " world"
            yield "!"
        elif provider == "anthropic":
            yield "Greetings"
            yield " from"
            yield " Claude"
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke_stream", fake_stream)
    
    response = client.post(
        "/api/v1/compare/stream",
        json={
            "prompt": "Say hello",
            "providers": [
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
        },
    )
    
    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"
    
    # Parse SSE events
    events = []
    for line in response.data.decode().split('\n'):
        if line.startswith('data: '):
            events.append(json.loads(line[6:]))
    
    # Verify events
    assert len(events) > 0
    assert events[0]['event'] == 'start'
    
    # Check for chunk events
    chunk_events = [e for e in events if e.get('event') == 'chunk']
    assert len(chunk_events) > 0
    
    # Check for completion
    done_events = [e for e in events if e.get('event') == 'done']
    assert len(done_events) == 1


def test_stream_handles_provider_errors(client, app, monkeypatch):
    """Test streaming handles individual provider failures gracefully."""
    from tests.conftest import register_and_login
    
    register_and_login(client)
    
    def fake_stream(provider, model, messages, api_key):
        if provider == "openai":
            yield "Success"
        else:
            raise Exception("Provider error")
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke_stream", fake_stream)
    
    response = client.post(
        "/api/v1/compare/stream",
        json={
            "prompt": "Test",
            "providers": [
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
        },
    )
    
    assert response.status_code == 200
    
    events = []
    for line in response.data.decode().split('\n'):
        if line.startswith('data: '):
            events.append(json.loads(line[6:]))
    
    # Should have error event for failed provider
    error_events = [e for e in events if e.get('event') == 'error']
    assert len(error_events) > 0
    
    # Should still complete
    done_events = [e for e in events if e.get('event') == 'done']
    assert len(done_events) == 1
```

---

## Part 2: Frontend Streaming UI (Days 4-6)

### 2.1 Streaming Hook

**File**: `src/hooks/useStreamingComparison.js` (NEW)

```javascript
import { useState, useCallback, useRef } from 'react';

export const useStreamingComparison = (chatApi) => {
  const [streamingResults, setStreamingResults] = useState({});
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonId, setComparisonId] = useState(null);
  const eventSourceRef = useRef(null);
  const streamingDataRef = useRef({});

  const startStreaming = useCallback(async (prompt, selectedModels) => {
    if (!prompt.trim() || selectedModels.length < 2) {
      setError('Please enter a prompt and select at least 2 models');
      return;
    }

    // Reset state
    setIsStreaming(true);
    setError(null);
    setStreamingResults({});
    setComparisonId(null);
    streamingDataRef.current = {};

    // Initialize streaming results for each model
    const initialResults = {};
    selectedModels.forEach(model => {
      const key = `${model.provider}_${model.model}`;
      initialResults[key] = {
        provider: model.provider,
        model: model.model,
        label: model.label,
        color: model.color,
        response: '',
        time: 0,
        tokens: 0,
        streaming: true,
        error: false,
      };
      streamingDataRef.current[key] = initialResults[key];
    });
    setStreamingResults(initialResults);

    try {
      // Create EventSource for SSE
      const token = localStorage.getItem('access_token');
      const url = new URL('/api/v1/compare/stream', window.location.origin);
      
      // Send POST request to initiate stream
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          prompt,
          providers: selectedModels.map(m => ({
            provider: m.provider,
            model: m.model,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start streaming');
      }

      // Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              handleStreamEvent(data);
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

    } catch (err) {
      console.error('Streaming error:', err);
      setError('Streaming failed. Please try again.');
      setIsStreaming(false);
    }
  }, []);

  const handleStreamEvent = useCallback((data) => {
    const { event, provider, model, chunk, time, first_chunk, error: eventError, comparisonId: cId } = data;

    if (event === 'start') {
      // Stream started
      console.log('Stream started:', data);
    } else if (event === 'chunk' && provider) {
      // Update streaming response
      const key = `${provider}_${model}`;
      
      setStreamingResults(prev => {
        const current = prev[key] || streamingDataRef.current[key];
        const updated = {
          ...current,
          response: current.response + (chunk || ''),
          time: time || current.time,
          streaming: true,
        };
        streamingDataRef.current[key] = updated;
        return {
          ...prev,
          [key]: updated,
        };
      });
      
      // Mark first chunk received
      if (first_chunk) {
        console.log(`First chunk received from ${provider} at ${time}s`);
      }
    } else if (event === 'complete' && provider) {
      // Provider completed
      const key = `${provider}_${model}`;
      const completedData = data.data || {};
      
      setStreamingResults(prev => {
        const updated = {
          ...prev[key],
          ...completedData,
          streaming: false,
        };
        streamingDataRef.current[key] = updated;
        return {
          ...prev,
          [key]: updated,
        };
      });
    } else if (event === 'error' && provider) {
      // Provider error
      const key = `${provider}_${model}`;
      
      setStreamingResults(prev => {
        const updated = {
          ...prev[key],
          response: eventError || 'Provider request failed',
          error: true,
          streaming: false,
        };
        streamingDataRef.current[key] = updated;
        return {
          ...prev,
          [key]: updated,
        };
      });
    } else if (event === 'done') {
      // All providers completed
      setIsStreaming(false);
      if (cId) {
        setComparisonId(cId);
      }
    }
  }, []);

  const cancelStreaming = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    streamingResults: Object.values(streamingResults),
    isStreaming,
    error,
    comparisonId,
    startStreaming,
    cancelStreaming,
  };
};
```

### 2.2 Update ComparisonMode Component

**File**: `src/components/ComparisonMode.js`

Update to use the streaming hook:

```javascript
import React, { useState } from 'react';
import ModelSelector from './ModelSelector';
import ResponseCard from './ResponseCard';
import MessageInput from './MessageInput';
import { useStreamingComparison } from '../hooks/useStreamingComparison';

export default function ComparisonMode({ chatApi }) {
  const [selectedModels, setSelectedModels] = useState([
    { provider: 'openai', model: 'gpt-4', label: 'GPT-4', color: '#10a37f' },
    { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', color: '#d97757' },
  ]);
  
  const {
    streamingResults,
    isStreaming,
    error,
    comparisonId,
    startStreaming,
    cancelStreaming,
  } = useStreamingComparison(chatApi);
  
  const [preferredIndex, setPreferredIndex] = useState(null);
  
  const handleCompare = async (content) => {
    await startStreaming(content, selectedModels);
  };
  
  const handleVote = async (index) => {
    if (!comparisonId) return;
    
    try {
      await chatApi.voteComparison(comparisonId, { preferred_index: index });
      setPreferredIndex(index);
    } catch (err) {
      console.error('Vote failed:', err);
    }
  };
  
  // ... rest of component
  
  return (
    <div className="comparison-mode">
      {/* Model selector */}
      <ModelSelector
        selectedModels={selectedModels}
        onModelChange={setSelectedModels}
        maxModels={4}
      />
      
      {/* Error display */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {/* Results grid */}
      {streamingResults.length > 0 && (
        <div className="results-grid" style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${Math.min(streamingResults.length, 2)}, 1fr)`,
          gap: '1rem',
          marginTop: '1rem',
        }}>
          {streamingResults.map((result, index) => (
            <ResponseCard
              key={`${result.provider}_${result.model}`}
              result={result}
              index={index}
              onVote={handleVote}
              isPreferred={preferredIndex === index}
              isStreaming={result.streaming}
            />
          ))}
        </div>
      )}
      
      {/* Message input */}
      <MessageInput
        onSendMessage={handleCompare}
        isLoading={isStreaming}
        onCancel={isStreaming ? cancelStreaming : undefined}
        placeholder="Enter your prompt to compare models..."
      />
    </div>
  );
}
```

---

## Part 3: Message Rendering (Days 7-8)

### 3.1 Install Dependencies

```bash
npm install react-markdown remark-gfm react-syntax-highlighter
```

**Update**: `package.json`

```json
{
  "dependencies": {
    "react-markdown": "^9.0.1",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.5.0"
  }
}
```

### 3.2 Create MarkdownMessage Component

**File**: `src/components/MarkdownMessage.js` (NEW)

```javascript
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function MarkdownMessage({ content }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    });
  };

  return (
    <div className="markdown-message">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const codeString = String(children).replace(/\n$/, '');
            const language = match ? match[1] : '';
            const index = `${language}-${codeString.slice(0, 20)}`;

            return !inline && match ? (
              <div className="code-block-wrapper" style={{ position: 'relative', marginBottom: '1rem' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  backgroundColor: '#1e1e1e',
                  padding: '0.5rem 1rem',
                  borderTopLeftRadius: '0.5rem',
                  borderTopRightRadius: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#d4d4d4',
                }}>
                  <span>{language}</span>
                  <button
                    onClick={() => copyToClipboard(codeString, index)}
                    style={{
                      backgroundColor: 'transparent',
                      border: '1px solid #444',
                      borderRadius: '0.25rem',
                      padding: '0.25rem 0.75rem',
                      color: '#d4d4d4',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                    }}
                  >
                    {copiedIndex === index ? '✓ Copied!' : 'Copy'}
                  </button>
                </div>
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={language}
                  PreTag="div"
                  {...props}
                >
                  {codeString}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code className={className} style={{
                backgroundColor: '#2d2d2d',
                padding: '0.2rem 0.4rem',
                borderRadius: '0.25rem',
                fontSize: '0.9em',
              }} {...props}>
                {children}
              </code>
            );
          },
          // Style tables
          table({ children }) {
            return (
              <div style={{ overflowX: 'auto', marginBottom: '1rem' }}>
                <table style={{
                  borderCollapse: 'collapse',
                  width: '100%',
                  border: '1px solid #444',
                }}>
                  {children}
                </table>
              </div>
            );
          },
          th({ children }) {
            return (
              <th style={{
                backgroundColor: '#2d2d2d',
                padding: '0.75rem',
                textAlign: 'left',
                borderBottom: '2px solid #444',
              }}>
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td style={{
                padding: '0.75rem',
                borderBottom: '1px solid #333',
              }}>
                {children}
              </td>
            );
          },
          // Style lists
          ul({ children }) {
            return (
              <ul style={{
                marginLeft: '1.5rem',
                marginBottom: '1rem',
              }}>
                {children}
              </ul>
            );
          },
          ol({ children }) {
            return (
              <ol style={{
                marginLeft: '1.5rem',
                marginBottom: '1rem',
              }}>
                {children}
              </ol>
            );
          },
          // Style blockquotes
          blockquote({ children }) {
            return (
              <blockquote style={{
                borderLeft: '4px solid #444',
                paddingLeft: '1rem',
                marginLeft: 0,
                marginBottom: '1rem',
                color: '#aaa',
              }}>
                {children}
              </blockquote>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
```

### 3.3 Update ResponseCard Component

**File**: `src/components/ResponseCard.js`

Update to use MarkdownMessage:

```javascript
import React from 'react';
import MarkdownMessage from './MarkdownMessage';

export default function ResponseCard({ result, index, onVote, isPreferred, isStreaming }) {
  const { provider, model, label, color, response, time, tokens, error } = result;
  
  return (
    <div className="response-card" style={{
      border: `2px solid ${isPreferred ? color : '#333'}`,
      borderRadius: '0.5rem',
      padding: '1rem',
      backgroundColor: '#1a1a1a',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem',
        paddingBottom: '0.5rem',
        borderBottom: '1px solid #333',
      }}>
        <div>
          <h3 style={{ margin: 0, color }}>{label}</h3>
          <div style={{ fontSize: '0.875rem', color: '#888', marginTop: '0.25rem' }}>
            {isStreaming ? (
              <span>⚡ Streaming...</span>
            ) : (
              <span>
                {time > 0 && `⏱ ${time.toFixed(2)}s`}
                {tokens > 0 && ` · ${tokens} tokens`}
              </span>
            )}
          </div>
        </div>
      </div>
      
      {/* Response */}
      <div style={{
        marginBottom: '1rem',
        minHeight: isStreaming ? '3rem' : 'auto',
      }}>
        {error ? (
          <div style={{ color: '#ff6b6b' }}>
            {response}
          </div>
        ) : (
          <MarkdownMessage content={response} />
        )}
        
        {isStreaming && (
          <span className="streaming-cursor" style={{
            display: 'inline-block',
            width: '0.5rem',
            height: '1rem',
            backgroundColor: color,
            animation: 'blink 1s infinite',
            marginLeft: '0.25rem',
          }} />
        )}
      </div>
      
      {/* Vote buttons */}
      {!isStreaming && !error && onVote && (
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          paddingTop: '0.5rem',
          borderTop: '1px solid #333',
        }}>
          <button
            onClick={() => onVote(index)}
            disabled={isPreferred}
            style={{
              flex: 1,
              padding: '0.5rem',
              backgroundColor: isPreferred ? color : '#2d2d2d',
              color: '#fff',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: isPreferred ? 'default' : 'pointer',
              opacity: isPreferred ? 1 : 0.8,
            }}
          >
            {isPreferred ? '✓ Preferred' : '👍 Vote'}
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Part 4: Comparison History UI (Days 9-10)

### 4.1 Create ComparisonHistory Component

**File**: `src/components/ComparisonHistory.js` (NEW)

```javascript
import React, { useState, useEffect } from 'react';
import MarkdownMessage from './MarkdownMessage';

export default function ComparisonHistory({ chatApi, onLoadComparison }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [limit] = useState(20);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    loadHistory();
  }, [offset]);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await chatApi.getComparisonHistory({ limit, offset });
      setHistory(response.data.comparisons);
    } catch (err) {
      setError('Failed to load comparison history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item) => {
    setSelectedItem(selectedItem?.id === item.id ? null : item);
  };

  const handleLoadComparison = (item) => {
    if (onLoadComparison) {
      onLoadComparison(item);
    }
  };

  if (loading && history.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading history...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#ff6b6b' }}>
        {error}
        <button onClick={loadHistory} style={{ marginLeft: '1rem' }}>Retry</button>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#888' }}>
        No comparison history yet. Create your first comparison!
      </div>
    );
  }

  return (
    <div className="comparison-history" style={{
      backgroundColor: '#1a1a1a',
      borderRadius: '0.5rem',
      padding: '1rem',
    }}>
      <h2 style={{ marginTop: 0 }}>Comparison History</h2>
      
      <div className="history-list">
        {history.map((item) => (
          <div
            key={item.id}
            style={{
              backgroundColor: '#2d2d2d',
              borderRadius: '0.5rem',
              padding: '1rem',
              marginBottom: '1rem',
              cursor: 'pointer',
              border: selectedItem?.id === item.id ? '2px solid #10a37f' : '2px solid transparent',
            }}
            onClick={() => handleItemClick(item)}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '0.5rem',
            }}>
              <div style={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                {new Date(item.created_at).toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#888' }}>
                {item.results?.length || 0} models
              </div>
            </div>
            
            <div style={{
              fontSize: '0.875rem',
              color: '#ccc',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {item.prompt}
            </div>
            
            {selectedItem?.id === item.id && (
              <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #444' }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                  gap: '1rem',
                  marginTop: '1rem',
                }}>
                  {item.results?.map((result, index) => (
                    <div
                      key={index}
                      style={{
                        backgroundColor: '#1a1a1a',
                        borderRadius: '0.5rem',
                        padding: '1rem',
                      }}
                    >
                      <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
                        {result.provider} - {result.model}
                      </div>
                      <div style={{
                        fontSize: '0.875rem',
                        color: '#888',
                        marginBottom: '0.5rem',
                      }}>
                        ⏱ {result.time?.toFixed(2)}s · {result.tokens} tokens
                      </div>
                      <div style={{
                        maxHeight: '200px',
                        overflow: 'auto',
                        fontSize: '0.875rem',
                      }}>
                        <MarkdownMessage content={result.response || ''} />
                      </div>
                    </div>
                  ))}
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleLoadComparison(item);
                  }}
                  style={{
                    marginTop: '1rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: '#10a37f',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '0.25rem',
                    cursor: 'pointer',
                  }}
                >
                  Load this comparison
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {history.length >= limit && (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '1rem',
          marginTop: '1rem',
        }}>
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#2d2d2d',
              color: '#fff',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: offset === 0 ? 'not-allowed' : 'pointer',
              opacity: offset === 0 ? 0.5 : 1,
            }}
          >
            Previous
          </button>
          <button
            onClick={() => setOffset(offset + limit)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#2d2d2d',
              color: '#fff',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer',
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Part 5: Manual Testing & Polish (Days 11-14)

### 5.1 Testing Checklist

**Test Cases**:

1. **Streaming Performance**
   - [ ] Time to first token < 1s for all providers
   - [ ] Multiple models stream simultaneously
   - [ ] Streaming is smooth without stuttering
   - [ ] Memory usage remains stable during streaming

2. **Error Handling**
   - [ ] Single provider failure doesn't block others
   - [ ] Appropriate error messages displayed
   - [ ] Can retry after failure
   - [ ] Cancellation works correctly

3. **UI/UX**
   - [ ] Streaming cursor animates correctly
   - [ ] Markdown renders properly
   - [ ] Code blocks have copy buttons
   - [ ] Syntax highlighting works
   - [ ] Vote buttons appear after completion
   - [ ] Comparison history loads correctly

4. **Edge Cases**
   - [ ] Very long responses
   - [ ] Special characters in code
   - [ ] Multiple code blocks
   - [ ] Tables render correctly
   - [ ] Lists render correctly
   - [ ] Empty responses

### 5.2 Performance Optimizations

**Backend**:
- Connection pooling for HTTP requests
- Efficient SSE event generation
- Proper resource cleanup

**Frontend**:
- Debounce rapid state updates
- Virtual scrolling for long responses
- Lazy load comparison history
- Optimize re-renders with React.memo

---

## Part 6: Documentation (Day 14)

### 6.1 Update CHANGELOG.md

```markdown
## [2.0.0] - 2025-11-02

### Added
- Real-time streaming for comparison mode with SSE
- Streaming support for OpenAI, Anthropic, Gemini, and Mistral
- Markdown rendering with syntax highlighting
- Code block copy buttons
- Comparison history UI component
- Graceful error handling for partial stream failures
- Request cancellation support

### Changed
- Comparison mode now streams responses in real-time
- Time to first token reduced from 20-60s to <1s
- Message rendering supports markdown, code blocks, tables, and lists

### Performance
- Multiple models stream simultaneously
- Parallel streaming orchestration
- Optimized frontend state management
```

### 6.2 Update DECISIONS.md

Add decision record:

```markdown
## DR-006: Server-Sent Events for Streaming (2025-11-02)

### Context
Users experience 20-60 second wait times for comparison results. Real-time streaming is needed for better UX.

### Decision
Implement Server-Sent Events (SSE) for streaming comparison results.

### Alternatives Considered
1. **WebSockets**: More complex, bidirectional unnecessary
2. **Polling**: Inefficient, higher latency
3. **HTTP/2 Server Push**: Limited browser support

### Rationale
- SSE is simpler than WebSockets for unidirectional data
- Native EventSource API in browsers
- Automatic reconnection handling
- HTTP/1.1 compatible
- Lower overhead than polling

### Consequences
**Positive**:
- Sub-second time to first token
- Better perceived performance
- Parallel streaming from multiple providers
- Native browser support

**Negative**:
- Keep-alive connections consume server resources
- Need proper cleanup on errors
- SSE not supported in IE (acceptable tradeoff)

### Implementation Notes
- Used Flask stream_with_context for SSE
- ThreadPoolExecutor for parallel provider streaming
- Proper error isolation per provider
- Frontend uses fetch() with ReadableStream (not EventSource for POST support)
```

### 6.3 Update README.md

Add streaming documentation:

```markdown
## Features

### Streaming Responses
LLMSelect streams responses in real-time for instant feedback:

- **Sub-second time to first token**: See responses appear immediately
- **Parallel streaming**: Multiple models stream simultaneously
- **Graceful degradation**: Individual provider failures don't block others
- **Cancellation support**: Stop streaming mid-response

### Markdown Rendering
- **Syntax highlighting**: Code blocks with language detection
- **Copy buttons**: One-click copying of code blocks
- **Rich formatting**: Tables, lists, blockquotes, and links
- **GFM support**: GitHub Flavored Markdown including task lists

### Comparison Mode
- **Real-time streaming**: See all models respond simultaneously
- **Performance metrics**: Response time and token counts
- **Voting**: Mark preferred responses
- **History**: Access past comparisons with full results

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | /api/v1/compare/stream | Stream comparison results via SSE |
| ... | ... | ... |
```

---

## Security Considerations

### Backend
1. **Rate Limiting**: Apply to streaming endpoints
2. **Authentication**: JWT required for all streaming requests
3. **Resource Limits**: Max concurrent streams per user
4. **Timeout**: Automatic stream termination after timeout
5. **Input Validation**: Sanitize prompts and parameters

### Frontend
1. **Token Storage**: Secure token handling
2. **XSS Prevention**: Sanitize markdown content
3. **Memory Management**: Cleanup EventSource on unmount
4. **Error Handling**: No sensitive data in error messages

---

## Success Metrics

### Performance
- ✅ Time to first token < 1 second
- ✅ Multiple models stream simultaneously
- ✅ No blocking between providers
- ✅ Graceful handling of failures

### Functionality
- ✅ Streaming works for all 4 providers
- ✅ Markdown renders correctly
- ✅ Code highlighting works
- ✅ Copy buttons functional
- ✅ History UI accessible

### Quality
- ✅ All tests pass
- ✅ No memory leaks
- ✅ Error handling comprehensive
- ✅ Documentation complete

---

## Rollout Plan

### Phase 1: Beta Testing (Day 11-12)
- Deploy to staging
- Internal testing
- Performance monitoring
- Bug fixes

### Phase 2: Gradual Rollout (Day 13)
- Feature flag controlled release
- Monitor error rates
- Collect user feedback
- Performance tuning

### Phase 3: Full Release (Day 14)
- Enable for all users
- Update documentation
- Announce features
- Monitor metrics

---

## Maintenance & Monitoring

### Metrics to Track
- Time to first token (p50, p95, p99)
- Stream completion rate
- Error rate by provider
- Memory usage during streaming
- Concurrent stream count

### Alerts
- High error rate (>5%)
- Slow time to first token (>2s)
- Memory usage spikes
- Provider failures

---

## Future Enhancements

### Phase 3.1 (Optional)
- Streaming for single chat mode
- Resume interrupted streams
- Stream history playback
- Custom streaming parameters

### Phase 3.2 (Optional)
- WebSocket support for bidirectional
- Streaming with conversation context
- Multi-turn streaming
- Stream analytics dashboard

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-02  
**Owner**: Implementation Team

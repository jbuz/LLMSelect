# Chat Streaming Implementation - LLMSelect Phase 4 Priority 4

## Context & Current State

**Project:** LLMSelect - Multi-LLM comparison platform  
**Phase:** 4 (Priority 4 - Chat Streaming)  
**Status:** Comparison mode has streaming ✅, Single-model chat does NOT ❌  
**Problem:** UX inconsistency - users expect streaming in both modes

**What Already Works:**
- ✅ Comparison mode has real-time SSE streaming (`POST /api/v1/compare` with `stream=true`)
- ✅ Frontend has `useStreamingComparison` hook for SSE handling
- ✅ Markdown rendering with syntax highlighting
- ✅ Backend streaming infrastructure exists

**What's Missing:**
- ❌ Single-model chat uses blocking POST request (slow, no feedback)
- ❌ No streaming endpoint for `/api/v1/chat`
- ❌ No streaming UI indicators in chat mode
- ❌ No cancel button for long-running requests

---

## Implementation Requirements

### Backend: Create SSE Streaming Endpoint

**File:** `llmselect/routes/chat.py`

**Add new endpoint:** `POST /api/v1/chat/stream`

**Requirements:**
1. Accept same parameters as existing `POST /api/v1/chat`:
   ```json
   {
     "conversation_id": "optional-uuid",
     "message": "user message text",
     "provider": "openai",
     "model": "gpt-4o"
   }
   ```

2. Stream response using SSE (Server-Sent Events):
   - Content-Type: `text/event-stream`
   - Return NDJSON chunks: `data: {"content": "token"}\n\n`
   - Final message: `data: {"done": true, "conversation_id": "uuid"}\n\n`

3. **Reuse existing streaming logic** from `llmselect/routes/comparisons.py`:
   - Look at the `compare()` function's streaming implementation
   - Use same NDJSON format for consistency
   - Handle errors the same way (send error event, close stream)

4. **Important:** Still save the message to database (conversation persistence)
   - Create/update conversation
   - Save user message
   - Save assistant response after streaming completes

**Implementation Pattern (based on existing code):**
```python
@bp.post("/stream")
@jwt_required()
@limiter.limit(_rate_limit)
def stream_chat():
    """Stream single-model chat response via SSE."""
    data = request.get_json()
    
    # Validate input
    validate_message_request(data)
    
    # Get services
    services = current_app.extensions["services"]
    
    # Get conversation (create if needed)
    conversation = get_or_create_conversation(...)
    
    # Save user message
    user_message = save_user_message(...)
    
    # Start streaming
    def generate():
        try:
            for chunk in services.llm.stream_invoke(
                provider=data["provider"],
                model=data["model"],
                messages=conversation.messages,
                api_key=get_user_api_key(...)
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # Save assistant response
            assistant_message = save_assistant_message(...)
            
            # Send completion event
            yield f"data: {json.dumps({'done': True, 'conversation_id': str(conversation.id)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")
```

**Key Points:**
- Follow existing patterns in `chat.py` for validation, auth, database operations
- Reuse streaming logic from `comparisons.py`
- Ensure proper error handling and cleanup
- Test with all 4 providers (OpenAI, Anthropic, Gemini, Mistral)

---

### Frontend: Create Streaming Chat Hook

**File:** `src/hooks/useStreamingChat.js` (NEW FILE)

**Purpose:** Handle SSE connection for single-model chat streaming

**API Design:**
```javascript
const {
  streamMessage,
  currentMessage,
  isStreaming,
  error,
  cancelStream
} = useStreamingChat();

// Usage:
streamMessage({
  conversationId: 'optional-uuid',
  message: 'user prompt',
  provider: 'openai',
  model: 'gpt-4o'
});
```

**Requirements:**
1. **Base on existing `useStreamingComparison.js`** - copy and adapt the pattern
2. Manage EventSource connection lifecycle
3. Handle streaming state (isStreaming, currentMessage, error)
4. Accumulate message chunks as they arrive
5. Handle completion event (update conversation ID)
6. Provide cancel functionality
7. Clean up connections on unmount

**Implementation Pattern:**
```javascript
export const useStreamingChat = () => {
  const [currentMessage, setCurrentMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const eventSourceRef = useRef(null);

  const streamMessage = async ({ conversationId, message, provider, model }) => {
    setIsStreaming(true);
    setError(null);
    setCurrentMessage('');
    
    try {
      const token = localStorage.getItem('token');
      const url = `/api/v1/chat/stream`;
      
      // POST request to initiate stream
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ conversation_id: conversationId, message, provider, model })
      });
      
      // Create EventSource from response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.error) {
              setError(data.error);
              setIsStreaming(false);
              return;
            }
            
            if (data.done) {
              setConversationId(data.conversation_id);
              setIsStreaming(false);
              return;
            }
            
            if (data.content) {
              setCurrentMessage(prev => prev + data.content);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setIsStreaming(false);
    }
  };
  
  const cancelStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      setIsStreaming(false);
    }
  };
  
  useEffect(() => {
    return () => cancelStream();
  }, []);
  
  return {
    streamMessage,
    currentMessage,
    isStreaming,
    error,
    conversationId,
    cancelStream
  };
};
```

---

### Frontend: Update MessageList Component

**File:** `src/components/MessageList.js`

**Changes Needed:**
1. Add streaming indicator when `isStreaming === true`
2. Display `currentMessage` as it streams in
3. Show a pulsing cursor or "typing..." indicator
4. Match the styling from ComparisonMode streaming

**Implementation:**
```javascript
// Add props to MessageList
function MessageList({ messages, isLoading, isStreaming, currentMessage }) {
  return (
    <div className="message-list">
      {messages.map((msg, idx) => (
        <MessageItem key={idx} message={msg} />
      ))}
      
      {isStreaming && currentMessage && (
        <div className="message streaming">
          <div className="message-role">Assistant</div>
          <div className="message-content">
            <MarkdownMessage content={currentMessage} />
            <span className="streaming-cursor">▊</span>
          </div>
        </div>
      )}
      
      {isLoading && !isStreaming && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <span>Thinking...</span>
        </div>
      )}
    </div>
  );
}
```

**CSS for streaming indicator:**
```css
.streaming-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  color: var(--primary-color);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
```

---

### Frontend: Update MessageInput Component

**File:** `src/components/MessageInput.js`

**Changes Needed:**
1. Add cancel button when streaming is active
2. Disable input while streaming
3. Show "Cancel" button next to send button

**Implementation:**
```javascript
function MessageInput({ onSendMessage, isLoading, isStreaming, onCancel }) {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isStreaming) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="message-input">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        disabled={isStreaming || isLoading}
        rows={3}
      />
      <div className="input-actions">
        {isStreaming ? (
          <button type="button" onClick={onCancel} className="cancel-btn">
            ⏹ Cancel
          </button>
        ) : (
          <button type="submit" disabled={!message.trim() || isLoading}>
            ➤ Send
          </button>
        )}
      </div>
    </form>
  );
}
```

---

### Frontend: Update App.js

**File:** `src/App.js`

**Changes Needed:**
1. Import `useStreamingChat` hook
2. Replace existing blocking chat logic with streaming
3. Pass streaming props to MessageList and MessageInput
4. Handle streaming state updates

**Key Changes:**
```javascript
import { useStreamingChat } from './hooks/useStreamingChat';

function App() {
  const [mode, setMode] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  
  // Replace old chat logic with streaming
  const {
    streamMessage,
    currentMessage,
    isStreaming,
    error: streamError,
    conversationId: newConversationId,
    cancelStream
  } = useStreamingChat();
  
  // When streaming completes, add message to list
  useEffect(() => {
    if (!isStreaming && currentMessage && newConversationId) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: currentMessage
      }]);
      setConversationId(newConversationId);
    }
  }, [isStreaming, currentMessage, newConversationId]);
  
  const sendMessage = async (message) => {
    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    
    // Start streaming
    await streamMessage({
      conversationId,
      message,
      provider: selectedProvider,
      model: selectedModel
    });
  };
  
  return (
    <div className="app">
      {mode === 'chat' && (
        <>
          <MessageList
            messages={messages}
            isStreaming={isStreaming}
            currentMessage={currentMessage}
          />
          <MessageInput
            onSendMessage={sendMessage}
            isStreaming={isStreaming}
            onCancel={cancelStream}
          />
        </>
      )}
    </div>
  );
}
```

---

## Testing Requirements

### Backend Tests

**File:** `tests/test_chat.py`

Add new test for streaming endpoint:
```python
def test_chat_stream_endpoint(client, app, monkeypatch):
    """Test SSE streaming chat endpoint."""
    register_and_login(client)
    
    # Mock LLM service to return chunks
    def fake_stream_invoke(provider, model, messages, api_key):
        yield "Hello"
        yield " "
        yield "world"
        yield "!"
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "stream_invoke", fake_stream_invoke)
    
    # Make streaming request
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Test message",
            "provider": "openai",
            "model": "gpt-4o"
        },
        headers={"Accept": "text/event-stream"}
    )
    
    assert response.status_code == 200
    assert response.content_type == "text/event-stream"
    
    # Verify chunks received
    data = response.get_data(as_text=True)
    assert "Hello" in data
    assert "world" in data
    assert '"done": true' in data
```

### Frontend Tests

**File:** `src/hooks/__tests__/useStreamingChat.test.js`

Test the streaming hook:
```javascript
describe('useStreamingChat', () => {
  it('should stream message chunks', async () => {
    // Test implementation
  });
  
  it('should handle errors', async () => {
    // Test implementation
  });
  
  it('should allow cancellation', async () => {
    // Test implementation
  });
});
```

### Manual Testing Checklist

**Add to TESTING_CHECKLIST.md:**

- [ ] Single-model chat streams responses in real-time
- [ ] Streaming indicator appears during response
- [ ] Can cancel mid-stream
- [ ] Messages save to database after streaming
- [ ] Works with all 4 providers (OpenAI, Anthropic, Gemini, Mistral)
- [ ] Error handling works (invalid API key, network errors)
- [ ] Conversation persistence works after streaming
- [ ] UI matches comparison mode streaming style

---

## Success Criteria

✅ **Functional:**
- Single-model chat uses streaming (not blocking requests)
- Cancel button works during streaming
- Messages persist to database after streaming
- Works with all 4 providers

✅ **Performance:**
- Time to first token < 1 second
- No memory leaks from EventSource connections
- Smooth UI updates without jank

✅ **UX Consistency:**
- Streaming UI matches comparison mode style
- Error handling matches existing patterns
- Loading states are clear and helpful

✅ **Code Quality:**
- Follows existing code patterns
- All tests pass (21+ tests)
- No breaking changes to existing features
- Code is maintainable and well-documented

---

## Implementation Order

1. **Day 1 Morning:** Backend streaming endpoint (2-3 hours)
   - Add `POST /api/v1/chat/stream` to `chat.py`
   - Reuse streaming logic from `comparisons.py`
   - Test with curl/Postman

2. **Day 1 Afternoon:** Frontend streaming hook (2-3 hours)
   - Create `useStreamingChat.js`
   - Base on `useStreamingComparison.js`
   - Test hook independently

3. **Day 1 Evening:** UI Integration (2-3 hours)
   - Update MessageList with streaming indicator
   - Update MessageInput with cancel button
   - Update App.js to use streaming
   - Manual testing

4. **Day 2 Morning:** Testing & Polish (2-3 hours)
   - Write backend tests
   - Write frontend tests
   - Update TESTING_CHECKLIST.md
   - Bug fixes

**Total Time:** 1-1.5 days

---

## Key Files to Modify

**Backend:**
- ✏️ `llmselect/routes/chat.py` - Add streaming endpoint
- 📖 `llmselect/routes/comparisons.py` - Reference for streaming pattern
- 📖 `llmselect/services/llm.py` - Reference for stream_invoke method

**Frontend:**
- ✏️ `src/hooks/useStreamingChat.js` - NEW FILE
- ✏️ `src/components/MessageList.js` - Add streaming display
- ✏️ `src/components/MessageInput.js` - Add cancel button
- ✏️ `src/App.js` - Integrate streaming
- 📖 `src/hooks/useStreamingComparison.js` - Reference for SSE pattern

**Tests:**
- ✏️ `tests/test_chat.py` - Add streaming test
- ✏️ `src/hooks/__tests__/useStreamingChat.test.js` - NEW FILE
- ✏️ `TESTING_CHECKLIST.md` - Add manual test cases

**Documentation:**
- ✏️ `TESTING_CHECKLIST.md` - Update with streaming tests
- 📖 `README.md` - Mention streaming feature (if needed)

---

## Notes

- This completes Phase 4 Priority 4
- Achieves UX consistency between chat and comparison modes
- Improves perceived performance (streaming feels faster)
- No breaking changes - old `/api/v1/chat` endpoint can remain for compatibility
- Sets foundation for future real-time features

**Ready to implement! Start with backend streaming endpoint, then frontend hook, then UI integration.**

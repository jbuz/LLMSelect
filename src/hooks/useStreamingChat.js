import { useState, useCallback, useRef, useEffect } from 'react';
import Cookies from 'js-cookie';

export const useStreamingChat = () => {
  const [currentMessage, setCurrentMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const abortControllerRef = useRef(null);

  const streamMessage = useCallback(async ({ conversationId, message, provider, model }) => {
    setIsStreaming(true);
    setError(null);
    setCurrentMessage('');

    try {
      // Create AbortController for cancellation
      abortControllerRef.current = new AbortController();

      const url = new URL('/api/v1/chat/stream', window.location.origin);

      // Prepare headers, including CSRF token so JWT cookies are accepted
      const headers = {
        'Content-Type': 'application/json',
      };

      const csrfToken = Cookies.get('csrf_access_token');
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken;
      }

      // Build messages array
      const messages = [{ role: 'user', content: message }];

      // Send POST request to initiate stream
      const response = await fetch(url, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
          conversationId: conversationId,
          messages,
          provider,
          model,
        }),
        signal: abortControllerRef.current.signal,
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

              if (data.error) {
                setError(data.error);
                setIsStreaming(false);
                return;
              }

              if (data.done) {
                setConversationId(data.conversationId);
                setIsStreaming(false);
                return;
              }

              if (data.content) {
                setCurrentMessage(prev => prev + data.content);
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Stream cancelled by user');
        setError('Streaming cancelled');
      } else {
        console.error('Streaming error:', err);
        setError('Streaming failed. Please try again.');
      }
      setIsStreaming(false);
    }
  }, []);

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    streamMessage,
    currentMessage,
    isStreaming,
    error,
    conversationId,
    cancelStream,
  };
};

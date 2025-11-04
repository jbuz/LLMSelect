import { useState, useCallback, useRef } from 'react';
import Cookies from 'js-cookie';

export const useStreamingComparison = (chatApi) => {
  const [streamingResults, setStreamingResults] = useState({});
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonId, setComparisonId] = useState(null);
  const streamingDataRef = useRef({});
  const abortControllerRef = useRef(null);

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
      // Create AbortController for cancellation
      abortControllerRef.current = new AbortController();
      
      // Get CSRF token from cookie for JWT protection
      const csrfToken = Cookies.get('csrf_access_token');
      const url = new URL('/api/v1/compare/stream', window.location.origin);
      
      // Prepare headers
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add CSRF token if available
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken;
      }
      
      // Send POST request to initiate stream
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        credentials: 'include', // Include cookies for JWT authentication
        body: JSON.stringify({
          prompt,
          providers: selectedModels.map(m => ({
            provider: m.provider,
            model: m.model,
          })),
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
              handleStreamEvent(data);
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
        console.error('Streaming error:', err.name);
        setError('Streaming failed. Please try again.');
      }
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
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setError('Streaming cancelled');
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

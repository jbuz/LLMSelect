import React, { useState, memo, useCallback } from 'react';
import MarkdownMessage from './MarkdownMessage';

const ResponseCard = memo(({ 
  provider, 
  model,
  label,
  color,
  response, 
  metadata, 
  onVote,
  isPreferred,
  isStreaming,
  hasError,
  index
}) => {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [response]);
  
  const handleVote = useCallback(() => {
    if (onVote) onVote(index);
  }, [onVote, index]);
  
  // Display label if provided, otherwise fall back to model name
  const displayName = label || model;
  
  return (
    <div 
      className={`response-card ${isPreferred ? 'preferred' : ''} ${isStreaming ? 'streaming' : ''} ${hasError ? 'error' : ''}`}
      style={{
        borderColor: isPreferred ? color : undefined,
      }}
    >
      <div className="response-header">
        <div className="model-info">
          <h3 className="model-name" style={{ color: color || undefined }}>
            {displayName}
          </h3>
          <span className="provider-badge">{provider}</span>
        </div>
        
        <div className="metadata">
          {isStreaming && (
            <span className="meta-item streaming-indicator" title="Streaming in progress">
              ⚡ Streaming...
            </span>
          )}
          {!isStreaming && metadata.time !== undefined && (
            <span className="meta-item" title="Response time">
              ⏱️ {metadata.time.toFixed(2)}s
            </span>
          )}
          {metadata.tokens > 0 && (
            <span className="meta-item" title="Estimated tokens">
              📊 {metadata.tokens}
            </span>
          )}
          {metadata.cost && (
            <span className="meta-item" title="Estimated cost">
              💰 ${metadata.cost.toFixed(4)}
            </span>
          )}
        </div>
      </div>
      
      <div className="response-content">
        {hasError ? (
          <div className="error-message" style={{ color: '#ff6b6b' }}>
            {response}
          </div>
        ) : (
          <div>
            <MarkdownMessage content={response} />
            {isStreaming && (
              <span 
                className="streaming-cursor"
                style={{
                  display: 'inline-block',
                  width: '0.5rem',
                  height: '1rem',
                  backgroundColor: color || '#10a37f',
                  marginLeft: '0.25rem',
                  animation: 'blink 1s infinite',
                }}
              />
            )}
          </div>
        )}
      </div>
      
      <div className="response-actions">
        <button 
          onClick={handleCopy}
          className="action-btn copy-btn"
          title="Copy response"
          disabled={isStreaming || hasError || !response}
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
        
        {!isStreaming && !hasError && onVote && (
          <button
            onClick={handleVote}
            className={`action-btn vote-btn ${isPreferred ? 'active' : ''}`}
            title="Mark as preferred"
          >
            {isPreferred ? '⭐ Preferred' : '👍 Prefer'}
          </button>
        )}
      </div>
    </div>
  );
});

ResponseCard.displayName = 'ResponseCard';

export default ResponseCard;

import React, { useState } from 'react';

export default function ResponseCard({ 
  provider, 
  model, 
  response, 
  metadata, 
  onVote,
  isPreferred,
  index
}) {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };
  
  return (
    <div className={`response-card ${isPreferred ? 'preferred' : ''}`}>
      <div className="response-header">
        <div className="model-info">
          <h3 className="model-name">{model}</h3>
          <span className="provider-badge">{provider}</span>
        </div>
        
        <div className="metadata">
          {metadata.time !== undefined && (
            <span className="meta-item" title="Response time">
              ⏱️ {metadata.time.toFixed(2)}s
            </span>
          )}
          {metadata.tokens && (
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
        <pre>{response}</pre>
      </div>
      
      <div className="response-actions">
        <button 
          onClick={handleCopy}
          className="action-btn copy-btn"
          title="Copy response"
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
        
        <button
          onClick={() => onVote(index)}
          className={`action-btn vote-btn ${isPreferred ? 'active' : ''}`}
          title="Mark as preferred"
        >
          {isPreferred ? '⭐ Preferred' : '👍 Prefer'}
        </button>
      </div>
    </div>
  );
}

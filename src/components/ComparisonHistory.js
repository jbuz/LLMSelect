import React, { useState } from 'react';
import { useComparisonHistory } from '../hooks/useComparisonHistory';
import MarkdownMessage from './MarkdownMessage';

export default function ComparisonHistory({ onLoadComparison, onClose }) {
  const { comparisons, loading, error, deleteComparison, refetch } = useComparisonHistory();
  const [expandedId, setExpandedId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (comparisonId) => {
    if (!window.confirm('Are you sure you want to delete this comparison?')) {
      return;
    }

    setDeletingId(comparisonId);
    const success = await deleteComparison(comparisonId);
    setDeletingId(null);

    if (success && expandedId === comparisonId) {
      setExpandedId(null);
    }
  };

  const handleLoad = (comparison) => {
    if (onLoadComparison) {
      onLoadComparison(comparison);
    }
  };

  const toggleExpand = (comparisonId) => {
    setExpandedId(expandedId === comparisonId ? null : comparisonId);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncatePrompt = (prompt, maxLength = 100) => {
    if (prompt.length <= maxLength) return prompt;
    return prompt.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="comparison-history">
        <div className="history-header">
          <h2>Comparison History</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading comparison history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="comparison-history">
        <div className="history-header">
          <h2>Comparison History</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        <div className="error-banner">
          ⚠️ {error}
          <button onClick={() => refetch()} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  if (comparisons.length === 0) {
    return (
      <div className="comparison-history">
        <div className="history-header">
          <h2>Comparison History</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <h3>No Comparisons Yet</h3>
          <p>Your comparison history will appear here after you run your first comparison.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="comparison-history">
      <div className="history-header">
        <h2>Comparison History</h2>
        <button onClick={onClose} className="close-btn">×</button>
      </div>

      <div className="history-list">
        {comparisons.map((comparison) => {
          const isExpanded = expandedId === comparison.id;
          const isDeleting = deletingId === comparison.id;

          return (
            <div
              key={comparison.id}
              className={`history-item ${isExpanded ? 'expanded' : ''}`}
            >
              <div className="history-item-header" onClick={() => toggleExpand(comparison.id)}>
                <div className="history-item-info">
                  <div className="history-item-prompt">
                    {truncatePrompt(comparison.prompt)}
                  </div>
                  <div className="history-item-meta">
                    <span className="history-item-date">
                      {formatDate(comparison.created_at)}
                    </span>
                    <span className="history-item-models">
                      {comparison.results.length} models compared
                    </span>
                  </div>
                </div>
                <div className="history-item-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLoad(comparison);
                    }}
                    className="load-btn"
                    disabled={isDeleting}
                  >
                    Load
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(comparison.id);
                    }}
                    className="delete-btn"
                    disabled={isDeleting}
                  >
                    {isDeleting ? '...' : 'Delete'}
                  </button>
                  <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                </div>
              </div>

              {isExpanded && (
                <div className="history-item-details">
                  <div className="history-item-full-prompt">
                    <h4>Prompt:</h4>
                    <p>{comparison.prompt}</p>
                  </div>

                  <div className="history-item-results">
                    <h4>Results:</h4>
                    {comparison.results.map((result, idx) => (
                      <div key={idx} className="history-result">
                        <div className="history-result-header">
                          <strong>{result.model}</strong> ({result.provider})
                          {comparison.preferred_index === idx && (
                            <span className="preferred-badge">⭐ Preferred</span>
                          )}
                        </div>
                        <div className="history-result-meta">
                          <span>⏱️ {result.time?.toFixed(2)}s</span>
                          <span>📝 {result.tokens} tokens</span>
                        </div>
                        <div className="history-result-response">
                          <MarkdownMessage content={result.response} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

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
  const [prompt, setPrompt] = useState('');
  const [preferredIndex, setPreferredIndex] = useState(null);
  
  // Use streaming hook
  const {
    streamingResults,
    isStreaming,
    error,
    comparisonId,
    startStreaming,
    cancelStreaming,
  } = useStreamingComparison(chatApi);
  
  const handleCompare = async (content) => {
    setPrompt(content);
    setPreferredIndex(null);
    await startStreaming(content, selectedModels);
  };
  
  const handleVote = async (index) => {
    if (!comparisonId) return;
    
    try {
      await chatApi.voteComparison(comparisonId, index);
      setPreferredIndex(index);
    } catch (err) {
      console.error('Vote failed:', err);
    }
  };
  
  return (
    <div className="comparison-mode">
      <div className="comparison-controls">
        <div className="model-selector-wrapper">
          <label>Models to Compare ({selectedModels.length}/4)</label>
          <ModelSelector
            selected={selectedModels}
            onChange={setSelectedModels}
            maxModels={4}
            minModels={2}
          />
        </div>
        
        <div className="prompt-input-wrapper">
          <label>Prompt</label>
          <MessageInput
            onSendMessage={handleCompare}
            isLoading={isStreaming || selectedModels.length < 2}
            placeholder="Enter your prompt to compare models..."
            onCancel={isStreaming ? cancelStreaming : undefined}
          />
        </div>
      </div>
      
      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}
      
      {isStreaming && streamingResults.length === 0 && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Starting comparison with {selectedModels.length} models...</p>
        </div>
      )}
      
      {streamingResults.length > 0 && (
        <div className="comparison-results">
          <div className="results-header">
            <h2>Comparison Results {isStreaming && '(Streaming...)'}</h2>
            <p className="prompt-display">"{prompt}"</p>
          </div>
          
          <div 
            className="results-grid"
            style={{
              gridTemplateColumns: `repeat(${Math.min(streamingResults.length, 2)}, 1fr)`
            }}
          >
            {streamingResults.map((result, idx) => (
              <ResponseCard
                key={`${result.provider}_${result.model}`}
                provider={result.provider}
                model={result.model}
                label={result.label}
                color={result.color}
                response={result.response}
                metadata={{
                  time: result.time,
                  tokens: result.tokens,
                }}
                onVote={handleVote}
                isPreferred={preferredIndex === idx}
                isStreaming={result.streaming}
                hasError={result.error}
                index={idx}
              />
            ))}
          </div>
        </div>
      )}
      
      {streamingResults.length === 0 && !isStreaming && (
        <div className="comparison-empty-state">
          <div className="empty-state-icon">🔄</div>
          <h3>Compare LLM Models Side-by-Side</h3>
          <p>Select 2-4 models above and enter a prompt to see how different models respond</p>
          <p className="streaming-info">✨ Real-time streaming enabled - see responses as they're generated!</p>
        </div>
      )}
    </div>
  );
}

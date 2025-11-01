import React, { useState } from 'react';
import ModelSelector from './ModelSelector';
import ResponseCard from './ResponseCard';
import MessageInput from './MessageInput';

export default function ComparisonMode({ chatApi }) {
  const [selectedModels, setSelectedModels] = useState([
    { provider: 'openai', model: 'gpt-4', label: 'GPT-4', color: '#10a37f' },
    { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', color: '#d97757' },
  ]);
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonId, setComparisonId] = useState(null);
  const [preferredIndex, setPreferredIndex] = useState(null);
  
  const handleCompare = async (content) => {
    if (!content.trim() || selectedModels.length < 2) {
      setError('Please enter a prompt and select at least 2 models');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResults(null);
    setComparisonId(null);
    setPreferredIndex(null);
    
    try {
      const response = await chatApi.compare({
        providers: selectedModels.map(m => ({
          provider: m.provider,
          model: m.model
        })),
        prompt: content
      });
      
      setResults(response.data.results);
      setComparisonId(response.data.id);
      setPrompt(content);
    } catch (err) {
      const message = err.response?.data?.message || err.response?.data?.error || 'Comparison failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
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
            isLoading={isLoading || selectedModels.length < 2}
            placeholder="Enter your prompt to compare models..."
          />
        </div>
      </div>
      
      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}
      
      {isLoading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Comparing {selectedModels.length} models...</p>
          <p className="loading-hint">This may take a few moments</p>
        </div>
      )}
      
      {results && results.length > 0 && (
        <div className="comparison-results">
          <div className="results-header">
            <h2>Comparison Results</h2>
            <p className="prompt-display">"{prompt}"</p>
          </div>
          
          <div 
            className="results-grid"
            style={{
              gridTemplateColumns: `repeat(${Math.min(results.length, 2)}, 1fr)`
            }}
          >
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
                onVote={handleVote}
                isPreferred={preferredIndex === idx}
                index={idx}
              />
            ))}
          </div>
        </div>
      )}
      
      {!results && !isLoading && (
        <div className="comparison-empty-state">
          <div className="empty-state-icon">🔄</div>
          <h3>Compare LLM Models Side-by-Side</h3>
          <p>Select 2-4 models above and enter a prompt to see how different models respond</p>
        </div>
      )}
    </div>
  );
}

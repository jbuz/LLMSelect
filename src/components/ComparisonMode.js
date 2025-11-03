import React, { useState, useMemo } from 'react';
import ModelSelector from './ModelSelector';
import ResponseCard from './ResponseCard';
import MessageInput from './MessageInput';
import { useStreamingComparison } from '../hooks/useStreamingComparison';

// Provider colors for visual distinction
const PROVIDER_COLORS = {
  openai: '#10a37f',
  anthropic: '#d97757',
  gemini: '#4285f4',
  mistral: '#f2a73b',
};

export default function ComparisonMode({ chatApi, providerModels = {} }) {
  // Convert providerModels to flat list with colors for initialization
  const availableModels = useMemo(() => {
    const models = [];
    Object.keys(providerModels).forEach(provider => {
      const color = PROVIDER_COLORS[provider] || '#666666';
      providerModels[provider].forEach(model => {
        models.push({
          provider,
          model: model.id,
          label: model.name,
          color,
        });
      });
    });
    return models;
  }, [providerModels]);

  // Initialize with first available models from different providers
  const [selectedModels, setSelectedModels] = useState(() => {
    const defaults = [];
    // Try to get one from openai and one from anthropic
    if (availableModels.length > 0) {
      const openaiModel = availableModels.find(m => m.provider === 'openai');
      const anthropicModel = availableModels.find(m => m.provider === 'anthropic');
      
      if (openaiModel) defaults.push(openaiModel);
      if (anthropicModel) defaults.push(anthropicModel);
      
      // If we don't have 2 yet, add more
      if (defaults.length < 2) {
        availableModels.slice(0, 2 - defaults.length).forEach(m => {
          if (!defaults.find(d => d.provider === m.provider && d.model === m.model)) {
            defaults.push(m);
          }
        });
      }
    }
    return defaults;
  });

  const [prompt, setPrompt] = useState('');
  const [preferredIndex, setPreferredIndex] = useState(null);
  
  // Convert providerModels to flat list with colors
  const allAvailableModels = useMemo(() => {
    const models = [];
    Object.keys(providerModels).forEach(provider => {
      const color = PROVIDER_COLORS[provider] || '#666666';
      providerModels[provider].forEach(model => {
        models.push({
          provider,
          model: model.id,
          label: model.name,
          color,
        });
      });
    });
    return models;
  }, [providerModels]);
  
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
            availableModels={allAvailableModels}
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

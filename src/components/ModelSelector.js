import React, { useState } from 'react';

const AVAILABLE_MODELS = [
  { provider: 'openai', model: 'gpt-4', label: 'GPT-4', color: '#10a37f' },
  { provider: 'openai', model: 'gpt-4-turbo', label: 'GPT-4 Turbo', color: '#10a37f' },
  { provider: 'openai', model: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo', color: '#10a37f' },
  { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', color: '#d97757' },
  { provider: 'anthropic', model: 'claude-3-opus-20240229', label: 'Claude 3 Opus', color: '#d97757' },
  { provider: 'anthropic', model: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku', color: '#d97757' },
  { provider: 'gemini', model: 'gemini-pro', label: 'Gemini Pro', color: '#4285f4' },
  { provider: 'gemini', model: 'gemini-pro-vision', label: 'Gemini Pro Vision', color: '#4285f4' },
  { provider: 'mistral', model: 'mistral-large-latest', label: 'Mistral Large', color: '#f2a73b' },
  { provider: 'mistral', model: 'mistral-medium-latest', label: 'Mistral Medium', color: '#f2a73b' },
  { provider: 'mistral', model: 'mistral-small-latest', label: 'Mistral Small', color: '#f2a73b' },
];

export default function ModelSelector({ selected, onChange, maxModels = 4, minModels = 2 }) {
  const [isOpen, setIsOpen] = useState(false);
  
  const handleToggle = (model) => {
    const isSelected = selected.some(s => 
      s.provider === model.provider && s.model === model.model
    );
    
    if (isSelected) {
      // Only allow removal if we'll still have at least minModels
      if (selected.length > minModels) {
        onChange(selected.filter(s => 
          !(s.provider === model.provider && s.model === model.model)
        ));
      }
    } else if (selected.length < maxModels) {
      onChange([...selected, model]);
    }
  };
  
  return (
    <div className="model-selector">
      <div className="selected-models">
        {selected.map((model, idx) => (
          <div 
            key={`${model.provider}-${model.model}`} 
            className="model-chip"
            style={{ borderLeftColor: model.color }}
          >
            <span className="model-label">{model.label}</span>
            {selected.length > minModels && (
              <button 
                onClick={() => handleToggle(model)}
                className="remove-btn"
                title="Remove model"
              >
                ×
              </button>
            )}
          </div>
        ))}
        
        {selected.length < maxModels && (
          <button 
            onClick={() => setIsOpen(!isOpen)}
            className="add-model-btn"
          >
            + Add Model
          </button>
        )}
      </div>
      
      {isOpen && (
        <div className="model-dropdown">
          <div className="dropdown-header">
            <span>Select a model to compare</span>
            <button onClick={() => setIsOpen(false)} className="close-dropdown">×</button>
          </div>
          {AVAILABLE_MODELS
            .filter(m => !selected.some(s => 
              s.provider === m.provider && s.model === m.model
            ))
            .map(model => (
              <button
                key={`${model.provider}-${model.model}`}
                onClick={() => {
                  handleToggle(model);
                  if (selected.length + 1 >= maxModels) {
                    setIsOpen(false);
                  }
                }}
                className="model-option"
              >
                <span 
                  className="model-indicator" 
                  style={{ backgroundColor: model.color }}
                />
                <span className="model-name">{model.label}</span>
              </button>
            ))
          }
        </div>
      )}
    </div>
  );
}

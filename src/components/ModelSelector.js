import React, { useState, memo, useCallback } from 'react';

const ModelSelector = memo(({ selected, onChange, availableModels = [], maxModels = 4, minModels = 2 }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const handleToggle = useCallback((model) => {
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
  }, [selected, onChange, minModels, maxModels]);
  
  const toggleDropdown = useCallback(() => setIsOpen(prev => !prev), []);
  const closeDropdown = useCallback(() => setIsOpen(false), []);
  
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
            onClick={toggleDropdown}
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
            <button onClick={closeDropdown} className="close-dropdown">×</button>
          </div>
          {availableModels
            .filter(m => !selected.some(s => 
              s.provider === m.provider && s.model === m.model
            ))
            .map(model => (
              <button
                key={`${model.provider}-${model.model}`}
                onClick={() => {
                  handleToggle(model);
                  if (selected.length + 1 >= maxModels) {
                    closeDropdown();
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
});

ModelSelector.displayName = 'ModelSelector';

export default ModelSelector;

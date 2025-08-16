import React, { useState } from 'react';

const ApiKeyModal = ({ onSave, onClose }) => {
  const [keys, setKeys] = useState({
    openai: '',
    anthropic: '',
    gemini: '',
    mistral: ''
  });

  const handleSave = () => {
    onSave(keys);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>API Configuration</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-content">
          {Object.entries(keys).map(([provider, key]) => (
            <div key={provider} className="form-group">
              <label className="form-label">
                {provider.charAt(0).toUpperCase() + provider.slice(1)} API Key
              </label>
              <input
                type="password"
                className="form-input"
                value={key}
                onChange={(e) => setKeys({ ...keys, [provider]: e.target.value })}
                placeholder={`Enter your ${provider} API key`}
              />
            </div>
          ))}
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave}>Save Keys</button>
        </div>
      </div>
    </div>
  );
};

export default ApiKeyModal;
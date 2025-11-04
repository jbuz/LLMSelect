import React, { useState, useEffect } from 'react';
import { keyApi } from '../services/api';

const ApiKeyModal = ({ onSave, onClose }) => {
  const [keys, setKeys] = useState({
    openai: '',
    anthropic: '',
    gemini: '',
    mistral: ''
  });
  const [existingProviders, setExistingProviders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch which providers already have keys configured
    const fetchExistingKeys = async () => {
      try {
        const response = await keyApi.get();
        setExistingProviders(response.data.providers || []);
      } catch (err) {
        console.error('Failed to fetch existing keys:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchExistingKeys();
  }, []);

  const handleSave = () => {
    onSave(keys);
  };

  const hasExistingKey = (provider) => existingProviders.includes(provider);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>API Configuration</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-content">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
          ) : (
            Object.entries(keys).map(([provider, key]) => (
              <div key={provider} className="form-group">
                <label className="form-label">
                  {provider.charAt(0).toUpperCase() + provider.slice(1)} API Key
                  {hasExistingKey(provider) && (
                    <span style={{ 
                      marginLeft: '10px', 
                      color: '#10b981', 
                      fontSize: '0.875rem',
                      fontWeight: 'normal'
                    }}>
                      ✓ API key already configured
                    </span>
                  )}
                </label>
                <input
                  type="password"
                  className="form-input"
                  value={key}
                  onChange={(e) => setKeys({ ...keys, [provider]: e.target.value })}
                  placeholder={
                    hasExistingKey(provider) 
                      ? `Leave empty to keep existing ${provider} key`
                      : `Enter your ${provider} API key`
                  }
                />
                {hasExistingKey(provider) && (
                  <small style={{ 
                    display: 'block', 
                    marginTop: '5px', 
                    color: '#9ca3af',
                    fontSize: '0.75rem'
                  }}>
                    Leave blank to keep your existing key, or enter a new one to replace it
                  </small>
                )}
              </div>
            ))
          )}
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
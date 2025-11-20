import React, { useState, useEffect } from 'react';
import { keyApi } from '../services/api';

const ApiKeyModal = ({ onSave, onClose }) => {
  const [keys, setKeys] = useState({
    openai: '',
    anthropic: '',
    gemini: '',
    mistral: ''
  });
  const [overrides, setOverrides] = useState({
    openai: false,
    anthropic: false,
    gemini: false,
    mistral: false
  });
  const [systemKeys, setSystemKeys] = useState({
    openai: false,
    anthropic: false,
    gemini: false,
    mistral: false
  });
  const [existingKeys, setExistingKeys] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch existing user keys and system key availability
    const fetchData = async () => {
      try {
        const [userKeysResponse, systemKeysResponse] = await Promise.all([
          keyApi.get(),
          keyApi.getSystemKeys()
        ]);
        
        // Set which providers user has configured
        const userKeyMap = {};
        const overrideMap = {};
        (userKeysResponse.data.keys || []).forEach(item => {
          userKeyMap[item.provider] = true;
          overrideMap[item.provider] = item.override_system_key || false;
        });
        setExistingKeys(Object.keys(userKeyMap));
        setOverrides(overrideMap);
        
        // Set which providers have system keys
        setSystemKeys(systemKeysResponse.data.system_keys || {});
      } catch (err) {
        console.error('Failed to fetch key data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleSave = () => {
    // Build payload with keys and override flags
    const payload = {};
    Object.entries(keys).forEach(([provider, key]) => {
      if (key.trim()) {
        payload[provider] = key;
        payload[`${provider}_override`] = overrides[provider];
      }
    });
    
    // Also include override flag updates even if key didn't change
    Object.entries(overrides).forEach(([provider, override]) => {
      if (existingKeys.includes(provider) && !payload[provider]) {
        // User has existing key but didn't enter new one, just update override flag
        payload[`${provider}_override`] = override;
      }
    });
    
    onSave(payload);
  };

  const hasExistingKey = (provider) => existingKeys.includes(provider);
  const hasSystemKey = (provider) => systemKeys[provider];

  const handleOverrideChange = (provider, checked) => {
    setOverrides({ ...overrides, [provider]: checked });
  };

  const getProviderLabel = (provider) => {
    const labels = {
      openai: 'OpenAI',
      anthropic: 'Anthropic (Claude)',
      gemini: 'Google Gemini',
      mistral: 'Mistral AI'
    };
    return labels[provider] || provider.charAt(0).toUpperCase() + provider.slice(1);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>API Key Configuration</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-content">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
          ) : (
            <>
              <div style={{ 
                marginBottom: '20px', 
                padding: '12px', 
                backgroundColor: '#f3f4f6', 
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#4b5563'
              }}>
                <strong>Note:</strong> System-wide keys are configured by your administrator. 
                You can override them with your own keys if needed.
              </div>
              
              {Object.entries(keys).map(([provider, key]) => (
                <div key={provider} className="form-group" style={{ marginBottom: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <label className="form-label" style={{ marginBottom: 0 }}>
                      {getProviderLabel(provider)}
                    </label>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '0.75rem' }}>
                      {hasSystemKey(provider) && (
                        <span style={{ color: '#10b981', fontWeight: '500' }}>
                          ✓ System key available
                        </span>
                      )}
                      {hasExistingKey(provider) && (
                        <span style={{ color: '#3b82f6', fontWeight: '500' }}>
                          ✓ Your key configured
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <input
                    type="password"
                    className="form-input"
                    value={key}
                    onChange={(e) => setKeys({ ...keys, [provider]: e.target.value })}
                    placeholder={
                      hasExistingKey(provider) 
                        ? `Leave empty to keep existing key`
                        : hasSystemKey(provider)
                        ? `Using system key (optional override)`
                        : `Enter your ${provider} API key`
                    }
                    style={{ marginBottom: '8px' }}
                  />
                  
                  {(hasSystemKey(provider) || hasExistingKey(provider)) && (
                    <label style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      fontSize: '0.875rem',
                      color: '#4b5563',
                      cursor: 'pointer',
                      userSelect: 'none'
                    }}>
                      <input
                        type="checkbox"
                        checked={overrides[provider]}
                        onChange={(e) => handleOverrideChange(provider, e.target.checked)}
                        disabled={!hasSystemKey(provider)}
                        style={{ cursor: hasSystemKey(provider) ? 'pointer' : 'not-allowed' }}
                      />
                      <span>
                        {hasSystemKey(provider) 
                          ? 'Override system key with my own key'
                          : 'No system key to override'}
                      </span>
                    </label>
                  )}
                  
                  {hasSystemKey(provider) && !overrides[provider] && (
                    <small style={{ 
                      display: 'block', 
                      marginTop: '6px', 
                      color: '#9ca3af',
                      fontSize: '0.75rem'
                    }}>
                      System key will be used by default
                    </small>
                  )}
                  
                  {hasSystemKey(provider) && overrides[provider] && (
                    <small style={{ 
                      display: 'block', 
                      marginTop: '6px', 
                      color: '#f59e0b',
                      fontSize: '0.75rem'
                    }}>
                      {hasExistingKey(provider) || key.trim()
                        ? 'Your key will override the system key'
                        : 'Enter a key above to override the system key'}
                    </small>
                  )}
                  
                  {!hasSystemKey(provider) && !hasExistingKey(provider) && (
                    <small style={{ 
                      display: 'block', 
                      marginTop: '6px', 
                      color: '#9ca3af',
                      fontSize: '0.75rem'
                    }}>
                      No system key configured - you must provide your own
                    </small>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave}>Save Configuration</button>
        </div>
      </div>
    </div>
  );
};

export default ApiKeyModal;
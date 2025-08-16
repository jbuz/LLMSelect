import React from 'react';

const Header = ({
  providers,
  models,
  selectedProvider,
  selectedModel,
  onProviderChange,
  onModelChange,
  onApiKeysClick,
  onClearChat
}) => {
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="logo">
          <span className="logo-icon">🤖</span>
          MultiChat
        </h1>
      </div>
      
      <div className="header-center">
        <select
          className="select-input"
          value={selectedProvider}
          onChange={(e) => onProviderChange(e.target.value)}
        >
          {providers.map(provider => (
            <option key={provider} value={provider}>
              {provider.charAt(0).toUpperCase() + provider.slice(1)}
            </option>
          ))}
        </select>
        
        <select
          className="select-input"
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
        >
          {models.map(model => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
      </div>
      
      <div className="header-right">
        <button className="btn btn-secondary" onClick={onClearChat}>
          Clear
        </button>
        <button className="btn btn-primary" onClick={onApiKeysClick}>
          API Keys
        </button>
      </div>
    </header>
  );
};

export default Header;
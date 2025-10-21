import React from 'react';

const Header = ({
  providers,
  models,
  selectedProvider,
  selectedModel,
  onProviderChange,
  onModelChange,
  onApiKeysClick,
  onClearChat,
  onLoginClick,
  onLogout,
  user
}) => {
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="logo">
          <span className="logo-icon">??</span>
          MultiChat
        </h1>
      </div>

      <div className="header-center">
        <select
          className="select-input"
          value={selectedProvider}
          onChange={(event) => onProviderChange(event.target.value)}
        >
          {providers.map((provider) => (
            <option key={provider} value={provider}>
              {provider.charAt(0).toUpperCase() + provider.slice(1)}
            </option>
          ))}
        </select>

        <select
          className="select-input"
          value={selectedModel}
          onChange={(event) => onModelChange(event.target.value)}
        >
          {models.map((model) => (
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
        <button className="btn btn-primary" onClick={onApiKeysClick} disabled={!user}>
          API Keys
        </button>
        {user ? (
          <button className="btn btn-ghost" onClick={onLogout}>
            Sign out ({user.username})
          </button>
        ) : (
          <button className="btn btn-ghost" onClick={onLoginClick}>
            Sign in
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;

import React, { useCallback, useEffect, useMemo, useState } from 'react';

import Header from './components/Header';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import ApiKeyModal from './components/ApiKeyModal';
import LoginModal from './components/LoginModal';
import ErrorBoundary from './components/ErrorBoundary';
import { authApi, chatApi, keyApi } from './services/api';

const PROVIDER_MODELS = {
  openai: [
    { id: 'gpt-4', name: 'GPT-4' },
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
  ],
  anthropic: [
    { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet' },
    { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus' },
    { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku' }
  ],
  gemini: [
    { id: 'gemini-pro', name: 'Gemini Pro' },
    { id: 'gemini-pro-vision', name: 'Gemini Pro Vision' }
  ],
  mistral: [
    { id: 'mistral-large-latest', name: 'Mistral Large' },
    { id: 'mistral-medium-latest', name: 'Mistral Medium' },
    { id: 'mistral-small-latest', name: 'Mistral Small' }
  ]
};

const STORAGE_KEY = 'chat-session';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isLoading, setIsLoading] = useState(false);
  const [showApiModal, setShowApiModal] = useState(false);
  const [user, setUser] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [globalError, setGlobalError] = useState('');

  const [authModal, setAuthModal] = useState({
    open: false,
    error: '',
    submitting: false
  });

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) {
      return;
    }

    try {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) {
        setMessages(parsed);
        setConversationId(null);
      } else if (parsed && typeof parsed === 'object') {
        setMessages(Array.isArray(parsed.messages) ? parsed.messages : []);
        setConversationId(parsed.conversationId ?? null);
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    const payload = JSON.stringify({ messages, conversationId });
    localStorage.setItem(STORAGE_KEY, payload);
  }, [messages, conversationId]);

  const bootstrapAuth = useCallback(async () => {
    try {
      const response = await authApi.me();
      setUser(response.data.user);
      setAuthModal((modal) => ({ ...modal, open: false, error: '' }));
    } catch {
      setUser(null);
      setAuthModal((modal) => ({ ...modal, open: true }));
    }
  }, []);

  useEffect(() => {
    bootstrapAuth();
  }, [bootstrapAuth]);

  const handleUnauthorized = useCallback((message = 'Your session has expired. Please sign in again.') => {
    setUser(null);
    setConversationId(null);
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    setAuthModal({ open: true, error: message, submitting: false });
  }, []);

  const sendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    const pendingMessages = [...messages, userMessage];
    setMessages(pendingMessages);
    setIsLoading(true);
    setGlobalError('');

    try {
      const response = await chatApi.sendMessage({
        provider: selectedProvider,
        model: selectedModel,
        messages: pendingMessages,
        conversationId
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response
      };
      const nextMessages = [...pendingMessages, assistantMessage];
      setMessages(nextMessages);
      if (response.data.conversationId) {
        setConversationId(response.data.conversationId);
      }
    } catch (error) {
      if (error.response?.status === 401) {
        handleUnauthorized();
        return;
      }
      const message =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'An unexpected error occurred';

      const assistantMessage = { role: 'assistant', content: message, isError: true };
      const nextMessages = [...pendingMessages, assistantMessage];
      setMessages(nextMessages);
      const conversationFromError = error.response?.data?.details?.conversationId || error.response?.data?.conversationId;
      if (conversationFromError) {
        setConversationId(conversationFromError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const saveApiKeys = async (keys) => {
    try {
      await keyApi.save(keys);
      setShowApiModal(false);
      setGlobalError('');
    } catch (error) {
      if (error.response?.status === 401) {
        handleUnauthorized();
        return;
      }
      setGlobalError(error.response?.data?.message || 'Unable to save API keys');
    }
  };

  const handleLogin = async (credentials) => {
    setAuthModal({ open: true, submitting: true, error: '' });
    try {
      const response = await authApi.login(credentials);
      setUser(response.data.user);
      setAuthModal({ open: false, submitting: false, error: '' });
      setGlobalError('');
    } catch (error) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Login failed';
      setAuthModal({ open: true, submitting: false, error: message });
    }
  };

  const handleRegister = async (payload) => {
    setAuthModal({ open: true, submitting: true, error: '' });
    try {
      await authApi.register(payload);
      await handleLogin({ username: payload.username, password: payload.password });
    } catch (error) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Registration failed';
      setAuthModal({ open: true, submitting: false, error: message });
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      // Nothing to do; logout is best-effort.
    } finally {
      setUser(null);
      setConversationId(null);
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY);
      setAuthModal({ open: true, error: '', submitting: false });
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const currentModels = useMemo(() => PROVIDER_MODELS[selectedProvider] || [], [selectedProvider]);

  return (
    <div className="app">
      <Header
        providers={Object.keys(PROVIDER_MODELS)}
        models={currentModels}
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onProviderChange={setSelectedProvider}
        onModelChange={setSelectedModel}
        onApiKeysClick={() => setShowApiModal(true)}
        onClearChat={clearChat}
        onLoginClick={() => setAuthModal((modal) => ({ ...modal, open: true }))}
        onLogout={handleLogout}
        user={user}
      />

      {globalError && <div className="global-error">{globalError}</div>}

      <ErrorBoundary onReset={clearChat}>
        <main className="main-content">
          <MessageList messages={messages} isLoading={isLoading} />
          <MessageInput onSendMessage={sendMessage} isLoading={isLoading || !user} />
        </main>
      </ErrorBoundary>

      {showApiModal && (
        <ApiKeyModal
          onSave={saveApiKeys}
          onClose={() => setShowApiModal(false)}
        />
      )}

      {authModal.open && (
        <LoginModal
          onLogin={handleLogin}
          onRegister={handleRegister}
          onClose={() => {
            if (user) {
              setAuthModal((modal) => ({ ...modal, open: false }));
            }
          }}
          error={authModal.error}
          isSubmitting={authModal.submitting}
        />
      )}
    </div>
  );
};

export default App;

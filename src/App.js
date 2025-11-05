import React, { useCallback, useEffect, useMemo, useState, Suspense, lazy, useRef } from 'react';

import Header from './components/Header';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import ErrorBoundary from './components/ErrorBoundary';
import LoginModal from './components/LoginModal';
import ToastContainer from './components/ToastContainer';
import { authApi, chatApi, keyApi } from './services/api';
import { useModels } from './hooks/useModels';
import { useStreamingChat } from './hooks/useStreamingChat';
import { useConversations } from './hooks/useConversations';
import { useToast } from './hooks/useToast';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

// Lazy load heavy components
const ComparisonMode = lazy(() => import('./components/ComparisonMode'));
const ComparisonHistory = lazy(() => import('./components/ComparisonHistory'));
const ConversationSidebar = lazy(() => import('./components/ConversationSidebar'));
const ApiKeyModal = lazy(() => import('./components/ApiKeyModal'));

const STORAGE_KEY = 'chat-session';

// Loading fallback component
const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    padding: '2rem',
    color: '#666'
  }}>
    Loading...
  </div>
);

const App = () => {
  const [mode, setMode] = useState('chat'); // 'chat', 'compare', or 'history'
  const messageInputRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [isLoading, setIsLoading] = useState(false);
  const [showApiModal, setShowApiModal] = useState(false);
  const [user, setUser] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [globalError, setGlobalError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const [authModal, setAuthModal] = useState({
    open: false,
    error: '',
    submitting: false
  });

  // Fetch models dynamically
  const { models: providerModels, loading: modelsLoading, error: modelsError } = useModels();

  // Streaming chat hook
  const {
    streamMessage,
    currentMessage,
    isStreaming,
    error: streamError,
    conversationId: streamConversationId,
    cancelStream
  } = useStreamingChat();

  // Conversations hook
  const {
    conversations,
    loading: conversationsLoading,
    error: conversationsError,
    fetchConversations,
    loadConversation,
    renameConversation,
    deleteConversation,
    exportConversation
  } = useConversations();

  // Toast notifications
  const { toasts, removeToast, success: showSuccess, error: showError, info: showInfo } = useToast();

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+k': () => {
      // Focus message input
      const input = document.querySelector('.message-input');
      if (input) input.focus();
    },
    'escape': () => {
      // Close modals
      if (showApiModal) setShowApiModal(false);
      if (authModal.open && user) setAuthModal(prev => ({ ...prev, open: false }));
    },
  });

  // When streaming completes, add the message to the list and refresh conversations
  useEffect(() => {
    if (!isStreaming && currentMessage && streamConversationId) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: currentMessage
      }]);
      setConversationId(streamConversationId);
      setActiveConversationId(streamConversationId);
      // Refresh conversations list to show updated conversation
      fetchConversations();
    }
  }, [isStreaming, currentMessage, streamConversationId, fetchConversations]);

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
    setMessages(prev => [...prev, userMessage]);
    setGlobalError('');

    await streamMessage({
      conversationId,
      message: content,
      provider: selectedProvider,
      model: selectedModel
    });
  };

  const saveApiKeys = async (keys) => {
    try {
      await keyApi.save(keys);
      setShowApiModal(false);
      setGlobalError('');
      showSuccess('API keys saved successfully!');
    } catch (error) {
      if (error.response?.status === 401) {
        handleUnauthorized();
        return;
      }
      const errorMsg = error.response?.data?.message || 'Unable to save API keys';
      setGlobalError(errorMsg);
      showError(errorMsg);
    }
  };

  const handleLogin = async (credentials) => {
    setAuthModal({ open: true, submitting: true, error: '' });
    try {
      const response = await authApi.login(credentials);
      setUser(response.data.user);
      setAuthModal({ open: false, submitting: false, error: '' });
      setGlobalError('');
      showSuccess(`Welcome back, ${response.data.user.username}!`);
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
      showSuccess('Registration successful!');
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
      showInfo('Logged out successfully');
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
    setActiveConversationId(null);
    localStorage.removeItem(STORAGE_KEY);
    showInfo('Chat cleared');
  };

  const handleSelectConversation = async (conversationId) => {
    const conversation = await loadConversation(conversationId);
    if (conversation) {
      setMessages(conversation.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })));
      setConversationId(conversationId);
      setActiveConversationId(conversationId);
      setSelectedProvider(conversation.provider);
      setSelectedModel(conversation.model);
      setMode('chat');
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setActiveConversationId(null);
    setMode('chat');
  };

  const handleLoadComparison = (comparison) => {
    // Switch to comparison mode and load the comparison
    setMode('compare');
    // The comparison will be loaded via ComparisonMode state
    // You could pass the comparison data as a prop if needed
  };

  const currentModels = useMemo(() => providerModels[selectedProvider] || [], [providerModels, selectedProvider]);
  const availableProviders = useMemo(() => Object.keys(providerModels), [providerModels]);

  return (
    <div className="app">
      <Header
        providers={availableProviders}
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
        mode={mode}
        onModeChange={setMode}
      />

      {globalError && <div className="global-error">{globalError}</div>}
      {modelsError && <div className="global-error">Failed to load models: {modelsError}</div>}
      {streamError && <div className="global-error">{streamError}</div>}
      {conversationsError && <div className="global-error">{conversationsError}</div>}

      <div className="app-layout">
        <Suspense fallback={<LoadingFallback />}>
          <ConversationSidebar
            conversations={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onRenameConversation={renameConversation}
            onDeleteConversation={deleteConversation}
            onExportConversation={exportConversation}
            onSearch={fetchConversations}
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
          />
        </Suspense>
        
        <ErrorBoundary onReset={clearChat}>
          <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
            {mode === 'chat' ? (
              <>
                <MessageList 
                  messages={messages} 
                  isLoading={isLoading} 
                  isStreaming={isStreaming}
                  currentMessage={currentMessage}
                />
                <MessageInput 
                  onSendMessage={sendMessage} 
                  isLoading={isStreaming || !user || modelsLoading}
                  onCancel={cancelStream}
                />
              </>
            ) : mode === 'compare' ? (
              <Suspense fallback={<LoadingFallback />}>
                <ComparisonMode chatApi={chatApi} providerModels={providerModels} />
              </Suspense>
            ) : mode === 'history' ? (
              <Suspense fallback={<LoadingFallback />}>
                <ComparisonHistory
                  onLoadComparison={handleLoadComparison}
                  onClose={() => setMode('compare')}
                />
              </Suspense>
            ) : null}
          </main>
        </ErrorBoundary>
      </div>

      {showApiModal && (
        <Suspense fallback={<LoadingFallback />}>
          <ApiKeyModal
            onSave={saveApiKeys}
            onClose={() => setShowApiModal(false)}
          />
        </Suspense>
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

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
};

export default App;

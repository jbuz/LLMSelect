import React, { Suspense, lazy } from 'react';
import Header from './Header';
import ErrorBoundary from './ErrorBoundary';
import LoginModal from './LoginModal';
import ApiKeyModal from './ApiKeyModal';
import ToastContainer from './ToastContainer';
import ConversationSidebar from './ConversationSidebar';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import { useChat } from '../contexts/ChatContext';
import { useModels } from '../hooks/useModels';
import { useConversations } from '../hooks/useConversations';
import { useToast } from '../hooks/useToast';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { keyApi, chatApi } from '../services/api';

// Lazy load pages
const ChatMode = lazy(() => import('../pages/ChatMode'));
const ComparisonMode = lazy(() => import('./ComparisonMode'));
const ComparisonHistory = lazy(() => import('./ComparisonHistory'));

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

const AppLayout = () => {
  const { user, login, register, logout, error: authError } = useAuth();
  const { 
    mode, 
    setMode,
    sidebarOpen, 
    toggleSidebar,
    selectedProvider,
    selectedModel,
    setSelectedProvider,
    setSelectedModel,
    showApiModal,
    openApiModal,
    closeApiModal
  } = useApp();
  const { clearChat, activeConversationId, loadConversationMessages } = useChat();
  const { models: providerModels, loading: modelsLoading, error: modelsError } = useModels();
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
  const { toasts, removeToast, success: showSuccess, error: showError, info: showInfo } = useToast();

  const [authModalOpen, setAuthModalOpen] = React.useState(!user);
  const [authModalSubmitting, setAuthModalSubmitting] = React.useState(false);
  const [authModalError, setAuthModalError] = React.useState('');

  // Show auth modal when user is not authenticated
  React.useEffect(() => {
    if (!user) {
      setAuthModalOpen(true);
    }
  }, [user]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+k': () => {
      const input = document.querySelector('.message-input');
      if (input) input.focus();
    },
    'escape': () => {
      if (showApiModal) closeApiModal();
      if (authModalOpen && user) setAuthModalOpen(false);
    },
  });

  const handleLogin = async (credentials) => {
    setAuthModalSubmitting(true);
    setAuthModalError('');
    const result = await login(credentials);
    if (result.success) {
      setAuthModalOpen(false);
      showSuccess(`Welcome back, ${result.user.username}!`);
    } else {
      setAuthModalError(result.error);
    }
    setAuthModalSubmitting(false);
  };

  const handleRegister = async (payload) => {
    setAuthModalSubmitting(true);
    setAuthModalError('');
    const result = await register(payload);
    if (result.success) {
      setAuthModalOpen(false);
      showSuccess('Registration successful!');
    } else {
      setAuthModalError(result.error);
    }
    setAuthModalSubmitting(false);
  };

  const handleLogout = async () => {
    await logout();
    clearChat();
    setAuthModalOpen(true);
    showInfo('Logged out successfully');
  };

  const handleClearChat = () => {
    clearChat();
    showInfo('Chat cleared');
  };

  const saveApiKeys = async (keys) => {
    try {
      await keyApi.save(keys);
      closeApiModal();
      showSuccess('API keys saved successfully!');
    } catch (error) {
      if (error.response?.status === 401) {
        handleLogout();
        return;
      }
      const errorMsg = error.response?.data?.message || 'Unable to save API keys';
      showError(errorMsg);
    }
  };

  const handleSelectConversation = async (conversationId) => {
    const conversation = await loadConversation(conversationId);
    if (conversation) {
      loadConversationMessages(conversation);
      setSelectedProvider(conversation.provider);
      setSelectedModel(conversation.model);
      setMode('chat');
    }
  };

  const handleNewConversation = () => {
    clearChat();
    setMode('chat');
  };

  const handleLoadComparison = () => {
    setMode('compare');
  };

  const currentModels = React.useMemo(
    () => providerModels[selectedProvider] || [], 
    [providerModels, selectedProvider]
  );
  const availableProviders = React.useMemo(
    () => Object.keys(providerModels), 
    [providerModels]
  );

  return (
    <div className="app">
      <Header
        providers={availableProviders}
        models={currentModels}
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onProviderChange={setSelectedProvider}
        onModelChange={setSelectedModel}
        onApiKeysClick={openApiModal}
        onClearChat={handleClearChat}
        onLoginClick={() => setAuthModalOpen(true)}
        onLogout={handleLogout}
        user={user}
        mode={mode}
        onModeChange={setMode}
      />

      {modelsError && <div className="global-error">Failed to load models: {modelsError}</div>}
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
            onToggle={toggleSidebar}
          />
        </Suspense>
        
        <ErrorBoundary onReset={handleClearChat}>
          <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
            <Suspense fallback={<LoadingFallback />}>
              {mode === 'chat' && <ChatMode />}
              {mode === 'compare' && <ComparisonMode chatApi={chatApi} providerModels={providerModels} />}
              {mode === 'history' && (
                <ComparisonHistory
                  onLoadComparison={handleLoadComparison}
                  onClose={() => setMode('compare')}
                />
              )}
            </Suspense>
          </main>
        </ErrorBoundary>
      </div>

      {showApiModal && (
        <Suspense fallback={<LoadingFallback />}>
          <ApiKeyModal
            onSave={saveApiKeys}
            onClose={closeApiModal}
          />
        </Suspense>
      )}

      {authModalOpen && (
        <LoginModal
          onLogin={handleLogin}
          onRegister={handleRegister}
          onClose={() => {
            if (user) {
              setAuthModalOpen(false);
            }
          }}
          error={authModalError}
          isSubmitting={authModalSubmitting}
        />
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
};

export default AppLayout;

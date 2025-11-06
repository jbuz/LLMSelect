import React, { createContext, useContext, useState, useCallback } from 'react';

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  const [mode, setMode] = useState('chat'); // 'chat', 'compare', or 'history'
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [showApiModal, setShowApiModal] = useState(false);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  const openApiModal = useCallback(() => {
    setShowApiModal(true);
  }, []);

  const closeApiModal = useCallback(() => {
    setShowApiModal(false);
  }, []);

  const switchToChat = useCallback(() => {
    setMode('chat');
  }, []);

  const switchToCompare = useCallback(() => {
    setMode('compare');
  }, []);

  const switchToHistory = useCallback(() => {
    setMode('history');
  }, []);

  const value = {
    // Mode state
    mode,
    setMode,
    switchToChat,
    switchToCompare,
    switchToHistory,
    
    // Sidebar state
    sidebarOpen,
    setSidebarOpen,
    toggleSidebar,
    
    // Model selection
    selectedProvider,
    selectedModel,
    setSelectedProvider,
    setSelectedModel,
    
    // Modals
    showApiModal,
    openApiModal,
    closeApiModal,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

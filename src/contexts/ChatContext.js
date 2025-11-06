import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'chat-session';

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [activeConversationId, setActiveConversationId] = useState(null);

  // Load saved session on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return;

    try {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) {
        setMessages(parsed);
        setConversationId(null);
      } else if (parsed && typeof parsed === 'object') {
        setMessages(Array.isArray(parsed.messages) ? parsed.messages : []);
        setConversationId(parsed.conversationId !== undefined ? parsed.conversationId : null);
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  // Save session to localStorage when it changes
  useEffect(() => {
    const payload = JSON.stringify({ messages, conversationId });
    localStorage.setItem(STORAGE_KEY, payload);
  }, [messages, conversationId]);

  const addMessage = useCallback((message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setActiveConversationId(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const loadConversationMessages = useCallback((conversation) => {
    setMessages(conversation.messages.map(msg => ({
      role: msg.role,
      content: msg.content
    })));
    setConversationId(conversation.id);
    setActiveConversationId(conversation.id);
  }, []);

  const value = {
    messages,
    setMessages,
    addMessage,
    conversationId,
    setConversationId,
    activeConversationId,
    setActiveConversationId,
    clearChat,
    loadConversationMessages,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

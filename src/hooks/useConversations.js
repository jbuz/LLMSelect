import { useState, useEffect, useCallback } from 'react';
import { conversationsApi } from '../services/api';

/**
 * Custom hook for managing conversation state and API interactions
 * @returns {Object} Hook state and methods
 */
export const useConversations = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  const fetchConversations = useCallback(async (searchQuery = '') => {
    try {
      setLoading(true);
      setError(null);
      
      const params = { page, limit: 20 };
      if (searchQuery) {
        params.search = searchQuery;
      }
      
      const response = await conversationsApi.list(params);
      const data = response.data;
      
      setConversations(data.conversations || []);
      setTotalPages(data.totalPages || 0);
    } catch (err) {
      // Don't show error for 401 (not authenticated) - this is expected on page load
      if (err.response?.status === 401) {
        console.log('Not authenticated - conversations will load after login');
        setConversations([]);
      } else {
        console.error('Failed to fetch conversations:', err);
        setError(err.response?.data?.message || 'Failed to load conversations');
        setConversations([]);
      }
    } finally {
      setLoading(false);
    }
  }, [page]);

  const loadConversation = useCallback(async (id) => {
    try {
      const response = await conversationsApi.get(id);
      return response.data;
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError(err.response?.data?.message || 'Failed to load conversation');
      return null;
    }
  }, []);

  const renameConversation = useCallback(async (id, newTitle) => {
    try {
      const response = await conversationsApi.update(id, { title: newTitle });
      // Update local state
      setConversations(prev => 
        prev.map(conv => 
          conv.id === id ? { ...conv, title: newTitle } : conv
        )
      );
      return response.data;
    } catch (err) {
      console.error('Failed to rename conversation:', err);
      setError(err.response?.data?.message || 'Failed to rename conversation');
      return null;
    }
  }, []);

  const deleteConversation = useCallback(async (id) => {
    // Show confirmation dialog
    if (!window.confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      return false;
    }

    try {
      await conversationsApi.delete(id);
      // Remove from local state
      setConversations(prev => prev.filter(conv => conv.id !== id));
      return true;
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError(err.response?.data?.message || 'Failed to delete conversation');
      return false;
    }
  }, []);

  const exportConversation = useCallback(async (id, format = 'markdown') => {
    try {
      const response = await conversationsApi.export(id, format);
      
      if (format === 'markdown') {
        // Create blob and trigger download
        const blob = new Blob([response.data], { type: 'text/markdown' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation-${id}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        // JSON format - create and download
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { 
          type: 'application/json' 
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation-${id}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
      
      return true;
    } catch (err) {
      console.error('Failed to export conversation:', err);
      setError(err.response?.data?.message || 'Failed to export conversation');
      return false;
    }
  }, []);

  // Fetch conversations on mount and when page changes
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  return {
    conversations,
    loading,
    error,
    page,
    totalPages,
    fetchConversations,
    loadConversation,
    renameConversation,
    deleteConversation,
    exportConversation,
    setPage,
  };
};

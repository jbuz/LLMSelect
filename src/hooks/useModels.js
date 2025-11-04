import { useState, useEffect, useCallback } from 'react';
import http from '../services/http';

/**
 * Custom hook for fetching and managing LLM models from the API
 * @param {string} provider - Optional provider filter (openai, anthropic, gemini, mistral)
 * @returns {Object} Hook state and methods
 */
export const useModels = (provider = null) => {
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchModels = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = provider ? { provider } : {};
      const response = await http.get('/models', { params });
      
      // Group models by provider
      const groupedModels = {};
      response.data.models.forEach(model => {
        if (!groupedModels[model.provider]) {
          groupedModels[model.provider] = [];
        }
        groupedModels[model.provider].push(model);
      });
      
      setModels(groupedModels);
    } catch (err) {
      // Don't show error for 401 (not authenticated) - this is expected on page load
      if (err.response?.status === 401) {
        console.log('Not authenticated - models will load after login');
        setModels({});
      } else {
        console.error('Failed to fetch models:', err);
        setError(err.response?.data?.message || 'Failed to fetch models');
        setModels({});
      }
    } finally {
      setLoading(false);
    }
  }, [provider]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  return {
    models,
    loading,
    error,
    refetch: fetchModels,
  };
};

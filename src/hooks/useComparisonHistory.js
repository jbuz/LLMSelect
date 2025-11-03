import { useState, useEffect, useCallback } from 'react';
import { chatApi } from '../services/api';

/**
 * Custom hook for fetching and managing comparison history
 * @returns {Object} Hook state and methods
 */
export const useComparisonHistory = () => {
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(false);

  const fetchComparisons = useCallback(async (offset = 0, limit = 20) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await chatApi.getComparisons({ offset, limit });
      const data = response.data;
      
      setComparisons(data.comparisons);
      setHasMore(data.comparisons.length >= limit);
    } catch (err) {
      console.error('Failed to fetch comparison history:', err);
      setError(err.response?.data?.message || 'Failed to load comparison history');
      setComparisons([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteComparison = useCallback(async (comparisonId) => {
    try {
      await chatApi.deleteComparison(comparisonId);
      // Remove from local state
      setComparisons(prev => prev.filter(c => c.id !== comparisonId));
      return true;
    } catch (err) {
      console.error('Failed to delete comparison:', err);
      setError(err.response?.data?.message || 'Failed to delete comparison');
      return false;
    }
  }, []);

  useEffect(() => {
    fetchComparisons();
  }, [fetchComparisons]);

  return {
    comparisons,
    loading,
    error,
    hasMore,
    refetch: fetchComparisons,
    deleteComparison,
  };
};

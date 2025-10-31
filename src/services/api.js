import http from './http';

export const authApi = {
  register: (data) => http.post('/auth/register', data),
  login: (data) => http.post('/auth/login', data),
  logout: () => http.post('/auth/logout'),
  me: () => http.get('/auth/me'),
  refresh: () => http.post('/auth/refresh')
};

export const chatApi = {
  sendMessage: (data) => http.post('/chat', data),
  compare: (data) => http.post('/compare', data),
  voteComparison: (comparisonId, preferredIndex) => 
    http.post(`/comparisons/${comparisonId}/vote`, { preferred_index: preferredIndex }),
  getComparisons: (params) => http.get('/comparisons', { params })
};

export const keyApi = {
  save: (keys) => http.post('/keys', keys)
};

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
  getComparisons: (params) => http.get('/comparisons', { params }),
  deleteComparison: (comparisonId) => http.delete(`/comparisons/${comparisonId}`)
};

export const keyApi = {
  get: () => http.get('/keys'),
  save: (keys) => http.post('/keys', keys),
  getSystemKeys: () => http.get('/keys/system-keys')
};

export const conversationsApi = {
  list: (params) => http.get('/conversations', { params }),
  get: (id) => http.get(`/conversations/${id}`),
  update: (id, data) => http.patch(`/conversations/${id}`, data),
  delete: (id) => http.delete(`/conversations/${id}`),
  export: (id, format = 'markdown') => http.get(`/conversations/${id}/export`, { 
    params: { format },
    responseType: format === 'markdown' ? 'blob' : 'json'
  })
};
